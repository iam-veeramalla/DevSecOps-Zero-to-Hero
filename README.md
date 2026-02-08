# DevSecOps-Zero-to-Hero

## Day 1: The Mindset Shift & Threat Modeling

**Focus**: Understanding the "Sec" in DevSecOps and planning before coding.

### Concepts:
- **What is DevSecOps?** (Shift Left vs. Shield Right)
- **The 2026 Landscape**: AI-driven attacks vs. AI-driven defense
- **Threat Modeling**: Using the STRIDE framework

### Tool Spotlight:
- OWASP Threat Dragon or PyTM

### Hands-on Lab:
- Perform a threat model for a simple 3-tier web application

---

## Day 2: DevSecOps for Git

1. .gitignore  
2. Native Git Pre-Commit Hooks (Custom Scripts)  
3. Block commits with Gitleaks  
4. Gitleaks -> Repository & History Scanning  
5. Gitleaks in GitHub Actions  
6. Branch Protection Rules  
7. RBAC  
8. Mandatory Reviews  
9. CODEOWNERS  
10. Dependabot  

---

## Day 3: IaC Security

### Concepts:
- Best Practices
- **IaC Scanning**: Catching misconfigured S3 buckets or open Security Groups before deployment
- Secret Management with Vault

### Tool Spotlight:
- Gitleaks
- Checkov
- Vault

### Hands-on Lab:
- Scan a "less secure" Terraform repo
- Implement HashiCorp Vault for dynamic secret injection

---

## Day 4: Container Security

**Focus**: Securing the ship (Docker) and the harbor (K8s).

### Concepts:
- Distroless images and multi-stage builds
- **Image Linting**: Finding "root" users and insecure instructions
- **Kubernetes Admission Controllers** and Network Policies

### Tool Spotlight:
- Trivy (Image Scanning)
- Hadolint (Docker Linting)

### Hands-on Lab:
- Scan a Docker image for CVEs
- Deploy a "Secure-by-Default" Pod to a K8s cluster

---

## Day 5: Kubernetes Security

**Focus**: 
 
- Namespaces
- RBAC
- Network Policies
- Kyverno
- Secrets
- External Secrets Operator

---

## Day 6: SAST, SCA and DAST
**Focus**: Testing the running application for real-world exploits.

### Concepts:
- **SAST**
- **SCA**
- **DAST** (Dynamic Application Security Testing): Attacking the app like a hacker


### Tool Spotlight:
- SonarQube
- OWASP ZAP (Automation)

### Hands-on Lab:
- Run an automated ZAP baseline scan against a Python application
- Run SAST and SCA against a Python application

---

## Day 7: The Grand Finale – Building the Ultimate Pipeline

**Focus**: Bringing it all together and the DevSecOps Career Roadmap.

### The Master Project: Build a "Golden Pipeline" that includes:
1. **Secret Scan** (Pre-commit)
2. **SAST/SCA** (Build phase)
3. **IaC Scan** (Provision phase)
4. **DAST** (Post-deploy phase)
5. **AI Fixes**: Use AI (like GitHub Copilot or Snyk AI) to auto-remediate a found bug

### Career Guidance:
- **Certifications**: CASE, CND, DevSecOps Foundation
- **Resume Tips** and guidance for the future of the role
