resource "aws_s3_bucket" "broken" {
  bucket =
  acl    "public-read"
