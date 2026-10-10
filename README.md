<div align="center">

# ⚡ Sortiq

**Intelligent, Offline-Safe Desktop File Management & Deduplication**

![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![Native Windows](https://img.shields.io/badge/OS-Windows-lightgrey)
![MIT License](https://img.shields.io/badge/License-MIT-green)
![SQLite Storage](https://img.shields.io/badge/Storage-SQLite-white)
![No Telemetry](https://img.shields.io/badge/Telemetry-Zero-red)

<br>

<p align="center">
  <img src="./Screenshot/sortiq.png" alt="Sortiq Interface" width="850">
</p>

<br>

[ Python ] [ React 19 ] [ TypeScript ] [ Tailwind CSS ] [ SQLite ]

</div>

---

Sortiq is an intelligent, secure, offline-first local file management and deduplication utility built for developer machines. It is designed to tame file chaos on massive local drives without requiring external servers, cloud connectivity, or intrusive background processes.

## 🛡️ Security & Zero-Risk Architecture
*   **PathGuard**: Hardcoded blacklists guarding critical system drives (`C:\Windows`, `Program Files`, `System32`, AppData root) to prevent accidental system interference.
*   **Recycle Bin Integration**: All deletions route through Windows `send2trash`, ensuring non-destructive cleanup.
*   **WAL Rollback**: Built-in Write-Ahead Logging allows for safe, 1-click rollback of organizational operations.

## ⚡ High-Speed Smart Engine
*   **Two-Phase Smart Hash**: Phase 1 crawls metadata efficiently, Phase 2 computes SHA-256 *only* for files matching identical size clusters, eliminating unnecessary I/O.
*   **Pruned Crawling**: Automatically ignores dev bloat (`node_modules`, `.git`, `venv`, `.next`, etc.) and safely skips broken junctions to prevent filesystem hangs.

## 🚀 Quick Start
### Local Setup
```bash
# Clone the repository
git clone https://github.com/Aby020/sortiq.git
cd sortiq

# Set up environment
uv sync
```

### Modes of Operation
*   **Interactive CLI**: `uv run python sortiq_cli.py`
*   **Standalone GUI**: Build via `uv run pyinstaller sortiq.spec --noconfirm`

## 📦 Standalone Packaging
Sortiq can be packaged as a standalone portable Windows executable using PyInstaller, functioning without browser coupling or network socket dependencies, maintaining complete offline integrity.

## 📄 License
Distributed under the MIT License. See `LICENSE` for details.
