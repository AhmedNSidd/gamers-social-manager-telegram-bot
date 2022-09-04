# *****************************************************************************
# Initial Setup (Providers and .env variables)
# *****************************************************************************

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 4.16"
    }
    github = {
      source  = "integrations/github"
      version = "~> 4.0"
    }
    mongodbatlas = {
      source = "mongodb/mongodbatlas"
      version = "1.4.3"
    }
  }
  required_version = ">= 1.2.0"
}

locals {
  envs = { for tuple in regexall("(.*)=(.*)", file("../.env")) : tuple[0] => sensitive(tuple[1]) }
}

provider "aws" {
  region = "eu-central-1"
  access_key = var.AWS_ACCESS_KEY
  secret_key = var.AWS_SECRET_KEY
}

# Configure the GitHub Provider
provider "github" {
  token = var.GITHUB_TOKEN
}

provider "mongodbatlas" {
  public_key = var.MONGODBATLAS_PUBLIC_KEY
  private_key = var.MONGODBATLAS_PRIVATE_KEY
}

resource "github_actions_secret" "aws_access_key_id" {
  repository       = var.GITHUB_REPO_NAME
  secret_name      = "AWS_ACCESS_KEY_ID"
  plaintext_value  = var.AWS_ACCESS_KEY
}

resource "github_actions_secret" "aws_secret_access_key" {
  repository       = var.GITHUB_REPO_NAME
  secret_name      = "AWS_SECRET_ACCESS_KEY"
  plaintext_value  = var.AWS_SECRET_KEY
}

resource "github_actions_secret" "dockerhub_credentials_username" {
  repository       = var.GITHUB_REPO_NAME
  secret_name      = "DOCKERHUB_CREDENTIALS_USR"
  plaintext_value  = var.DOCKERHUB_CREDENTIALS_USR
}

resource "github_actions_secret" "dockerhub_credentials_password" {
  repository       = var.GITHUB_REPO_NAME
  secret_name      = "DOCKERHUB_CREDENTIALS_PSW"
  plaintext_value  = var.DOCKERHUB_CREDENTIALS_PSW
}

# *****************************************************************************
# Set up MongoDB Atlas infrastructure (db + db-user)
# *****************************************************************************

# Create the mongodbatlas instance
resource "mongodbatlas_serverless_instance" "gsm-db" {
  project_id   = var.MONGODBATLAS_PROJECT_ID
  name         = var.MONGODBATLAS_INSTANCE_NAME

  provider_settings_backing_provider_name = "AWS"
  provider_settings_provider_name = "SERVERLESS"
  provider_settings_region_name = "EU_WEST_1"
}

# Generate a random password for the mongodbatlas user
resource "random_password" "mongodbatlas_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Create the db user for the created mongodbatlas instance
resource "mongodbatlas_database_user" "gsm-db-user" {
  username = var.MONGODBATLAS_DB_USER_USERNAME
  password = "${random_password.mongodbatlas_password.result}"
  project_id = var.MONGODBATLAS_PROJECT_ID
  auth_database_name = "admin"

  roles {
    role_name     = "readWrite"
    database_name = "gsm"
  }
}

resource "null_resource" "provision_prod_db" {
  depends_on = [
    mongodbatlas_database_user.gsm-db-user
  ]

  provisioner "local-exec" {
    environment = {
      GSM_DB_URL_WITHOUT_USERNAME_AND_PASSWORD = "${mongodbatlas_serverless_instance.gsm-db.connection_strings_standard_srv}"
      GSM_DB_USERNAME = "${var.MONGODBATLAS_DB_USER_USERNAME}"
      GSM_DB_PASSWORD = nonsensitive("${random_password.mongodbatlas_password.result}")
      PSN_NPSSO = "${var.PSN_NPSSO}"
      XBOX_CLIENT_ID = "${var.XBOX_CLIENT_ID}"
      XBOX_CLIENT_SECRET = "${var.XBOX_CLIENT_SECRET}"
     }
    command = "/bin/bash provision_db.sh"
  }
}

# *****************************************************************************
# Set up AWS infrastructure
# *****************************************************************************

# resource "aws_ecr_repository" "gsm-repo" {
#   name = "gsm-repo"
# }


resource "aws_kms_key" "gsm-key" {
}

resource "aws_cloudwatch_log_group" "gsm-logs" {
  name = "gsm-logs"
}

resource "aws_ecs_cluster" "gsm" {
  name = "gsm"

  configuration {
    execute_command_configuration {
      kms_key_id = aws_kms_key.gsm-key.arn
      logging = "OVERRIDE"

      log_configuration {
        cloud_watch_encryption_enabled = true
        cloud_watch_log_group_name = aws_cloudwatch_log_group.gsm-logs.name
      }
    }
  }
}

resource "aws_ecs_task_definition" "gsm-task-definition" {
  family = "gsm-task-definition"
  container_definitions = jsonencode([
    {
      "name" : "gsm-bot",
      "image" : "jesuisahmedn/gsm-bot:latest",
      "essential" : true,
      "environment" : [
        { "name" : "GUB_BOT_TOKEN", "value" : var.GUB_TG_BOT_TOKEN },
        { "name" : "GSM_DB_URL_WITHOUT_USERNAME_AND_PASSWORD", "value" : "${mongodbatlas_serverless_instance.gsm-db.connection_strings_standard_srv}" },
        { "name" : "GSM_DB_USERNAME", "value" : var.MONGODBATLAS_DB_USER_USERNAME },
        { "name" : "GSM_DB_PASSWORD", "value" : "${random_password.mongodbatlas_password.result}" },
      ],
      "portMappings" : [
        {
          "containerPort" : 80,
          "hostPort" : 80
        }
      ],
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-group" : "gsm-logs",
          "awslogs-region" : "eu-central-1",
          "awslogs-stream-prefix" : "bot"
        }
      },
      "memory" : 512,
      "cpu" : 100
    }
  ])
  requires_compatibilities = [ "FARGATE" ]
  network_mode = "awsvpc"
  memory = 512
  cpu = 256
  execution_role_arn = "${aws_iam_role.ecs-task-execution-role.arn}"
}

resource "aws_iam_role" "ecs-task-execution-role" {
  name = "ecs-task-execution-role"
  assume_role_policy = "${data.aws_iam_policy_document.assume_role_policy.json}"
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecs-task-execution-role-policy" {
  role = "${aws_iam_role.ecs-task-execution-role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Creating a security group for the ECS service
resource "aws_security_group" "service_security_group" {
  name        = "example-task-security-group"
  vpc_id      = aws_default_vpc.default_vpc.id

  ingress {
    protocol        = "tcp"
    from_port       = 80 
    to_port         = 80
    security_groups = [aws_security_group.load_balancer_security_group.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_service" "gsm-service" {
  name = "gsm-service"
  cluster = "${aws_ecs_cluster.gsm.id}"
  task_definition = "${aws_ecs_task_definition.gsm-task-definition.arn}"
  launch_type = "FARGATE"
  desired_count = 1

  load_balancer {
    target_group_arn = aws_lb_target_group.target_group.arn # Referencing our target group
    container_name   = "gsm-bot"
    container_port   = 80 # Specifying the container port
  }

  network_configuration {
    security_groups = [ aws_security_group.service_security_group.id ]
    subnets = ["${aws_default_subnet.default_subnet_a.id}", "${aws_default_subnet.default_subnet_b.id}", "${aws_default_subnet.default_subnet_c.id}"]
    assign_public_ip = true
  }
}

resource "aws_default_vpc" "default_vpc" {
}

resource "aws_default_subnet" "default_subnet_a" {
  availability_zone = "eu-central-1a"
}

resource "aws_default_subnet" "default_subnet_b" {
  availability_zone = "eu-central-1b"
}

resource "aws_default_subnet" "default_subnet_c" {
  availability_zone = "eu-central-1c"
}

resource "aws_alb" "application_load_balancer" {
  name               = "test-lb-tf" # Naming our load balancer
  load_balancer_type = "application"
  subnets = [ # Referencing the default subnets
    "${aws_default_subnet.default_subnet_a.id}",
    "${aws_default_subnet.default_subnet_b.id}",
    "${aws_default_subnet.default_subnet_c.id}"
  ]
  # Referencing the security group
  security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
}

# Creating a security group for the load balancer:
resource "aws_security_group" "load_balancer_security_group" {
  ingress {
    from_port   = 443 # Allowing traffic in from port 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allowing traffic in from all sources
  }

  egress {
    from_port   = 0 # Allowing any incoming port
    to_port     = 0 # Allowing any outgoing port
    protocol    = "-1" # Allowing any outgoing protocol 
    cidr_blocks = ["0.0.0.0/0"] # Allowing traffic out to all IP addresses
  }
}

resource "aws_lb_target_group" "target_group" {
  name        = "target-group"
  port        = 80 # The port the bot is exposed on
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = "${aws_default_vpc.default_vpc.id}" # Referencing the default VPC
  health_check {
    matcher = "405"
    path = "/${var.GUB_TG_BOT_TOKEN}"
  }
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = "${aws_alb.application_load_balancer.arn}" # Referencing our load balancer
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = aws_acm_certificate_validation.cert.certificate_arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group.arn # Referencing our tagrte group
  }
}

# # This data source looks up the public DNS zone
data "aws_route53_zone" "public" {
  name         = "gamersutilitybot.com"
  private_zone = false
}

# This creates an SSL certificate
resource "aws_acm_certificate" "myapp" {
  domain_name       = aws_route53_record.myapp.fqdn
  validation_method = "DNS"
  lifecycle {
    create_before_destroy = true
  }
}

# # This is a DNS record for the ACM certificate validation to prove we own the domain
# #
# # This example, we make an assumption that the certificate is for a single domain name so can just use the first value of the
# # domain_validation_options.  It allows the terraform to apply without having to be targeted.
# # This is somewhat less complex than the example at https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/acm_certificate_validation
# # - that above example, won't apply without targeting

resource "aws_route53_record" "cert_validation" {
  allow_overwrite = true
  name            = tolist(aws_acm_certificate.myapp.domain_validation_options)[0].resource_record_name
  records         = [ tolist(aws_acm_certificate.myapp.domain_validation_options)[0].resource_record_value ]
  type            = tolist(aws_acm_certificate.myapp.domain_validation_options)[0].resource_record_type
  zone_id  = data.aws_route53_zone.public.id
  ttl      = 60
}

# This tells terraform to cause the route53 validation to happen
resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.myapp.arn
  validation_record_fqdns = [ aws_route53_record.cert_validation.fqdn ]
}

# # Standard route53 DNS record for "myapp" pointing to an ALB
resource "aws_route53_record" "myapp" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = "${data.aws_route53_zone.public.name}"
  type    = "A"
  alias {
    name                   = aws_alb.application_load_balancer.dns_name
    zone_id                = aws_alb.application_load_balancer.zone_id
    evaluate_target_health = false
  }
}
