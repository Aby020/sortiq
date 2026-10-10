# Sortiq

![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![Native Windows](https://img.shields.io/badge/OS-Windows-lightgrey)
![MIT License](https://img.shields.io/badge/License-MIT-green)
![SQLite Storage](https://img.shields.io/badge/Storage-SQLite-white)
![No Telemetry](https://img.shields.io/badge/Telemetry-Zero-red)

Sortiq is an intelligent, secure, offline-first local file management and deduplication utility built for developer machines. It is designed to tame file chaos on massive local drives without requiring external servers, cloud connectivity, or intrusive background processes.

By leveraging a high-performance, in-process Python scanner and a local SQLite database, Sortiq provides actionable insights into your storage layout, identifies duplicate structures with precision, and facilitates safe, non-destructive file cleanup operations directly from your terminal or desktop.

## Key Features

*   **⚡ High-Speed Two-Phase Scanner**: Optimized to crawl massive local file trees while ignoring dev bloat (`node_modules`, `.git`, `venv`, `.next`, etc.) and safely auto-pruning broken junction points. It uses a metadata-first approach and computes SHA-256 hashes *only* for files with identical sizes, slashing scanning time.
*   **🛡️ PathGuard System Protection**: Features robust, hardcoded safety blacklists guarding critical Windows directories (`C:\Windows`, `System32`, `Program Files`, AppData roots) to ensure operations never compromise system integrity.
*   **♻️ Non-Destructive Cleanup**: Integrated with `send2trash` for Windows Recycle Bin routing and a Write-Ahead Log (WAL) system to ensure safe, undoable operations and immediate 1-click rollbacks.
*   **💻 Modern Interactive TUI**: A native terminal interface powered by `rich`, featuring a styled, branded menu, live progress tracking, and intuitive dashboards for duplicate inspection.
*   **🖥️ Optional Standalone Desktop GUI**: Fully packagable as a standalone Windows `.exe` using PyInstaller, functioning without browser coupling or network socket dependencies.

## Visual Demo

| Interactive Terminal Menu | Fast Scan Summary |
| :---: | :---: |
| ![Terminal Menu](docs/assets/cli_menu.png) | ![Scan Summary](docs/assets/cli_scan_summary.png) |

*(Screenshots placeholder: Replace with your actual project screenshots.)*

## Quick Start / Installation

### Prerequisites
*   Windows 10/11
*   Python 3.10+
*   `uv` or `pip`

### Local Setup
```bash
# Clone the repository
git clone https://github.com/Aby020/sortiq.git
cd sortiq

# Set up environment
uv venv
uv pip install -r requirements.txt
```

### Launching the Interactive Terminal
```bash
uv run python sortiq_cli.py
```

### Building Standalone Windows Executable
```bash
uv run pyinstaller sortiq.spec --noconfirm
```

## Architecture & Local Storage
Sortiq follows a zero-server, in-process architecture. When running, the scanner interacts directly with the filesystem and manages cataloging locally at `%LOCALAPPDATA%\Sortiq\sortiq.db`. There is no background HTTP daemon, no Redis dependency, and zero telemetry data ever leaves your machine.

## Safety & Guardrails
All potentially destructive actions route through the Windows Recycle Bin. For operations outside the Recycle Bin capability, Sortiq maintains a local `.sortiq_quarantine` directory and journaling system, ensuring that permanent deletion is never performed by default.

## License
Distributed under the MIT License. See `LICENSE` for details.
