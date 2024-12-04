provider "aws" {
  region = "eu-central-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "main-vpc"
  }
}

# Subnet 'Public'
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "eu-central-1a"
  tags = {
    Name = "public-subnet"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "main-gateway"
  }
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  tags = {
    Name = "public-route-table"
  }
}

# Associate Route Table
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "web" {
  vpc_id = aws_vpc.main.id
  name   = "web-sg"
  ingress {
      description      = "SSH Access"
      from_port        = 22
      to_port          = 22
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
    }
  ingress {
      description      = "HTTP Access"
      from_port        = 80
      to_port          = 80
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
    }
  egress {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
  tags = {
    Name = "web-security-group"
  }
}

# Generate an RSA key pair
resource "tls_private_key" "ec2_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

# Use the generated public key in AWS
resource "aws_key_pair" "ec2_key" {
  key_name   = "terraform_key"
  public_key = tls_private_key.ec2_key.public_key_openssh
}

# Save the private key locally
resource "local_file" "private_key" {
  content  = tls_private_key.ec2_key.private_key_pem
  filename = "${pathexpand("~/.ssh/terraform_key.pem")}"
}

# Ensure permissions on the private key are secure
resource "null_resource" "secure_key_permissions" {
  triggers = {
    key_saved = local_file.private_key.content
  }

  provisioner "local-exec" {
    command = "chmod 600 ~/.ssh/terraform_key.pem"
  }
}

# EC2 Instance
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.public.id
  security_groups = [aws_security_group.web.id]
  key_name = aws_key_pair.ec2_key.key_name

  tags = {
    Name = basename(path.cwd)
  }
}
# Add a sleep resource to wait for the instance to be ready for SSH connections
resource "time_sleep" "wait_for_instance" {
  depends_on = [aws_instance.web]
  create_duration = "30s"  # Adjust the time as needed
}

# Use the local-exec provisioner, with a dependency on the time_sleep resource
resource "null_resource" "run_ansible_playbook" {
  depends_on = [time_sleep.wait_for_instance]

  provisioner "local-exec" {
    command = <<-EOT
      ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_SSH_ARGS='-o IdentitiesOnly=yes' \
      ansible-playbook -i "${aws_instance.web.public_ip}," -u ubuntu \
      --private-key="${var.ssh_private_key_path}" "${var.ansible_playbook_path}"
    EOT
  }
}

# Variables
variable "ssh_private_key_path" {
  description = "Path to the SSH private key used for Ansible"
  default     = "~/.ssh/terraform_key.pem"
}

variable "ansible_playbook_path" {
  description = "Path to the Ansible playbook"
  default     = "./setup_ec2.yml"  # Replace with the actual playbook path
}

