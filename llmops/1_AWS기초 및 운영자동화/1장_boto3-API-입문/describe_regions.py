import boto3

session = boto3.Session(profile_name="lab")
ec2 = session.client("ec2", region_name="ap-northeast-2")

response = ec2.describe_regions()

print("전체 응답 출력")
print(response)
