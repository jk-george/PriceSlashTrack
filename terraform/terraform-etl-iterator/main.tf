provider "aws" {
  region = "eu-west-2"
}


resource "aws_ecr_repository" "ecr_for_etl" {
  name                 = var.ETL_ECR_NAME  
  image_tag_mutability = "MUTABLE"  
  image_scanning_configuration {
    scan_on_push = true  
  }

  lifecycle {
    prevent_destroy = false  
  }
}
