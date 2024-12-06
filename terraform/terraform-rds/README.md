# ☁️ Cloud Deployment of the dashboard ECS Service

This folder contains the Terraform code for the AWS RDS (PostgreSQL) database.

## 🛠️ Prerequisites

Please read the README located in the top-level Terraform folder for detailed instructions on the required prerequisites.

## ⚙️ Setup

1. Create a `terraform.tfvars` file and fill it with the following variables:
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID = "your-aws-access-key"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-key"

# RDS Database Config
DB_USERNAME = "the-rds-username" # this is not standard across the files - in the ETL iterator main.tf, it's DB_USER, in this folder's main.tf, it's DB_USERNAME - make this standard!
DB_PASSWORD = "the-rds-password"
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