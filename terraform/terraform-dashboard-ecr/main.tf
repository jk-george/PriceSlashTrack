provider "aws" {
  region = "eu-west-2"
}


resource "aws_ecr_repository" "ecr_for_dashboard" {
  name                 = var.DASHBOARD_ECR_NAME
  image_tag_mutability = "MUTABLE"  
  image_scanning_configuration {
    scan_on_push = true
  }
  force_delete = true

  lifecycle {
    prevent_destroy = false
  }
}