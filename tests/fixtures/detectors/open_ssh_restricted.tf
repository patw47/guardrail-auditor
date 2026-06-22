# near-miss: SSH only from a private CIDR, plus 443 open to the world.
# Neither is SSH-from-0.0.0.0/0 — MUST NOT flag OPEN_SSH.
resource "aws_security_group" "restricted" {
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
