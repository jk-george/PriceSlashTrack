# ☁️ Cloud Deployment of the Lambda

This folder contains the Terraform code for the subscriber checking Lambda function.

## 🛠️ Prerequisites

Please read the README located in the top-level Terraform folder for detailed instructions on the required prerequisites.

## ⚙️ Setup

1. Create a `terraform.tfvars` file and fill it with the following variables:
```bash
# RDS Database Config
DB_USER = "the-rds-username"
DB_NAME = "the-rds-name"
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