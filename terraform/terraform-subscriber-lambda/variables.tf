variable "DB_NAME" {
    type = string
}

variable "DB_USER" {
    type = string
}

variable "DB_PASSWORD" {
    type = string
}

variable "DB_HOST" {
    type = string
}

variable "DB_PORT" {
    type = string
}

variable "IMAGE_URI" {
    type = string
    description = "The IMAGE URI of the container image to be used for the Lambda Function"
}