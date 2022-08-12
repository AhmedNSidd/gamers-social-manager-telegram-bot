# *****************************************************************************
# Initial Setup (Providers and .env variables)
# *****************************************************************************

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 4.16"
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

# Set up the mongodbatlas provider and get credentials from our variables file
provider "mongodbatlas" {
  public_key = var.MONGODBATLAS_PUBLIC_KEY
  private_key = var.MONGODBATLAS_PRIVATE_KEY
}

provider "aws" {
  region = "eu-central-1"
  access_key = var.AWS_ACCESS_KEY
  secret_key = var.AWS_SECRET_KEY
}

# *****************************************************************************
# Create an EC2 instance with a Jenkins server running on it
# *****************************************************************************

# First define a security group resource that will allow traffic to the Jenkins
# server on port 8080 and ssh access on port 22
resource "aws_security_group" "web_traffic" {
  name = "web_traffic"
  description = "inbound ports for ssh and standard http and everything outbound"

  ingress {
    from_port = 8080
    to_port = 8080
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    "Name" = "gsm-jenkins-sg"
  }
}

# Set up a data block to find the lastest AMI from Amazon that we want to use
# for your EC2 instance

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
  }
}

# Create an EC2 instance and provision the instance
resource "aws_instance" "gsm-jenkins" {
  # ami = "ami-02058f44341e7f54e"
  ami = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"
  security_groups = [aws_security_group.web_traffic.name]
  key_name = "gsm-jenkins-ec2-key-pair"

  provisioner "remote-exec" {
    inline  = [
      # Install Jenkins and its dependencies
      "sudo apt update",
      "sudo apt-get update",
      "sudo apt install -y awscli",
      "sudo apt-get install -y openjdk-11-jdk",
      "curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null",
      "echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null",
      "sudo apt-get update",
      "sudo apt-get install -y jenkins apt-transport-https ca-certificates curl gnupg lsb-release",
      # Install Docker
      "sudo mkdir -p /etc/apt/keyrings",
      "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
      "echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null",
      "sudo apt-get update",
      "sudo apt-get install -y docker-ce docker-ce-cli containerd.io",
      # Set proper permissions for docker & jenkins so docker can be run on jenkins server
      "sudo usermod -aG docker ubuntu",
      "sudo usermod -aG docker jenkins",
      "sudo service jenkins restart", # Restart the jenkins server so new permissions take effect
      # Create profile configuration file with aws credentials to configure aws-cli
      "printf '[default]\naws_access_key_id=${var.AWS_ACCESS_KEY}\naws_secret_access_key=${var.AWS_SECRET_KEY}\nregion=eu-central-1' > ~/.aws/config",
      "printf '[default]\naws_access_key_id=${var.AWS_ACCESS_KEY}\naws_secret_access_key=${var.AWS_SECRET_KEY}\nregion=eu-central-1' > ~/.aws/credentials",

      # "sudo yum update –y",
      # "sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo",
      # "sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io.key",
      # "sudo amazon-linux-extras install epel -y",
      # "sudo amazon-linux-extras install java-openjdk11 -y",
      # "sudo yum upgrade -y",
      # "sudo yum install -y jenkins git yum-utils",
      # "sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
      # "sudo yum install docker-ce docker-ce-cli containerd.io",
      # "sudo groupadd docker",
      # "sudo usermod -aG docker ubuntu",
      # "sudo usermod -aG docker jenkins",
      # "sudo systemctl daemon-reload",
      # "sudo systemctl start jenkins",
    ]
  }

  connection {
    type = "ssh"
    host = self.public_ip
    user = "ubuntu"
    private_key = file("~/.ssh/gsm-jenkins-ec2-key-pair.pem")
  }

  tags = {
    "Name" = "gsm-jenkins-instance"
  }
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
        "name": "gsm-bot",
        "image": "jesuisahmedn/gsm-bot",
        "essential": true,
        "environment": [
          {"name": "GSM_TG_BOT_TOKEN", "value": local.envs["GSM_TG_BOT_TOKEN"]},
          {"name": "XBOX_CLIENT_SECRET_EXPIRY_DATE", "value": local.envs["XBOX_CLIENT_SECRET_EXPIRY_DATE"]}
        ],
        "portMappings": [
          {
            "containerPort": 8443,
            "hostPort": 8443
          }
        ],
        "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "gsm-logs",
            "awslogs-region": "eu-central-1",
            "awslogs-stream-prefix": "bot"
          }
        },
        "memory": 512,
        "cpu": 100
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

resource "aws_ecs_service" "gsm-service" {
  name = "gsm-service"
  cluster = "${aws_ecs_cluster.gsm.id}"
  task_definition = "${aws_ecs_task_definition.gsm-task-definition.arn}"
  launch_type = "FARGATE"
  desired_count = 1

  load_balancer {
    target_group_arn = "${aws_lb_target_group.target_group.arn}" # Referencing our target group
    container_name   = "gsm-bot"
    container_port   = 8443 # Specifying the container port
  }

  network_configuration {
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
    from_port   = 80 # Allowing traffic in from port 80
    to_port     = 80
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
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = "${aws_default_vpc.default_vpc.id}" # Referencing the default VPC
  health_check {
    matcher = "200,301,302"
    path = "/"
  }
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = "${aws_alb.application_load_balancer.arn}" # Referencing our load balancer
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = "${aws_lb_target_group.target_group.arn}" # Referencing our tagrte group
  }
}