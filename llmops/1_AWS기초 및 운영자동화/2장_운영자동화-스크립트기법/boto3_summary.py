import boto3

def get_name_tag(instance):
    tags = instance.get("Tags", [])

    for tag in tags:
        if tag["Key"] == "Name":
            return tag["Value"]

    return "NoName"

def print_instances():
    session = boto3.Session(profile_name="lab")
    ec2 = session.client("ec2", region_name="ap-northeast-2")

    response = ec2.describe_instances()

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            state = instance["State"]["Name"]
            name = get_name_tag(instance)

            print(f"id={instance_id}, name={name}, state={state}")

try:
    print_instances()
except Exception as e:
    print("EC2 조회 중 오류 발생")
    print(f"오류 내용:{e}")
