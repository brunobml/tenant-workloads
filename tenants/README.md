# Tenant registrations

Each file in `tenants/<tenant>/apps/<app>-<env>.yaml` registers one application environment.
The platform's per-tenant ApplicationSet (gitops-control-plane `tenant-workloads-<tenant>`, Track B.2) turns every file into an
Argo CD Application `<app>-<env>` in namespace `<app>-<env>`; a pull request here is all it takes.

* `env` must be `dev`, `test` or `prod`; the platform picks the cluster and AWS account.
* `prod` must pin `valuesRevision` to a full 40-character commit SHA (promotion gate).
* The `tenant-workloads` AppProject limits namespaces and resource kinds.

