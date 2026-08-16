name=RELEASE_CHECKLIST.md
# Release checklist for Hermezgan Intelligent Platform

- [ ] All unit tests pass (backend & frontend)
- [ ] Integration tests pass in docker-compose.dev
- [ ] Security review done for env variables and secrets
- [ ] Remove or archive large files (or move to object storage)
- [ ] Update CHANGELOG.md
- [ ] Bump version in app metadata
- [ ] Build & push Docker images to registry
- [ ] Create GitHub Release and attach CHANGELOG
- [ ] Announce release and update deployment docs