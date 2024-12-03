provider "aws" {
  region = "eu-west-2"
}


resource "aws_db_instance" "price_slash_db" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t2.micro"
  name                 = "price_slash_db"
  username             = "priceslash"
  password             = "psst"
  parameter_group_name = "default.mysql8.0"
  publicly_accessible  = true
  skip_final_snapshot  = true
}

resource "local_file" "env_file" {
  content  = <<EOT
DB_NAME=${aws_db_instance.price_slash_db.name}
DB_USER=${aws_db_instance.price_slash_db.username}
DB_PASSWORD=${random_password.db_password.result}
DB_HOST=${aws_db_instance.price_slash_db.address}
DB_PORT=${aws_db_instance.price_slash_db.port}
AWS_ACCESS_KEY_ID=${var.aws_access_key_id}
AWS_SECRET_ACCESS_KEY=${var.aws_secret_access_key}
EOT
  filename = "./.env"
}

variable "aws_access_key_id" {}
variable "aws_secret_access_key" {}
