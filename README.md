# Tenant Workloads Repository

**Owner**: Application Engineering / Tenant Teams (e.g., Tenant-A)  
**Upstream GitHub Remote**: `https://github.com/brunobml/tenant-workloads.git`

This repository contains declarative tenant application specifications consuming platform blueprints.

## Multi-Tenant & Multi-Environment Directory Structure
```text
tenants/
└── tenant-a/
    ├── dev/                # Deployed to spoke-nonprod (namespace: tenant-a-dev)
    │   └── orders-service.yaml
    ├── test/               # Deployed to spoke-nonprod (namespace: tenant-a-test)
    │   └── orders-service.yaml
    └── prod/               # Deployed to spoke-prod (namespace: tenant-a-prod)
        └── orders-service.yaml
```

Argo CD's `ApplicationSet` in the Hub cluster automatically monitors this repository, discovers folders matching `tenants/*/*`, and routes them to the target spoke cluster and namespace.
