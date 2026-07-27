terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "ap-northeast-2"
  profile = "admin"
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_vpc" "this" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "llmops-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "llmops-public-subnet"
  }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "llmops-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = {
    Name = "llmops-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "this" {
  name        = "llmops-sg"
  description = "SSM-managed instances, no inbound"
  vpc_id      = aws_vpc.this.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "llmops-sg"
  }
}

resource "aws_iam_role" "ssm" {
  name = "llmops-ssm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ssm.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ssm" {
  name = "llmops-ssm-profile"
  role = aws_iam_role.ssm.name
}

resource "aws_instance" "this" {
  count = 2

  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.this.id]
  iam_instance_profile   = aws_iam_instance_profile.ssm.name

  tags = {
    Name = "llmops-test-${count.index + 1}"
  }
}

output "vpc_id" {
  value = aws_vpc.this.id
}

output "public_subnet_id" {
  value = aws_subnet.public.id
}

output "ec2_public_ips" {
  value = aws_instance.this[*].public_ip
}

output "ssm_start_session_commands" {
  value = [
    for i in aws_instance.this :
    "aws ssm start-session --target ${i.id} --region ap-northeast-2 --profile admin"
  ]
}

resource "aws_s3_bucket" "llm" {
  bucket = "kyt-llm-bucket-892880329905"

  tags = {
    Name = "kyt-llm-bucket"
  }
}

resource "aws_s3_bucket_public_access_block" "llm" {
  bucket = aws_s3_bucket.llm.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "llm_public_read" {
  bucket = aws_s3_bucket.llm.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicReadGetObject"
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.llm.arn}/*"
    }]
  })

  depends_on = [aws_s3_bucket_public_access_block.llm]
}

resource "aws_s3_object" "license" {
  bucket       = aws_s3_bucket.llm.id
  key          = "LICENSE.txt"
  content      = file("${path.module}/LICENSE.txt")
  content_type = "text/plain"
}

output "s3_bucket_name" {
  value = aws_s3_bucket.llm.bucket
}

output "s3_license_url" {
  value = "https://${aws_s3_bucket.llm.bucket}.s3.ap-northeast-2.amazonaws.com/${aws_s3_object.license.key}"
}
