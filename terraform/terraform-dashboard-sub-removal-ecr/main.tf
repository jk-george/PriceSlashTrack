provider "aws" {
  region = "eu-west-2"
}

# ECR Repository for Dashboard Container Image

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


# ECR Repository for Subscription removal Container Image

resource "aws_ecr_repository" "c14-price-slash-subscription-checker" {
  name = "c14-priceslashers-subscription-checker-repo"
  image_tag_mutability = "MUTABLE"  
  image_scanning_configuration {
    scan_on_push = true
  }
  force_delete = true

  lifecycle {
    prevent_destroy = false
  }
}
