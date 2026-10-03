# Tenant Workloads Repository

**Owner**: Application Engineering / Tenant Teams (e.g., Tenant-A)
**Upstream GitHub Remote**: `https://github.com/brunobml/tenant-workloads.git`

Tenants **register** their application environments here. Each tenant has its own ApplicationSet
in gitops-control-plane (`applicationsets/tenant-workloads-<tenant>.yaml`, 2026-10-03 Track B.2),
which turns every registration file under `tenants/<tenant>/apps/` into an Argo CD Application.
A malformed file therefore stops only its own tenant. Registering an app or environment is a pull
request in this repository (the required check `registration-checks` must pass). Onboarding a new
*tenant* is a platform change: the platform adds that tenant's ApplicationSet with
`scripts/tenant-appset.sh <tenant>`; until then CI rejects a new `tenants/<tenant>/` directory.

```text
tenants/
└── tenant-a/
    └── apps/
        ├── orders-dev.yaml    # -> Application orders-dev  on spoke-nonprod (AWS account 111111111111)
        ├── orders-test.yaml   # -> Application orders-test on spoke-nonprod (AWS account 111111111111)
        └── orders-prod.yaml   # -> Application orders-prod on spoke-prod    (AWS account 222222222222)
```

Registration format, rules and the prod promotion flow: [`tenants/README.md`](tenants/README.md)
and [`developer-tutorial.md`](developer-tutorial.md).
