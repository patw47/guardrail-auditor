# near-miss: same resource type, not publicly accessible — MUST NOT flag.
resource "aws_db_instance" "db" {
  engine              = "mysql"
  publicly_accessible = false
  storage_encrypted   = true
}
