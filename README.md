# Tenant Workloads Repository

**Owner**: Application Engineering / Tenant Teams (e.g., Tenant-A)
**Upstream GitHub Remote**: `https://github.com/brunobml/tenant-workloads.git`

Tenants **register** their application environments here. The platform's `tenant-workloads`
ApplicationSet (gitops-control-plane, `applicationsets/tenant-workloads.yaml`) turns every
registration file into an Argo CD Application. A pull request in this repository is all a tenant
needs; the control-plane repository is not touched.

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
