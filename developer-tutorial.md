# Developer Tutorial: Registering and Promoting an Application

This repository only holds **registrations**. Application code and its Helm values live in the
application's own repository (for `orders`: `brunobml/orders-processor`, `deploy/values-<env>.yaml`).
The platform blueprint (`QueueBackedService`: worker Deployment, SQS queue + DLQ, NetworkPolicy,
ingress) is provided by `platform-catalog`.

## 1. Register an environment
Add `tenants/<tenant>/apps/<app>-<env>.yaml` and open a pull request:

```yaml
tenant: tenant-a
app: orders                 # Application and namespace <app>-<env> (must match orders-*)
env: dev                    # dev | test | prod; the platform chooses the cluster and AWS account
port: "8081"                # spoke ingress port for dashboard links (nonprod 8081, prod 8082)
valuesRevision: main        # commit of deploy/values-<env>.yaml; prod needs a full 40-char SHA
# valuesFile: deploy/values-dev.yaml   # optional, this is the default
```

After the merge, Argo CD creates the Application within a few minutes. The platform operator runs
`make post-bootstrap` once so the new worker gets its cloud credential.

## 2. Promote to production
1. Make sure the image is released and signed by CI (only CI-signed images are admitted).
2. Pin it by digest in `deploy/values-prod.yaml` in the application repository and merge.
3. Here, set `valuesRevision` in `tenants/tenant-a/apps/orders-prod.yaml` to that commit's **full SHA**
   and open a pull request. Anything other than a full SHA is refused by the platform for `prod`.

## 3. Remove an environment
Delete its registration file (pull request). Argo CD removes the Application, the workload and its
queues. The platform's `post-bootstrap` step cleans up the leftover credential and empty namespace.

## 4. See it running
* Argo CD: http://localhost → **Log in via Keycloak** as `tenant-a-user` (sync dev/test; prod is read-only)
* Dashboards: `http://<app>-<env>.localhost:8081` (nonprod), `:8082` (prod)

More detail: `gitops-control-plane/docs/developer-tutorial.md`.
