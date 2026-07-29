aws_region      = "ap-northeast-2"
aws_profile     = "admin"
project_name    = "llmops"
student_initial = "kyt"

vpc_cidr          = "10.0.0.0/16"
allowed_http_cidr = "0.0.0.0/0"

app_port          = 8000
health_check_path = "/health"

instance_type    = "t3.micro"
root_volume_size = 8

asg_min_size         = 1
asg_desired_capacity = 2
asg_max_size         = 3

enable_scaling_policy = true
alarm_cpu_threshold   = 70
