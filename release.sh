name=release.sh
#!/usr/bin/env bash
set -euo pipefail

# release.sh - simple release helper
# Usage: ./release.sh v1.0.0

VERSION=${1:-}
if [[ -z "${VERSION}" ]]; then
  echo "Usage: $0 vX.Y.Z"
  exit 1
fi

# Run tests
cd backend
pip install -r requirements-full.txt
pytest -q
cd ..

# Build and push images
docker build -t ghcr.io/${GITHUB_REPOSITORY_OWNER:-mahdihadari16-stack}/hermezgan-backend:${VERSION} -f services/backend/Dockerfile .
docker build -t ghcr.io/${GITHUB_REPOSITORY_OWNER:-mahdihadari16-stack}/hermezgan-frontend:${VERSION} -f services/frontend/Dockerfile .

docker push ghcr.io/${GITHUB_REPOSITORY_OWNER:-mahdihadari16-stack}/hermezgan-backend:${VERSION}
docker push ghcr.io/${GITHUB_REPOSITORY_OWNER:-mahdihadari16-stack}/hermezgan-frontend:${VERSION}

# Create git tag and GitHub release
git tag -a ${VERSION} -m "Release ${VERSION}"
git push origin ${VERSION}

echo "Release ${VERSION} created. Consider creating a GitHub Release with notes."