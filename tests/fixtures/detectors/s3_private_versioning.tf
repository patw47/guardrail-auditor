# ADAPTER §2 near-miss: private bucket with versioning enabled — MUST NOT flag.
resource "aws_s3_bucket" "private_versioned" {
  bucket = "demo"
  acl    = "private"

  versioning {
    enabled = true
  }
}
