import boto3

session = boto3.Session(profile_name="lab")
ec2 = session.client("ec2", region_name="ap-northeast-2")

response = ec2.describe_instances()

for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        print(
            f"id={instance['InstanceId']}, "
            f"state={instance['State']['Name']}"
        )
