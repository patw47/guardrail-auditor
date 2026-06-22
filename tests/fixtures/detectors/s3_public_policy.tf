resource "aws_s3_bucket" "public_policy" {
  bucket = "demo"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::demo/*"
    }
  ]
}
POLICY
}
