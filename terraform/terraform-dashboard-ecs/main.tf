provider "aws" {
  region = "eu-west-2"
}


data "aws_ecs_cluster" "c14-cluster" {
    cluster_name = "c14-ecs-cluster"
}

data "aws_iam_role" "execution-role" {
    name = "ecsTaskExecutionRole"
}

data "aws_vpc" "c14-vpc" {
    id = "vpc-0344763624ac09cb6"
}

data "aws_subnet" "c14-subnet-1" {
  id = "subnet-0497831b67192adc2"
}

data "aws_subnet" "c14-subnet-2" {
  id = "subnet-0acda1bd2efbf3922"
}

data "aws_subnet" "c14-subnet-3" {
  id = "subnet-0465f224c7432a02e"
}

data "aws_ecr_repository" "ecr_for_dashboard" {
    name = var.DASHBOARD_ECR_NAME
}



resource "aws_ecs_task_definition" "c14-price-slash-dashboard-task-def" {
  family                   = "c14-price-slash-dashboard-task-def"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  execution_role_arn       = data.aws_iam_role.execution-role.arn
  cpu                      = 1024
  memory                   = 2048
  container_definitions    = jsonencode([
    {
      name         = "c14-price-slash-dashboard-task-def"
      image        = data.aws_ecr_repository.ecr_for_dashboard.repository_url
      cpu          = 10
      memory       = 512
      essential    = true
      portMappings = [
        {
            containerPort = 80
            hostPort      = 80
        },
        {
            containerPort = 8501
            hostPort      = 8501       
        }
      ]
      environment= [
                {
                    "name": "ACCESS_KEY",
                    "value": var.AWS_ACCESS_KEY
                },
                {
                    "name": "SECRET_ACCESS_KEY",
                    "value": var.AWS_SECRET_KEY
                },
                {
                    "name": "FROM_EMAIL",
                    "value": var.FROM_EMAIL
                },
                {
                    "name": "DB_NAME",
                    "value": var.DB_NAME
                },
                {
                    "name": "DB_USER",
                    "value": var.DB_USER
                },
                {
                    "name": "DB_PASSWORD",
                    "value": var.DB_PASSWORD
                },
                {
                    "name": "DB_HOST",
                    "value": var.DB_HOST
                },
                {
                    "name": "DB_PORT",
                    "value": var.DB_PORT
                }
            ]
            logConfiguration = {
                logDriver = "awslogs"
                options = {
                    "awslogs-create-group"  = "true"
                    "awslogs-group"         = "/ecs/c14-price-slash-dashboard-task-def"
                    "awslogs-region"        = "eu-west-2"
                    "awslogs-stream-prefix" = "ecs"
                }
            }
    },
  ])
}

resource "aws_security_group" "c14-price-slash-dashboard-sg" {
    name        = "c14-price-slash-dashboard-sg"
    description = "Security group for connecting to dashboard"
    vpc_id      = data.aws_vpc.c14-vpc.id

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port   = 8501
        to_port     = 8501
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }


}

resource "aws_ecs_service" "c14-price-slash-dashboard-service-tf" {
    name            = "c14-price-slash-dashboard-service-tf"
    cluster         = data.aws_ecs_cluster.c14-cluster.cluster_name
    task_definition = aws_ecs_task_definition.c14-price-slash-dashboard-task-def.arn
    desired_count   = 1
    launch_type     = "FARGATE" 
    
    network_configuration {
        subnets          = [data.aws_subnet.c14-subnet-1.id, data.aws_subnet.c14-subnet-2.id, data.aws_subnet.c14-subnet-3.id] 
        security_groups  = [aws_security_group.c14-price-slash-dashboard-sg.id] 
        assign_public_ip = true
    }
}
