# Checkov 

---

## Problem 

Terraform can deploy insecure infrastructure without warnings:
- Public S3 buckets
- SSH open to the internet
- No encryption

---

## What Is Checkov?

Checkov scans Terraform code for security misconfigurations
BEFORE infrastructure is deployed.

---

### Step 1: Install Checkov

```bash
pip install checkov
```

Verify:
```bash
checkov --version
```

---

## Step 2: Create Insecure Terraform Code

```bash
mkdir terraform-checkov-demo
cd terraform-checkov-demo
```

Create `main.tf` (INSECURE ON PURPOSE):

```bash
cat <<EOF > main.tf

resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-public-demo-bucket"
}

resource "aws_s3_bucket_acl" "public_acl" {
  bucket = aws_s3_bucket.public_bucket.id
  acl    = "public-read"
}

resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket                  = aws_s3_bucket.public_bucket.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

EOF
```

---

## Step 3: Scan with Checkov

```bash
checkov -d .
```

---

### What You Should See

❌ Public S3 bucket  
❌ SSH open to 0.0.0.0/0  

Terraform did NOT warn you.
Checkov did.

---

## Step 4: Fix the Terraform Code

```bash
cat <<EOF > main.tf
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-demo-bucket"
}

resource "aws_s3_bucket_public_access_block" "secure_access" {
  bucket                  = aws_s3_bucket.secure_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

EOF
```

---

## Step 5: Re-Scan

```bash
checkov -d .
```

✅ No critical findings.

---

## Key Takeaway

Terraform builds infrastructure.
Checkov secures it before deployment.
