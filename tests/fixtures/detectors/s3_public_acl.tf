resource "aws_s3_bucket" "public_acl" {
  bucket = "demo"
  acl    = "public-read"
}
