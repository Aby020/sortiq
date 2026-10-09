# Security Model

- PathGuard containment prevents traversal and reserved-device injection.
- IDOR: every DRF viewset scopes by `user=self.request.user`; unauthenticated returns 401, cross-user returns 404/403.
- FastAPI internal endpoints require `X-Internal-Service-Token`. Missing/invalid tokens return 401.
- Correlation middleware binds `X-Request-ID` to structlog JSON context.
- Quarantine replaces delete: `delete` action raises `NotImplementedError`.
