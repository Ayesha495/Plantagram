---
type: "platform"
phase: 1
area: "platform"
tags: [platform]
---
# CD Pipeline

Merge to main -> image to GHCR -> bump staging values -> Argo CD sync -> smoke tests. release-please tag + manual approval promotes the same digest to production.

## Related
- [[Argo CD]]
- [[Release Process]]
- [[Staging Environment]]
- [[Production Environment]]
- [[Phase 1 - DevOps Platform]]
- [[DevOps MOC]]
