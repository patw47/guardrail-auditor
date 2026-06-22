resource "aws_security_group" "single" {
  ingress {
    from_port = 22
  }
}

resource "aws_security_group" "multi" {
  ingress {
    from_port = 22
  }
  ingress {
    from_port = 443
  }
}
