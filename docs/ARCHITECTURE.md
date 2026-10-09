# Sortiq Architecture

## Dual-plane design

Django (port 8000) serves the public REST API, auth, persistence, and Celery task scheduling. FastAPI (port 8100, internal token-protected) handles high-throughput scan streams and batch hashing. Both planes share the same database and filesystem state; the Operations Engine is the only permitted mutation path.

## Operations WAL engine

PlanItem (source, target, action) → OperationPlan (conflict detection) → execute_plan (stat verification, apply, post-state record) → _persist_journal (Operation + OperationItem ORM records). Rollback iterates items with status==success and reverses `shutil.move`, setting operation.status="rolled_back".

## Windows path containment

`normalize()` handles drive-letter casing, mixed slashes, and UNC paths. `validate()` rejects traversal, reserved device names (`COM1`, `NUL`), relative escapes, and paths outside the root.
