# ECR Repository

resource "aws_ecr_repository" "c14-price-slash-subscription-checker" {
  name = "c14-price-slash-subscription-checker"
}

# IAM role for Lambda function

resource "aws_iam_role" "c14-price-slash-lambda-execution-role" {
  name = "c14-price-slash-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attaching policies to the Lambda IAM role

resource "aws_iam_policy_attachment" "c14-price-slash-lambda-policy-attachment" {
  name       = "c14-price-slash-lambda-policy-attachment"
  roles      = [aws_iam_role.c14-price-slash-lambda-execution-role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function for Subscription Checker
resource "aws_lambda_function" "c14-price-slash-subscription-checker" {
  function_name = "c14-price-slash-subscription-checker"
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-price-slash-subscription-checker-repo:latest"
  role          = aws_iam_role.c14-price-slash-lambda-execution-role.arn
  package_type  = "Image"
  timeout       = 900
  memory_size   = 512

  environment {
    variables = {
      DB_HOST     = aws_db_instance.c14-price_slash_db.endpoint
      DB_NAME     = var.DB_NAME
      DB_USER     = var.DB_USERNAME
      DB_PASSWORD = var.DB_PASSWORD
    }
  }

  image_config {
    command = ["lambda_function.lambda_handler"] # This will need to be changed later once lambda code has been written
  }
}

# EventBridge Rule to trigger Lambda every 24 hours

resource "aws_cloudwatch_event_rule" "c14-price-slash-subscription-checker-schedule" {
  name        = "c14-price-slash-subscription-checker-schedule"
  description = "EventBridge rule to trigger the subscription checker Lambda daily"
  schedule_expression = "cron(0 0 * * ? *)"
}

# EventBridge Target to invoke the Lambda

resource "aws_cloudwatch_event_target" "c14-price-slash-subscription-checker-target" {
  rule      = aws_cloudwatch_event_rule.c14-price-slash-subscription-checker-schedule.name
  target_id = "c14-price-slash-subscription-checker"
  arn       = aws_lambda_function.c14-price-slash-subscription-checker.arn
}

# Lambda permission to allow invocation by EventBridge

resource "aws_lambda_permission" "allow-eventbridge-c14-price-slash-subscription-checker" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.c14-price-slash-subscription-checker.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.c14-price-slash-subscription-checker-schedule.arn
}