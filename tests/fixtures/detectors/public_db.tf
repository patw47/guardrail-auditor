resource "aws_db_instance" "db" {
  engine              = "mysql"
  publicly_accessible = true
  storage_encrypted   = true
}
