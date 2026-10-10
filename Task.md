Overhaul Sortiq frontend architecture: fix 401 Unauthorized blocking all API requests, and rebuild the UI/UX into a modern, fluid desktop application interface.

CRITICAL BUGS TO FIX:
1. 401 Unauthorized on all /api/v1/* requests:
   - Inspect backend auth requirements in Django (REST_FRAMEWORK settings, permission_classes, and JWT / Session auth).
   - In `frontend/src/lib/api.ts`, configure authentication headers. If JWT/Token authentication is enabled, implement an automatic session/auth interceptor or provide a clean Login modal / auto-dev bootstrap token injector using the bootstrap credentials (`admin@sortiq.local` with the local dev bootstrap token) so every request succeeds with 200 OK.
   - If Django uses SessionAuthentication / CSRF, configure axios/fetch credentials: 'include' and pass the `X-CSRFToken` header.

2. Complete UI/UX Redesign & Modern Layout:
   - Replace the bare navigation bar with a modern desktop layout:
     * Left-hand collapsible sidebar with Lucide icons (LayoutDashboard, FolderSearch, CopyCheck, FolderTree, History, Settings).
     * Top header showing real-time health badges for Django (:8000) and FastAPI (:8100), active database path (SQLite), and quick Django Admin launch button.
     * Use a balanced dark-mode palette (e.g. slate-900 / zinc-900 backgrounds, subtle border-slate-800 dividers, vibrant violet/indigo or emerald accents).
   
3. Overhaul Feature Views:
   - **Scan Center**:
     * Quick-pick shortcut pills for standard Windows locations (`C:\Users\%USERNAME%\Downloads`, `Documents`, `Pictures`, custom path).
     * Polished input card with validation and active "Add & Scan" action.
     * Registered folders table showing directory name, file count, last scanned timestamp, and action buttons (Scan Now, Remove).
     * Live scan status progress indicator when a background task is running.
   - **Dashboard**:
     * Grid of metric cards: Total Files Indexed, Storage Managed, Duplicate Clusters Found, Staged Safe Operations.
     * Interactive recent operations log table with status badges (success, quarantined, pending).
   - **Duplicate Hub**:
     * Collapsible duplicate clusters grouped by SHA-256 hash and file size.
     * Visual comparison cards showing path, modified date, and size.
     * Quick actions: "Keep Newest", "Keep Oldest", "Move to Quarantine".
   - **File Explorer**:
     * Category filter chips (Documents, Images, Audio, Video, Archives, Code).
     * Search bar with instant client/server filtering.
     * Clean table with file extension badges, human-readable file sizes, and directory locations.
   - **Operations & Safety**:
     * Write-Ahead Log view showing rollback-ready actions.
     * "Undo Operation" button invoking `/api/v1/operations/{id}/rollback/`.

4. Verification:
   - Run `cd frontend && npm run build` and ensure 0 TypeScript or packaging errors.
   - Verify network requests to `/api/v1/folders/`, `/api/v1/files/`, etc., return 200 OK without 401 errors.

5. Git Commit & Push:
   - Author / Committer: "Abi Thomas <abithomas520@gmail.com>"
   - STRICT REQUIREMENT: ZERO AI/bot attribution trailers (NO "Co-Authored-By", NO "Generated with Claude", NO AI signatures).
   - Commit message: "feat: redesign modern desktop ui and resolve api authentication 401s"
   - Push to origin main.