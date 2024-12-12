
cd terraform/terraform-dashboard-sub-removal-ecr
terraform init
terraform apply

cd ../terraform-dashboard-ecs
terraform init
terraform apply

cd ../terraform-etl-iterator
terraform init
terraform apply

