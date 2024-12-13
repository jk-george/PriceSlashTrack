
variable ETL_ECR_NAME {
    type = string
    description = "ECR name for ETL process"
}

variable DB_HOST {
    type = string
    description = "Host address for database"
}

variable DB_PORT {
    type = string
    description = "Port for the database"
}

variable DB_PASSWORD {
    type = string
    description = "Password for database login"
}

variable DB_USER {
    type = string
    description = "Username for database"
}

variable DB_NAME {
    type = string
    description = "Name of the database"
}


variable ECS_CLUSTER_NAME {
    type = string
    description = " Holds the ECS Cluster name "
}

variable VPC_ID {
    type = string
    description = " Holds VPC ID "
}

variable SUBNET_IDS {
    type = list(string)
    description = " List of Public Subnet IDs "
}

variable FROM_EMAIL {
    type = string
    description = " From Email (our no reply email.) "
}


variable ACCESS_KEY {
    type = string
    description = " ACCESS_KEY for AWS"
}


variable SECRET_KEY {
    type = string
    description = " SECRET_KEY for AWS"
}