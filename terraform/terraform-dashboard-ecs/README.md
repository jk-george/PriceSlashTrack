# ☁️ Cloud Deployment of the dashboard ECS Service

This folder contains the Terraform code for the ECS Service that will run the Streamlit dashboard.

## 🛠️ Prerequisites

Please read the README located in the top-level Terraform folder for detailed instructions on the required prerequisites.

## ⚙️ Setup

1. Create a `terraform.tfvars` file and fill it with the following variables:
```bash
# AWS Credentials
AWS_ACCESS_KEY = "your-aws-access-key"
AWS_SECRET_KEY = "your-aws-secret-key"
FROM_EMAIL = "your-verified-ses-sender-email"
DASHBOARD_ECR_NAME = "your-dashboard-ecr-repo-name"

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