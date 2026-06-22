# near-miss: same resource type, encryption enabled — MUST NOT flag.
resource "aws_ebs_volume" "vol" {
  availability_zone = "us-east-1a"
  size              = 8
  encrypted         = true
}
