# HARD near-miss (the Checkov false positive): wildcard Principal "*" but a
# scoping Condition (source-IP) — the bucket is NOT public. MUST NOT flag.
resource "aws_s3_bucket" "conditioned" {
  bucket = "demo"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::demo/*",
      "Condition": {
        "IpAddress": { "aws:SourceIp": "10.0.0.0/8" }
      }
    }
  ]
}
POLICY
}
