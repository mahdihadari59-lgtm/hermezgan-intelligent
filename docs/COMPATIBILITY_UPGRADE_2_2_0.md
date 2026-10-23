# Compatibility-Safe Upgrade Guide

## Overview
This repository contains multiple parallel implementation layers (backend, frontend, mobile, legacy modules, data pipeline helpers, and archived variants). To avoid breaking the working system, the upgrade was performed in compatibility-safe mode instead of a destructive merge.

## Version policy
- Project core version: 2.2.0
- Backend package version: 2.2.0
- Frontend package version: 2.2.0
- Legacy modules: kept in place and marked as compatibility / archive-friendly until fully validated

## Safety principles applied
1. Preserve working modules and routes.
2. Do not delete duplicate modules without validation.
3. Keep compatibility shims for legacy APIs.
4. Unify version metadata in a central place.
5. Document release changes before final hard migration.

## Files updated
- VERSION
- package.json
- frontend/package.json
- backend/app/__init__.py
- CHANGELOG.md

## Recommended next steps
- Run smoke tests for backend and frontend.
- Validate API routes still respond correctly.
- Review archived folders before final cleanup.
- Keep legacy endpoints available until all clients are migrated.

## Rollback guidance
If a specific change causes incompatibility, revert only the metadata or compatibility section while preserving the archived modules. This avoids losing working legacy functionality.
