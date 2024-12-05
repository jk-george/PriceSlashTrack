provider "aws" {
  region = "eu-west-2"
}


data "aws_vpc" "VPC" {
  id = var.VPC_ID
}

data "aws_ecs_cluster" "ecs_cluster" {
  cluster_name = var.ECS_CLUSTER_NAME
}


resource "aws_ecr_repository" "ecr_for_etl" {
  name                 = var.ETL_ECR_NAME  
  image_tag_mutability = "MUTABLE"  
  image_scanning_configuration {
    scan_on_push = true
  }
  force_delete = true

  lifecycle {
    prevent_destroy = false
  }
}



# Task definition permissions 
resource "aws_iam_role" "ecs_role" {
  name               = "c14-priceslashers-ETL-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = ""
        Action    = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Effect    = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_container_registry_readonly" {
  role       = aws_iam_role.ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "ecs_full_access" {
  role       = aws_iam_role.ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs_full_access" {
  role       = aws_iam_role.ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}


# Task Definition 
resource "aws_ecs_task_definition" "etl-task-def" {
  family                   = "c14-priceslashers-ETL-taskdef"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_role.arn
  task_role_arn            = aws_iam_role.ecs_role.arn
  container_definitions    = jsonencode([
    {
      name      = var.ETL_ECR_NAME
      image     = format("%s:latest", aws_ecr_repository.ecr_for_etl.repository_url)
      essential = true
      cpu       = 256
      memory    = 512
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        },
        {
          containerPort = 443
          hostPort      = 443
        }
      ]
      environment = [
        {
          name  = "DB_HOST"
          value = var.DB_HOST
        },
        {
          name  = "DB_USER"
          value = var.DB_USER
        },
        {
          name  = "DB_PASSWORD"
          value = var.DB_PASSWORD
        },
        {
          name  = "DB_NAME"
          value = var.DB_NAME
        },
        {
          name  = "DB_PORT"
          value = var.DB_PORT
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/c14-priceslashers-ETL-task"
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}


# Scheduler permissions section

resource "aws_iam_role" "scheduler_ecs_role" {
  name = "c14-priceslashers-scheduler-ETL-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "scheduler.amazonaws.com" 
        }
        Effect = "Allow"
      }
    ]
  })
}



resource "aws_iam_policy" "scheduler_run_task_policy" {
  name        = "c14-priceslashers-scheduler-run-task-policy"
  description = "Allows ECS tasks to be run and pass roles"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecs:RunTask"
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_ecs_run_task_policy" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = aws_iam_policy.scheduler_run_task_policy.arn
}



resource "aws_iam_role_policy_attachment" "scheduler_ecs_role_policy" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"  
}



resource "aws_iam_role_policy_attachment" "scheduler_logs_policy" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess" 
}

resource "aws_iam_role_policy_attachment" "scheduler_container_registry_readonly" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "scheduler_vpc_access" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonVPCFullAccess"
}




resource "aws_scheduler_schedule_group" "c14-priceslashers-schedule-group" {
  name = "c14-priceslashers-schedule-group"
}

resource "aws_security_group" "task_exec_security_group"{
  name        = "c14-priceslashers-sg"
  description = "Allow inbound HTTPS traffic on port 443 from anywhere"
  vpc_id      = var.VPC_ID  

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  
    ipv6_cidr_blocks = ["::/0"]
  }
  ingress {
    from_port   = var.DB_PORT
    to_port     = var.DB_PORT
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port   = var.DB_PORT
    to_port     = var.DB_PORT
    protocol    = "tcp"  
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Scheduler for ETL script
resource "aws_scheduler_schedule" "priceslashers-ETL-scheduler" {
  name       = "c14-priceslashers-ETL-scheduler"
  group_name = aws_scheduler_schedule_group.c14-priceslashers-schedule-group.id

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(*/3 * ? * * *)"

  target {
    arn      = data.aws_ecs_cluster.ecs_cluster.arn
    role_arn = aws_iam_role.scheduler_ecs_role.arn


    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.etl-task-def.arn
      task_count = 1
      launch_type = "FARGATE"
      group = "c14-priceslashers-ETL-task"

      network_configuration {
      
        assign_public_ip    = true
        subnets             = var.SUBNET_IDS
        security_groups     = [aws_security_group.task_exec_security_group.id]
      }
    }
  }
}

