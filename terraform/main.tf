# 1. Define the Provider
provider "aws" {
  region = "us-east-1"
}

# 2. Create a Random ID for unique bucket naming
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# 3. Create the S3 Bucket
resource "aws_s3_bucket" "vault_test_bucket" {
  bucket = "devsecops-vault-demo-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "Vault Dynamic Secret Test"
    Environment = "Dev"
    ManagedBy   = "Terraform"
  }
}

# 4. (Optional) Output the bucket name so you can see it in GitHub logs
output "bucket_name" {
  value = aws_s3_bucket.vault_test_bucket.id
}
