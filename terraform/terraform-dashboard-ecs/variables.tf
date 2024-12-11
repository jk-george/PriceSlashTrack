variable "AWS_ACCESS_KEY" {
  type = string
  description = "Access Key"
}
variable "AWS_SECRET_KEY" {
  type = string
  description = "Secret Key"
}

variable "FROM_EMAIL" {
  type = string
  description = "Our company emailer"
}


variable "DB_USER" {
    type = string
    description = "Database Username"
}
variable "DB_PASSWORD"{
    type = string
    description = "Database Password"
}
variable "DB_NAME" {
    type = string
    description = "Database Name"
}
variable "DB_HOST"{
    type = string
    description = "Database Host"
}
variable "DB_PORT"{
    type = string
    description = "Database Port"
}


variable "DASHBOARD_ECR_NAME"{
    type = string
    description = "ECR that holds the Dashboard."
}