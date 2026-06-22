# Top-of-file comment
// double-slash comment
/* block comment
   spanning two lines */

resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-public-bucket"
  acl    = "public-read"
  tags = { Name = "demo" }
}

# a comment between resources

resource "aws_security_group" "open_ssh" {
  name = "open-ssh"

  // a comment before the nested block
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
