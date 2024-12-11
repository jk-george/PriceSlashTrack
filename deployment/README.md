## ✈️ Deployment

The contents of this directory are bash files that are used for deployment.

Run the following commands from the **main** directory whilst also completing the intermediatory steps:

1. Run `bash deployment/create_rds.sh`
2. Run `bash deployment/initial_terraforming.sh`
3. Run `bash deployment/dockerising_step.sh`
4.  Find the `Image URI` of the `Image` (**not Image Index**) within the ECR: `c14-priceslashers-subscription-checker-repo` and add this to the terraform.tfvars file within the `terraform/terraform-subscriber-lambda` directory. 
5. Run `bash deployment/final_terraforming.sh`
