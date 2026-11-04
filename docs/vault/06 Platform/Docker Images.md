---
type: "platform"
phase: 1
area: "platform"
tags: [platform]
---
# Docker Images

Multi-stage, non-root, multi-arch (amd64 + arm64) images: `api` (gunicorn), `worker` (Celery), `web` (Expo web export on Nginx). Signed with cosign, SBOM via Syft.

## Related
- [[GitHub Container Registry]]
- [[CI Pipeline]]
- [[Helm Chart]]
- [[Phase 1 - DevOps Platform]]
- [[DevOps MOC]]
