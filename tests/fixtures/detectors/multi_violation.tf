resource "aws_s3_bucket" "b" {
  bucket = "x"
  acl    = "public-read"
}

resource "aws_security_group" "sg" {
  ingress {
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ebs_volume" "v" {
  size      = 8
  encrypted = false
}

resource "aws_db_instance" "d" {
  publicly_accessible = true
}
