# Kubernetes Security

---

## Prerequisites

* Docker installed
* kubectl installed
* kind installed

Check versions:

```
docker --version
kubectl version --client
kind version
```

---

## Cluster Setup (kind)

Create a dedicated cluster for security demos:

```
kind create cluster --name k8s-security
```

Verify:

```
kubectl get nodes
```

---

# 1. Namespaces

## What is a Namespace?

A namespace is a **logical isolation boundary** inside a Kubernetes cluster.

Namespaces help with:

* Team or project separation (payments, search, platform)
* Team isolation
* Applying security controls (RBAC, NetworkPolicy, quotas)

> Kubernetes security always starts with namespaces.

---

## Hands-On: Creating Namespaces

Create namespaces for teams/projects:

```
kubectl create namespace payments
kubectl create namespace search
```

Verify:

```
kubectl get namespaces
```

---

## Hands-On: Deploying Apps in Different Namespaces

Create a simple nginx deployment in `payments`:

```
kubectl create deployment nginx-payments --image=nginx -n payments
```

Create the same in `search`:

```
kubectl create deployment nginx-search --image=nginx -n search
```

Verify:

```
kubectl get pods -n payments
kubectl get pods -n search
```

**Key takeaway:**

* Namespaces map cleanly to teams or projects
* Isolation helps apply RBAC, NetworkPolicy, and quotas per team

Namespaces do NOT provide security by default (yet)

---

# 2. RBAC (Role-Based Access Control)

## What is RBAC?

RBAC controls **who can do what** in a Kubernetes cluster.

RBAC answers:

* Who? → User / ServiceAccount
* What? → Verbs (get, list, create, delete)
* On what? → Resources (pods, secrets, deployments)
* Where? → Namespace or cluster

---

## RBAC Components

* **Role**: Permissions within a namespace
* **ClusterRole**: Permissions cluster-wide
* **RoleBinding**: Binds Role to a subject
* **ClusterRoleBinding**: Binds ClusterRole to a subject

---

## Hands-On: Create a Read-Only Role for Pods

Create a Role in `payments` namespace:

```
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: payments
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
EOF
```

---

## Hands-On: Create a ServiceAccount

```
kubectl create serviceaccount payments-user -n payments
```

---

## Hands-On: Bind Role to ServiceAccount

```
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods-binding
  namespace: payments
subjects:
- kind: ServiceAccount
  name: payments-user
  namespace: payments
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
EOF
```

---

## Verification (Very Important)

Check permissions:

```
kubectl auth can-i list pods \
  --as=system:serviceaccount:payments:payments-user \
  -n payments
```

Expected output:

```
yes
```

Try deleting pods:

```
kubectl auth can-i delete pods \
  --as=system:serviceaccount:dev:dev-user \
  -n payments
```

Expected output:

```
no
```

---

# 3. Network Policies

## What is a NetworkPolicy?

By default:

* All pods can talk to all pods

NetworkPolicy allows:

* Deny all traffic by default
* Explicitly allow required traffic

> NetworkPolicy is **zero-trust networking** for Kubernetes.

---

## Important Note (kind)

kind supports NetworkPolicy **only if a CNI like Calico is installed**.

We will install Calico.

---

## Install Calico on kind

```
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml
```

Wait until ready:

```
kubectl get pods -n kube-system
```

---

## Hands-On Setup: Backend and Frontend Pods

We will simulate a real application:

frontend → allowed to access backend

other pods → should be blocked

### Create backend pod:

```
kubectl run backend \
  --image=nginx \
  --labels="app=my-app" \
  -n payments
```

### Create frontend pod:

```
kubectl run frontend \
  --image=busybox \
  --labels="role=frontend" \
  -n payments -- sleep 3600
```

### Create an attacker pod:

```
kubectl run attacker \
  --image=busybox \
  -n payments -- sleep 3600
```

### Expose backend:

```
kubectl expose pod backend \
  --port=80 \
  --name=backend-svc \
  -n payments
```

### Verify Default Behavior (No NetworkPolicy)

Exec into attacker:

```
kubectl exec -it attacker -n payments -- sh
```

Try accessing backend:

`wget -qO- backend-svc`

This works, because Kubernetes allows all traffic by default.

### Apply NetworkPolicy: Allow Specific Traffic Only

```
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-specific-traffic
  namespace: payments
spec:
  podSelector:
    matchLabels:
      app: my-app
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 80
EOF
```

Now we restrict traffic so that:

Only pods with role=frontend can access backend

Only on TCP port 80

### Verify NetworkPolicy Enforcement

From frontend pod:

```
kubectl exec -it frontend -n payments -- sh
wget -qO- backend-svc
```

This should work.

From attacker pod:

```
kubectl exec -it attacker -n payments -- sh
wget -qO- backend-svc
```

This should fail.

---

# 4. Kyverno (Policy as Code)

## What is Kyverno?

Kyverno is a **Kubernetes-native policy engine**.

It can:

* Validate manifests
* Mutate resources
* Generate resources

No new language. Uses YAML.

---

## Install Kyverno

```
kubectl apply --server-side -f https://github.com/kyverno/kyverno/releases/latest/download/install.yaml
```

Verify:

```
kubectl get pods -n kyverno
```

---

## Hands-On: Enforce No Latest Tag

Policy:

```
kubectl apply -f - <<EOF
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-latest-tag
spec:
  validationFailureAction: Enforce
  rules:
  - name: require-image-tag
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Image tag 'latest' is not allowed"
      pattern:
        spec:
          containers:
          - image: "!*:latest"
EOF
```

---

## Test Kyverno Policy

This should fail:

```
kubectl run bad-pod --image=nginx:latest -n payments
```

This should succeed:

```
kubectl run good-pod --image=nginx:1.25 -n payments
```

---

# 5. Secret Management

## Why Secrets Matter

Never:

* Hardcode passwords
* Commit secrets to Git

Kubernetes Secrets store sensitive data safely (base64 encoded).

---

## Hands-On: Create a Secret

```
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=StrongPassword123 \
  -n dev
```

Verify:

```
kubectl get secrets -n dev
```

---

## Hands-On: Use Secret as Environment Variables

```
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: secret-demo
  namespace: dev
spec:
  containers:
  - name: app
    image: busybox
    command: ["sh", "-c", "env && sleep 3600"]
    env:
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
EOF
```

Check:

```
kubectl logs secret-demo -n dev
```

---

## Security Best Practices (Real World)

* Combine Secrets + RBAC
* Restrict secret access per namespace
* Never expose secrets via logs
* Avoid storing plain Kubernetes Secrets in Git

---

# 6. Git-Safe Secret Management (External Secrets Operator)

## The Real Problem

Kubernetes Secrets are **not safe to store in Git**:

* Base64 encoding is NOT encryption
* Anyone with repo access can decode secrets

Real teams need:

* GitOps-friendly workflows
* Secrets stored **outside** the cluster
* Automatic sync into Kubernetes

This is where **External Secrets Operator (ESO)** fits perfectly.

---

## What is External Secrets Operator (ESO)?

ESO allows Kubernetes to:

* Read secrets from external secret stores
* Inject them as native Kubernetes Secrets

Common backends:

* AWS Secrets Manager
* HashiCorp Vault
* Azure Key Vault

For learning purposes, we will use **Vault** (simple and widely used).

---

## High-Level Flow (Very Important)

1. Secret is stored securely in Vault
2. Git contains only a reference (not the secret)
3. ESO syncs the secret into Kubernetes
4. Pods consume it like a normal Secret

Git stays clean. Secrets stay safe.

---

## Install External Secrets Operator

```
helm repo add external-secrets https://charts.external-secrets.io
helm repo update
```

Verify:

```
kubectl get pods -n external-secrets
```

---

## Install Vault

```
kubectl create namespace vault

kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vault
  namespace: vault
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vault
  template:
    metadata:
      labels:
        app: vault
    spec:
      containers:
      - name: vault
        image: hashicorp/vault:1.15
        args: ["server", "-dev"]
        env:
        - name: VAULT_DEV_ROOT_TOKEN_ID
          value: root
        - name: VAULT_DEV_LISTEN_ADDRESS
          value: 0.0.0.0:8200
        ports:
        - containerPort: 8200
EOF
```

Expose Vault:

```
kubectl port-forward -n vault deploy/vault 8200:8200
```

---

## Store a Secret in Vault

In another terminal:

```
kubectl exec -it -n vault deploy/vault -- sh

export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=root

vault kv put secret/payments/db username=admin password=SuperSecret123
```

Create Vault Token Secret

```
kubectl create secret generic vault-token \
  --from-literal=token=root \
  -n payments
```

---

## Create a SecretStore (Vault Connection)

```
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: payments
spec:
  provider:
    vault:
      server: "http://vault.vault.svc.cluster.local:8200"
      path: "secret"
      version: "v2"
      auth:
        tokenSecretRef:
          name: vault-token
          key: token
EOF
```

---

## Create ExternalSecret (Git-Safe)

This is what goes into Git:

```
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: db-secret
  namespace: payments
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: db-secret
    creationPolicy: Owner
  data:
  - secretKey: username
    remoteRef:
      key: payments/db
      property: username
  - secretKey: password
    remoteRef:
      key: payments/db
      property: password
EOF
```

Verify:

```
kubectl get secrets -n payments
```

---

## Consume the Secret (No Changes for App)

Pods consume it like any Kubernetes Secret:

```
env:
- name: DB_USER
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: username
```

---

## Cleanup

```
kind delete cluster --name k8s-security
```
---

