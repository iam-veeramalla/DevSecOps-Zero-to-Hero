# Vault Production Setup on EC2 + GitHub Actions 

GitHub Actions → Vault (EC2) → AWS (temporary credentials)

---

## Step 1: Launch EC2 for Vault

- AMI: Ubuntu 22.04
- Instance type: t2.micro
- Security Group:
  - SSH (22) → your IP
  - Vault (8200) → GitHub IPs (demo: 0.0.0.0/0)

SSH:
```bash
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP
```

---

## Step 2: Install Vault

```bash
sudo apt update
sudo apt install -y unzip wget
wget https://releases.hashicorp.com/vault/1.15.5/vault_1.15.5_linux_amd64.zip
unzip vault_1.15.5_linux_amd64.zip
sudo mv vault /usr/local/bin/
vault version
```

---

## Step 3: Run Vault

```bash
vault server -dev -dev-root-token-id="root" -dev-listen-address="0.0.0.0:8200"
```

---

## Step 4: Configure Vault

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
vault login root

# Enable AWS Engine
vault secrets enable aws

# Configure connection using your IAM User keys (Manager keys)
vault write aws/config/root \
    access_key="AKIA..." \
    secret_key="SECRET..." \
    region="us-east-1"

# Create the role that vends S3 keys
vault write aws/roles/terraform-role \
    credential_type=iam_user \
    policy_document=-<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    }
  ]
}
EOF
```

---

## Step 5: GitHub Actions OIDC trust

```bash
# Enable JWT Auth
vault auth enable jwt

# Configure OIDC connection
vault write auth/jwt/config \
    oidc_discovery_url="https://token.actions.githubusercontent.com" \
    bound_issuer="https://token.actions.githubusercontent.com"

# Create Policy
vault policy write terraform-policy - <<EOF
path "aws/creds/terraform-role" {
  capabilities = ["read"]
}
EOF

# Bind Repo to Policy (Replace with your GitHub user/repo)
vault write auth/jwt/role/gh-actions-role - <<EOF
{
  "role_type": "jwt",
  "bound_audiences": ["https://github.com/iam-veeramalla"],
  "user_claim": "sub",
  "bound_claims_type": "glob",
  "bound_claims": {
    "sub": "repo:iam-veeramalla/DevSecOps-Zero-to-Hero:*"
  },
  "token_policies": ["terraform-policy"],
  "token_ttl": "1h"
}
EOF
```

---


## Step 6: Terraform code

```bash
provider "aws" {
  region = "us-east-1"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "test_bucket" {
  bucket = "vault-demo-bucket-${random_id.bucket_suffix.hex}"
}
```

---

## Step 7: GitHub Workflow

```bash
name: Terraform Deployment
on: [push]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./terraform

    steps:
      - uses: actions/checkout@v4

      - name: Fetch Keys from Vault
        uses: hashicorp/vault-action@v3
        with:
          url: http://<YOUR_EC2_IP>:8200
          role: gh-actions-role
          method: jwt
          secrets: |
            aws/creds/terraform-role access_key | AWS_ACCESS_KEY_ID ;
            aws/creds/terraform-role secret_key | AWS_SECRET_ACCESS_KEY

      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: terraform plan
      - run: terraform apply -auto-approve
```

