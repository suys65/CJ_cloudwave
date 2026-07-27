import boto3

session = boto3.Session(profile_name="lab")

ec2_client = session.client("ec2", region_name="ap-northeast-2")
s3_resource = session.resource("s3", region_name="ap-northeast-2")

print("ec2 client created")
print(ec2_client)

print("s3 resource created")
print(s3_resource)
