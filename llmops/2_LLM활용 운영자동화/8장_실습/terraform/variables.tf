variable "aws_region" {
  type    = string
  default = "ap-northeast-2"
}

variable "aws_profile" {
  type    = string
  default = "student"
}

variable "project_name" {
  type    = string
  default = "llmops"
}

variable "student_initial" {
  type    = string
  default = "kyt"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "allowed_http_cidr" {
  type    = string
  default = "0.0.0.0/0"
}

variable "app_port" {
  type    = number
  default = 8000
}

variable "health_check_path" {
  type    = string
  default = "/health"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "root_volume_size" {
  type    = number
  default = 8
}

variable "asg_min_size" {
  type    = number
  default = 1
}

variable "asg_desired_capacity" {
  type    = number
  default = 2
}

variable "asg_max_size" {
  type    = number
  default = 3
}

variable "enable_scaling_policy" {
  type    = bool
  default = true
}

variable "alarm_cpu_threshold" {
  type    = number
  default = 70
}
