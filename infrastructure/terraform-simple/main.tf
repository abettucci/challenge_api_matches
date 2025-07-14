terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# DynamoDB
resource "aws_dynamodb_table" "item_pairs" {
  name           = "item_pairs"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name = "${var.project_name}-item-pairs-table"
  }
}

# ECR Repository
resource "aws_ecr_repository" "lambda" {
  name                 = "${var.project_name}-lambda"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-ecr-repo"
  }
}

# IAM Role para Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy para DynamoDB
resource "aws_iam_policy" "dynamodb_access" {
  name        = "${var.project_name}-dynamodb-access"
  description = "Policy for DynamoDB access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:DescribeTable"
        ]
        Resource = aws_dynamodb_table.item_pairs.arn
      }
    ]
  })
}

# IAM Policy para CloudWatch Logs
resource "aws_iam_policy" "lambda_logging" {
  name        = "${var.project_name}-lambda-logging"
  description = "IAM policy for logging from a lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach policies to role
resource "aws_iam_role_policy_attachment" "lambda_dynamodb" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

# Lambda Function (Container Image)
resource "aws_lambda_function" "api" {
  function_name = "${var.project_name}-api"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda.repository_url}:latest"
  timeout       = 30
  memory_size   = 1024

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.item_pairs.name
    }
  }

  tags = {
    Name = "${var.project_name}-lambda-function"
  }

  # Ignorar cambios en image_uri para permitir actualizaciones manuales
  lifecycle {
    ignore_changes = [image_uri]
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name        = "${var.project_name}-api"
  description = "API para gestión de ítems similares - Meli Challenge"
}

# API Gateway Resource - Health
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "health"
}

# API Gateway Method - Health GET
resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

# API Gateway Integration - Health
resource "aws_api_gateway_integration" "health_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_get.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api.invoke_arn
}

# API Gateway Resource - Items
resource "aws_api_gateway_resource" "items" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "items"
}

# API Gateway Resource - Items/Compare
resource "aws_api_gateway_resource" "items_compare" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.items.id
  path_part   = "compare"
}

# API Gateway Method - Items/Compare POST
resource "aws_api_gateway_method" "items_compare_post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.items_compare.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration - Items/Compare
resource "aws_api_gateway_integration" "items_compare_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.items_compare.id
  http_method = aws_api_gateway_method.items_compare_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api.invoke_arn
}

# API Gateway Resource - Items/Pairs
resource "aws_api_gateway_resource" "items_pairs" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.items.id
  path_part   = "pairs"
}

# API Gateway Method - Items/Pairs GET
resource "aws_api_gateway_method" "items_pairs_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.items_pairs.id
  http_method   = "GET"
  authorization = "NONE"
}

# API Gateway Method - Items/Pairs POST
resource "aws_api_gateway_method" "items_pairs_post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.items_pairs.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration - Items/Pairs GET
resource "aws_api_gateway_integration" "items_pairs_get_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.items_pairs.id
  http_method = aws_api_gateway_method.items_pairs_get.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api.invoke_arn
}

# API Gateway Integration - Items/Pairs POST
resource "aws_api_gateway_integration" "items_pairs_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.items_pairs.id
  http_method = aws_api_gateway_method.items_pairs_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api.invoke_arn
}

# API Gateway Resource - Items/Pairs/{pair_id}
resource "aws_api_gateway_resource" "items_pairs_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.items_pairs.id
  path_part   = "{pair_id}"
}

# API Gateway Method - Items/Pairs/{pair_id} GET
resource "aws_api_gateway_method" "items_pairs_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.items_pairs_id.id
  http_method   = "GET"
  authorization = "NONE"
}

# API Gateway Integration - Items/Pairs/{pair_id}
resource "aws_api_gateway_integration" "items_pairs_id_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.items_pairs_id.id
  http_method = aws_api_gateway_method.items_pairs_id_get.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api.invoke_arn
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
  
  # Ignorar cambios para evitar conflictos
  lifecycle {
    ignore_changes = [statement_id]
  }
}

# API Gateway Stage
resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.api.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = "prod"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "api" {
  depends_on = [
    aws_api_gateway_integration.health_integration,
    aws_api_gateway_integration.items_compare_integration,
    aws_api_gateway_integration.items_pairs_get_integration,
    aws_api_gateway_integration.items_pairs_post_integration,
    aws_api_gateway_integration.items_pairs_id_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.api.id
}

# Outputs
output "api_url" {
  description = "URL of the API"
  value       = "${aws_api_gateway_stage.prod.invoke_url}"
}

output "health_url" {
  description = "URL of the health endpoint"
  value       = "${aws_api_gateway_stage.prod.invoke_url}/health"
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.lambda.repository_url
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.item_pairs.name
} 