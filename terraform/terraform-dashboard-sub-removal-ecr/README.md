# ☁️ Cloud Deployment of the dashboard ECR repository

This folder contains the Terraform code for the ECR repository that will hold the Docker image for the Streamlit dashboard.

## 🛠️ Prerequisites

Please read the README located in the top-level Terraform folder for detailed instructions on the required prerequisites.

## ⚙️ Setup

1. Create a `terraform.tfvars` file and fill it with the following variables:
```bash
DASHBOARD_ECR_NAME = "your-dashboard-ecr-repo-name"
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