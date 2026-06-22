# A safe configuration — every detector's near-miss. Should yield ZERO findings.
resource "aws_s3_bucket" "private" {
  bucket = "private-bucket"
  acl    = "private"
}

resource "aws_security_group" "restricted" {
  ingress {
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["10.0.0.0/8"]
  }
}

resource "aws_ebs_volume" "vol" {
  availability_zone = "us-east-1a"
  size              = 8
  encrypted         = true
}

resource "aws_db_instance" "db" {
  engine              = "mysql"
  publicly_accessible = false
  storage_encrypted   = true
}
