import boto3

session = boto3.Session(profile_name="lab")
ec2 = session.client("ec2", region_name="ap-northeast-2")

response = ec2.describe_regions()

print("리전 이름 목록")
for region in response["Regions"]:
    print(region["RegionName"])
