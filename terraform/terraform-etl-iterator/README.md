# ☁️ Cloud Deployment of the dashboard ECS Service

This folder contains the Terraform code for the ETL pipeline, including the ECR repository the Docker image will be held in and the EventBridge scheduler that runs every 3 minutes.

## 🛠️ Prerequisites

Please read the README located in the top-level Terraform folder for detailed instructions on the required prerequisites.

## ⚙️ Setup

1. Create a `terraform.tfvars` file and fill it with the following variables:
```bash
# ECR Repository
ETL_ECR_NAME = "ecr-repo-name-for-etl-pipeline"

# AWS Network Config
ECS_CLUSTER_NAME = "the-aws-ecs-cluster-name"
VPC_ID = "the-vpc-id"
SUBNET_IDS = ["the-first-subnet-id","the-second-subnet-id","the-third-subnet-id"]

# RDS Database Config
DB_HOST = "the-rds-host-address"
DB_USER = "the-rds-username"
DB_PASSWORD = "the-rds-password"
DB_NAME = "the-rds-name"
DB_PORT = "the-rds-port-number"
```

2. Initialise Terraform:
```bash
terraform init
```

3. Deploy cloud services:
```bash
terraform apply
```
  - Enter 'yes' when it asks to approve changes.
  - Can be used to redeploy if resource definitions have been changed.

4. To bring down the cloud infrastructure:
```bash
terraform destroy
```