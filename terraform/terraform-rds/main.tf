provider "aws" {
access_key = var.AWS_ACCESS_KEY_ID
secret_key = var.AWS_SECRET_ACCESS_KEY
region = "eu-west-2"
}

data "aws_vpc" "c14-vpc" {
    id = "vpc-0344763624ac09cb6"
}

data "aws_subnet" "c14-subnet-1" {
  id = "subnet-0497831b67192adc2"
}

data "aws_subnet" "c14-subnet-2" {
  id = "subnet-0acda1bd2efbf3922"
}

data "aws_subnet" "c14-subnet-3" {
  id = "subnet-0465f224c7432a02e"
}



resource "aws_db_instance" "c14-price_slash_db" {
    allocated_storage            = 10
    db_name                      = "priceslash"
    identifier                   = "c14-price-slash-db"
    engine                       = "postgres"
    engine_version               = "16.1"
    instance_class               = "db.t3.micro"
    publicly_accessible          = true
    performance_insights_enabled = false
    skip_final_snapshot          = true
    db_subnet_group_name         = "c14-public-subnet-group"
    vpc_security_group_ids       = [aws_security_group.c14-price_slash_sg.id]
    username                     = var.DB_USER
    password                     = var.DB_PASSWORD
}

resource "aws_security_group" "c14-price_slash_sg" {
    name = "c14-price_slash_sg"
    description = "Security group for connecting to RDS database"
    vpc_id = data.aws_vpc.c14-vpc.id

    egress {
        from_port        = 0
        to_port          = 0
        protocol         = "-1"
        cidr_blocks      = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 5432
        to_port = 5432
        protocol = "tcp"
        cidr_blocks      = ["0.0.0.0/0"]
    }
}