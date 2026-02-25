"""
Kubernetes deployment manifests for local development with Kind.
"""

# Directory structure:
# ├── base/
# │   ├── namespace.yaml
# │   ├── postgres/
# │   ├── redis/
# │   ├── rabbitmq/
# │   ├── elasticsearch/
# │   ├── jaeger/
# │   ├── auth-service/
# │   ├── user-service/
# │   ├── project-service/
# │   ├── issue-service/
# │   ├── comment-service/
# │   ├── notification-service/
# │   ├── search-service/
# │   ├── audit-service/
# │   └── api-gateway/
# ├── overlays/
# │   ├── dev/
# │   ├── stage/
# │   └── prod/
# └── kustomization.yaml

# This structure uses Kustomize for managing Kubernetes manifests
# with environment-specific overlays for different deployment targets.
