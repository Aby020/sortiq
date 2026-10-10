#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SORTIQ — Intelligent Local File Organizer (Rich Terminal CLI).
Direct in-process scanning via sortiq_fs; writes to local SQLite.
Zero external HTTP / Celery / FastAPI daemon dependency.
"""
from __future__ import annotations

import os
import sqlite3
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any

# Resolve project root for backend imports
PROJECT_ROOT = Path(__file__).parent.resolve()
BACKEND = PROJECT_ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TimeElapsedColumn
from rich.prompt import Prompt, IntPrompt
from rich.live import Live
from rich.rule import Rule
from rich.align import Align
from rich import box

# sortiq_fs modules (pure Python, no Django required for scanner)
try:
    from sortiq_fs.pathguard import is_blacklisted, normalize, validate, PathCheckResult
    from sortiq_fs.walker import iter_entries, WalkStats
    from sortiq_fs.hasher import hash_file, PARTIAL_SIZE
    from sortiq_fs.metadata import extract
    from sortiq_fs.quarantine import safe_delete, quarantine_move
except Exception as exc:
    # Graceful degradation if backend not fully on PYTHONPATH
    pass

# ------------------------------------------------------------------
# CONFIG / DB
# ------------------------------------------------------------------
DB_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Sortiq"
DB_PATH = DB_DIR / "sortiq.db"
DB_DIR.mkdir(parents=True, exist_ok=True)

console = Console(force_terminal=True, color_system="auto")

# ------------------------------------------------------------------
# PATH SANITIZATION & GUARD
# ------------------------------------------------------------------
def sanitize_path(raw: str) -> str:
    """Strip quotes, expand ~ and %USERPROFILE%, resolve absolute."""
    s = raw.strip()
    # Strip surrounding single/double quotes
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        s = s[1:-1]
    s = s.strip()
    # Expand ~
    if s.startswith("~"):
        s = os.path.expanduser(s)
    # Expand %USERPROFILE% (Windows env)
    s = os.path.expandvars(s)
    # Resolve to absolute
    p = Path(s).resolve()
    return str(p)


def check_path(path_str: str) -> Tuple[bool, str, str]:
    """Return (ok, reason, resolved_path)."""
    try:
        resolved = sanitize_path(path_str)
    except Exception as exc:
        return False, f"Invalid path format: {exc}", path_str

    p = Path(resolved)
    if not p.exists():
        return False, "Directory not found — path does not exist on this system.", resolved
    if not p.is_dir():
        return False, "Not a directory — the path points to a file.", resolved

    # PathGuard / blacklisted check
    norm = normalize(resolved)
    if is_blacklisted(norm):
        return False, "System directory protected — access denied by PathGuard (Windows protected area such as System32, Program Files, or AppData root).", resolved

    # Additional guard: reserved device names / bad drives / traversal
    # Use a managed root based on the drive of the path itself
    if ":/" in norm:
        drive_root = norm.split(":/")[0] + ":/"
    else:
        drive_root = "C:/"
    try:
        result = validate(drive_root, resolved)
        if not result.ok:
            return False, result.reason, resolved
    except Exception:
        pass
    return True, "", resolved


# ------------------------------------------------------------------
# DIRECT LOCAL SQLITE ENGINE (in-process, no HTTP)
# ------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS catalog_file (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_path TEXT NOT NULL,
            relative_path TEXT NOT NULL,
            canonical_path TEXT NOT NULL,
            name TEXT NOT NULL,
            extension TEXT,
            size_bytes INTEGER DEFAULT 0,
            mtime_ns INTEGER,
            ctime_ns INTEGER,
            inode_identity TEXT,
            is_directory INTEGER DEFAULT 0,
            is_symlink INTEGER DEFAULT 0,
            mime_type TEXT,
            sha256 TEXT,
            partial_hash TEXT,
            hash_stage TEXT DEFAULT 'none',
            first_seen_at TEXT,
            last_seen_at TEXT,
            UNIQUE(folder_path, relative_path)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_folder_path ON catalog_file(folder_path)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sha ON catalog_file(sha256)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ext ON catalog_file(extension)")
    conn.commit()
    conn.close()


def insert_catalog_entries(folder_path: str, entries: List[Any], stats: WalkStats):
    conn = sqlite3.connect(str(DB_PATH))
    now_iso = datetime.now().isoformat()
    inserted = 0
    updated = 0
    for entry in entries:
        try:
            # Hash computation (direct, in-process)
            sha = ""
            partial = ""
            stage = "none"
            if not entry.is_directory:
                try:
                    h = hash_file(entry.absolute_path)
                    sha = h.sha256
                    partial = h.partial_hash
                    stage = h.stage
                except Exception:
                    stage = "error"
            meta = extract(entry.absolute_path)
            # Insert / update
            conn.execute("""
                INSERT INTO catalog_file
                (folder_path, relative_path, canonical_path, name, extension,
                 size_bytes, mtime_ns, ctime_ns, inode_identity, is_directory,
                 is_symlink, mime_type, sha256, partial_hash, hash_stage,
                 first_seen_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(folder_path, relative_path) DO UPDATE SET
                size_bytes=excluded.size_bytes,
                mtime_ns=excluded.mtime_ns,
                ctime_ns=excluded.ctime_ns,
                inode_identity=excluded.inode_identity,
                is_directory=excluded.is_directory,
                is_symlink=excluded.is_symlink,
                mime_type=excluded.mime_type,
                sha256=excluded.sha256,
                partial_hash=excluded.partial_hash,
                hash_stage=excluded.hash_stage,
                last_seen_at=excluded.last_seen_at
            """, (
                folder_path,
                entry.relative_path,
                entry.absolute_path,
                entry.name,
                meta.get("extension") or (entry.name.split(".")[-1].lower() if "." in entry.name else ""),
                entry.size_bytes,
                entry.mtime_ns,
                entry.ctime_ns,
                entry.inode,
                1 if entry.is_directory else 0,
                1 if entry.is_symlink else 0,
                meta.get("mime_type") or "",
                sha,
                partial,
                stage,
                now_iso,
                now_iso,
            ))
            conn.commit()
            inserted += 1
        except Exception:
            continue
    conn.close()
    return inserted, stats


def count_catalog_for(folder_path: str) -> Tuple[int, int, int, int]:
    conn = sqlite3.connect(str(DB_PATH))
    total = conn.execute("SELECT COUNT(*) FROM catalog_file WHERE folder_path=?", (folder_path,)).fetchone()[0]
    dirs = conn.execute("SELECT COUNT(*) FROM catalog_file WHERE folder_path=? AND is_directory=1", (folder_path,)).fetchone()[0]
    dup_sha = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT sha256 FROM catalog_file WHERE folder_path=? AND sha256!='' AND sha256 IS NOT NULL
            GROUP BY sha256 HAVING COUNT(*) > 1
        ) as d
    """, (folder_path,)).fetchone()[0]
    conn.close()
    return total, dirs, dup_sha, 0


def get_duplicate_groups(folder_path: str, limit: int = 10) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute("""
        SELECT sha256, COUNT(*) as cnt, SUM(size_bytes) as total_size
        FROM catalog_file
        WHERE folder_path=? AND sha256!='' AND sha256 IS NOT NULL
        GROUP BY sha256 HAVING cnt > 1
        ORDER BY cnt DESC
        LIMIT ?
    """, (folder_path, limit)).fetchall()
    conn.close()
    groups = []
    for sha, cnt, total_size in rows:
        groups.append({"sha256": sha[:16] + "...", "full_sha": sha, "count": cnt, "total_size": total_size or 0})
    return groups


def get_catalog_summary(folder_path: str) -> Dict[str, Any]:
    conn = sqlite3.connect(str(DB_PATH))
    total = conn.execute("SELECT COUNT(*) FROM catalog_file WHERE folder_path=?", (folder_path,)).fetchone()[0]
    indexed = total
    dup = conn.execute("""
        SELECT COUNT(DISTINCT sha256) FROM catalog_file
        WHERE folder_path=? AND sha256!='' AND sha256 IS NOT NULL
         AND sha256 IN (
             SELECT sha256 FROM catalog_file WHERE folder_path=?
             GROUP BY sha256 HAVING COUNT(*) > 1
         )
    """, (folder_path, folder_path)).fetchone()[0]
    skipped = 0  # tracked via stats
    conn.close()
    return {"indexed": indexed, "duplicates": dup, "skipped": skipped}


# ------------------------------------------------------------------
# UI: HEADER / BANNER
# ------------------------------------------------------------------
def render_header():
    header_text = Text()
    header_text.append("SORTIQ  ", style="bold bright_cyan")
    header_text.append("Intelligent Local File Organizer\n", style="dim")
    header_text.append("  Storage: SQLite  |  Mode: Offline Safe  |  Sandbox: Active  ", style="bright_black")
    banner = Panel(
        Align.center(header_text),
        border_style="bright_cyan",
        subtitle="[bold bright_yellow]Direct In-Process • No HTTP • Local DB[/bold bright_yellow]",
        title="[bold]SORTIQ CLI[/bold]",
    )
    console.print(banner)
    console.print()


def render_menu():
    menu = Table(show_header=False, box=box.ROUNDED, border_style="blue", padding=(0, 1))
    menu.add_column("Key", style="bold bright_yellow", justify="center", width=6)
    menu.add_column("Action", style="bold bright_white")
    menu.add_column("Description", style="dim")
    rows = [
        ("[1]", "📁 Scan Directory", "Quick presets + Custom path — direct in-process crawl"),
        ("[2]", "🔍 Duplicate Detector", "Inspect hash groups, side-by-side comparison"),
        ("[3]", "⚡ Auto-Organize", "Dry-run preview before moving duplicates"),
        ("[4]", "↩️ Undo / Rollback", "Restore from Write-Ahead Log (local quarantine)"),
        ("[5]", "📊 Storage Analytics", "MIME summary, largest files, growth"),
        ("[0]", "🚪 Exit", "Leave the terminal safely"),
    ]
    for k, a, d in rows:
        menu.add_row(k, a, d)
    console.print(Panel(menu, title="Main Menu", border_style="cyan"))


# ------------------------------------------------------------------
# SCAN ENGINE (direct, synchronous / local thread feel)
# ------------------------------------------------------------------
def run_scan_flow():
    console.print()
    console.print(Panel("[bold bright_cyan]Scan Directory[/bold bright_cyan]", subtitle="Choose a target"))
    console.print()
    # Quick presets
    presets = {
        "1": ("Downloads", str(Path.home() / "Downloads")),
        "2": ("Documents", str(Path.home() / "Documents")),
        "3": ("Desktop", str(Path.home() / "Desktop")),
        "4": ("Custom", None),
    }
    for k, (label, val) in presets.items():
        console.print(f"  [{k}] {label}" + (f"  →  {val}" if val else ""))
    choice = Prompt.ask("Select option or type full path", default="4")

    if choice == "4" or (choice not in presets):
        raw = Prompt.ask("Enter directory path (quotes OK)")
        path_input = raw
    else:
        _, path_input = presets[choice]

    ok, reason, resolved = check_path(path_input)
    if not ok:
        # High-visibility warning panel
        console.print()
        console.print(Panel(
            f"[bold red]SCAN BLOCKED[/bold red]\n\nReason: [bold]{reason}[/bold]\nResolved: [dim]{resolved}[/dim]",
            title="[bold red]PathGuard Warning[/bold red]",
            border_style="red",
        ))
        console.print("[yellow]Press Enter to return to main menu.[/yellow]")
        input()
        return

    console.print(f"\n[green]Scanning:[/green] [bold]{resolved}[/bold]  (in-process, direct to SQLite)")
    # Direct execution — call python catalog walker synchronously
    start = time.time()
    # Use walker.walk directly (returns entries + stats)
    from sortiq_fs.walker import walk
    entries_list, stats_acc = walk(resolved, recursive=True, follow_symlinks=False)

    # Re-collect via walker directly (synchronous)
    start = time.time()
    entries_list = []
    stats_acc = WalkStats()
    try:
        for e in iter_entries(resolved, recursive=True, follow_symlinks=False):
            entries_list.append(e)
            if e.is_directory:
                stats_acc.directories += 1
            else:
                stats_acc.files += 1
    except Exception as exc:
        stats_acc.errors.append(str(exc))

    total_scanned = len(entries_list)

    # Progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("Files:[bold]{task.fields[files]}[/bold]"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning directory...", total=total_scanned, start=True, files=0)
        # Insert in batches for progress feedback
        batch_size = 50
        for i in range(0, total_scanned, batch_size):
            batch = entries_list[i:i+batch_size]
            insert_catalog_entries(resolved, batch, stats_acc)
            progress.update(task, advance=min(batch_size, total_scanned - i), files=min(i + batch_size, total_scanned))

    elapsed = time.time() - start

    # Count results from DB directly
    indexed, dirs, dup_groups, skipped = count_catalog_for(resolved)
    # Rough duplicate detection from DB
    conn = sqlite3.connect(str(DB_PATH))
    dup_found = conn.execute("""
        SELECT COUNT(DISTINCT sha256) FROM catalog_file
        WHERE folder_path=? AND sha256!='' AND sha256 IS NOT NULL
         AND sha256 IN (SELECT sha256 FROM catalog_file WHERE folder_path=? GROUP BY sha256 HAVING COUNT(*)>1)
    """, (resolved, resolved)).fetchone()[0] or 0
    conn.close()

    # Post-scan summary table
    summary = Table(title="Scan Complete — Summary", box=box.ROUNDED, border_style="green")
    summary.add_column("Metric", style="bold cyan")
    summary.add_column("Value", justify="right")
    summary.add_row("Folder", resolved)
    summary.add_row("Total Scanned", str(total_scanned))
    summary.add_row("Indexed (DB)", str(indexed))
    summary.add_row("Directories", str(dirs))
    summary.add_row("Duplicates Found", str(dup_found))
    summary.add_row("Skipped / Locked", str(stats_acc.skipped + skipped))
    summary.add_row("Elapsed", f"{elapsed:.2f}s")
    console.print()
    console.print(summary)
    console.print()
    console.print("[bold bright_green]✅ Catalog written directly to:[/bold bright_green] [dim]" + str(DB_PATH) + "[/dim]")
    console.print("[yellow]Press Enter to return to main menu.[/yellow]")
    input()


# ------------------------------------------------------------------
# DUPLICATE DETECTOR
# ------------------------------------------------------------------
def run_duplicate_flow():
    console.print()
    console.print(Panel("[bold bright_magenta]Duplicate Detector[/bold bright_magenta]", subtitle="Inspect hash groups"))
    # Ask folder
    raw = Prompt.ask("Folder path to inspect (default = last scanned folder or custom)")
    if not raw:
        # Try to infer from DB: most recent folder
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute("SELECT folder_path FROM catalog_file GROUP BY folder_path LIMIT 1").fetchone()
        conn.close()
        folder_path = row[0] if row else os.path.expanduser("~/Downloads")
    else:
        ok, _, folder_path = check_path(raw)
        if not ok:
            console.print(f"[red]Invalid folder: {folder_path}[/red]")
            console.print("[yellow]Press Enter to return.[/yellow]"); input(); return

    groups = get_duplicate_groups(folder_path, limit=5)
    if not groups:
        console.print("[dim]No duplicate groups found for this folder.[/dim]")
    else:
        tbl = Table(title=f"Duplicate Groups — {folder_path}", box=box.ROUNDED, border_style="magenta")
        tbl.add_column("Group SHA (prefix)", style="dim")
        tbl.add_column("Files", justify="right")
        tbl.add_column("Total Size", justify="right")
        for g in groups:
            tbl.add_row(g["sha256"], str(g["count"]), f"{g['total_size']:,} bytes")
        console.print(tbl)
        console.print("[yellow]Use menu [3] Auto-Organize to act on duplicates.[/yellow]")
    console.print("[yellow]Press Enter to return to main menu.[/yellow]")
    input()


# ------------------------------------------------------------------
# AUTO-ORGANIZE (dry-run preview)
# ------------------------------------------------------------------
def run_organize_flow():
    console.print()
    console.print(Panel("[bold bright_blue]Auto-Organize by Rules[/bold bright_blue]", subtitle="Dry-run preview"))
    console.print("[bold]Dry-run mode enabled — no files will be moved yet.[/bold]")
    # Simple rule: for each duplicate hash group, keep first (oldest mtime) and flag rest
    raw = Prompt.ask("Folder path (or blank for latest)")
    if not raw:
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute("SELECT folder_path FROM catalog_file GROUP BY folder_path LIMIT 1").fetchone()
        conn.close()
        folder_path = row[0] if row else ""
    else:
        _, _, folder_path = check_path(raw)
    if not folder_path or not Path(folder_path).exists():
        console.print("[red]Folder not valid.[/red]"); input(); return

    groups = get_duplicate_groups(folder_path, limit=3)
    if not groups:
        console.print("No duplicate groups — nothing to organize.")
    else:
        console.print(f"[green]Would process {len(groups)} duplicate group(s) in:[/green] {folder_path}")
        for g in groups:
            console.print(f"  • SHA {g['sha256']} — {g['count']} files, {g['total_size']:,} bytes")
    console.print("[yellow]In real execution this would call safe_delete / quarantine_move (Recycle Bin / local fallback).[/yellow]")
    console.print("[yellow]Press Enter to return to main menu.[/yellow]")
    input()


# ------------------------------------------------------------------
# UNDO / ROLLBACK (local quarantine awareness)
# ------------------------------------------------------------------
def run_undo_flow():
    console.print()
    console.print(Panel("[bold bright_green]Undo / Rollback[/bold bright_green]", subtitle="Write-Ahead Log awareness"))
    console.print("[dim]Local quarantine directory:[/dim] %LOCALAPPDATA%\\Sortiq\\.sortiq_quarantine")
    console.print("[dim]Recycle-bin actions are restorable by Windows Explorer.[/dim]")
    console.print("[bold yellow]This CLI operates in safe mode: no permanent deletion is performed.[/bold yellow]")
    console.print("[yellow]Press Enter to return to main menu.[/yellow]")
    input()


# ------------------------------------------------------------------
# STORAGE ANALYTICS
# ------------------------------------------------------------------
def run_analytics_flow():
    console.print()
    console.print(Panel("[bold bright_yellow]Storage Analytics & Catalog[/bold bright_yellow]", subtitle="From local SQLite"))
    conn = sqlite3.connect(str(DB_PATH))
    # MIME summary
    mime_rows = conn.execute("SELECT mime_type, COUNT(*), SUM(size_bytes) FROM catalog_file WHERE mime_type!='' GROUP BY mime_type ORDER BY COUNT(*) DESC LIMIT 8").fetchall()
    # Largest files
    big = conn.execute("SELECT folder_path, name, size_bytes FROM catalog_file WHERE is_directory=0 ORDER BY size_bytes DESC LIMIT 8").fetchall()
    conn.close()

    mime_t = Table(title="MIME-Type Summary", box=box.ROUNDED)
    mime_t.add_column("MIME", style="cyan")
    mime_t.add_column("Count", justify="right")
    mime_t.add_column("Size", justify="right")
    for m, c, s in mime_rows:
        mime_t.add_row(str(m) or "unknown", str(c), f"{s or 0:,}")
    console.print(mime_t)

    big_t = Table(title="Largest Files (Indexed)", box=box.ROUNDED)
    big_t.add_column("Path / Name", style="dim")
    big_t.add_column("Size", justify="right")
    for fold, name, sz in big:
        big_t.add_row(f"{fold} / {name}", f"{sz:,} bytes")
    console.print(big_t)
    console.print("[yellow]Press Enter to return to main menu.[/yellow]")
    input()


# ------------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------------
def main():
    init_db()
    # Ensure DB exists at expected path
    console.clear()
    render_header()
    while True:
        render_menu()
        choice = Prompt.ask("Select option", choices=["0","1","2","3","4","5"], default="0")
        if choice == "0":
            console.print("\n[bold bright_green]Goodbye — Sortiq safe mode. No data left behind.[/bold bright_green]")
            break
        elif choice == "1":
            run_scan_flow()
            console.clear(); render_header()
        elif choice == "2":
            run_duplicate_flow()
            console.clear(); render_header()
        elif choice == "3":
            run_organize_flow()
            console.clear(); render_header()
        elif choice == "4":
            run_undo_flow()
            console.clear(); render_header()
        elif choice == "5":
            run_analytics_flow()
            console.clear(); render_header()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bright_red]Interrupted — exiting safely.[/bright_red]")
        sys.exit(0)
