import boto3

try:
    session = boto3.Session(profile_name="lab")
    ec2 = session.client("ec2", region_name="ap-northeast-2")

    response = ec2.describe_regions()

    for region in response["Regions"]:
        print(region["RegionName"])

except Exception as e:
    print("리전 조회 실패")
    print(f"오류 내용:{e}")
