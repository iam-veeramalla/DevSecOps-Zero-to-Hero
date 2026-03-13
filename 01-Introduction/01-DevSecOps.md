DevSecOps is a mindset where security is built into every step of software development and operations

---

# 🔐 DevSecOps Security Practices

## 1️⃣ **Git Security**
Git security practices
- Secret scanning (GitLeaks, TruffleHog)
- Protected branches (no direct pushes)
- Mandatory PR reviews
- Commit signing (GPG/SSH)
- Pre‑commit hooks for linting & basic SAST
- Dependency pinning
- CODEOWNERS enforcement

---

## 2️⃣ **Scripting Security**
Following best scripting security practices.
- No hardcoded secrets (use env vars or secret managers)
- Input validation & sanitization
- Least‑privilege execution (avoid sudo)
- Secure API handling (TLS verification)
- Logging with redaction
- Static analysis (ShellCheck, Bandit)
- Safe error handling

---

## 3️⃣ **Container Security**
Types of Container Security
- Image scanning (Trivy, Grype)
- Minimal base images (Alpine, distroless)
- Non‑root containers
- Read‑only root filesystem
- Multi‑stage builds
- SBOM generation (Syft)
- Image signing (Cosign)

---

## 4️⃣ **Infrastructure as Code Security**
Security shifts left into provisioning.
- IaC scanning (Checkov, tfsec)
- Policy‑as‑Code (OPA, Conftest)
- Encrypted Terraform state
- Remote state backends with RBAC
- Drift detection
- Secure module registries
- Enforcing least‑privilege IAM via IaC

---

## 5️⃣ **CI/CD Pipeline Security**
securing the entire delivery chain.
- SAST, DAST, SCA in pipelines
- Ephemeral runners (no persistent agents)
- Secrets management (Vault, SSM, OIDC)
- Dependency scanning (Dependabot, Renovate)
- Artifact signing & verification (Sigstore)
- Pipeline isolation (no shared workspaces)
- Security gates (block deploy on scan failures)

---

## 6️⃣ **Kubernetes Security**
This is where real DevSecOps mastery shows.
- RBAC least privilege
- Network Policies (deny‑all baseline)
- Pod Security Standards (restricted)
- Admission controllers (Kyverno, Gatekeeper)
- Secrets encryption at rest
- Runtime security (Falco, Tetragon)
- Namespace isolation
- Secure Ingress (TLS, cert‑manager)
- Image pull policies & registry restrictions

---

## 7 **Other popular security Practices**
- IAM least privilege
- Encrypt data
- Monitor logs
- Detect attacks while the app is running
- Tools like Falco, CrowdSec, WAFs



