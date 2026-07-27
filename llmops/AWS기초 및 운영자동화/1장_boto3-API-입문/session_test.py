import boto3

session = boto3.Session(
    profile_name="lab",
    region_name="ap-northeast-2",
)

ec2_client = session.client("ec2")
s3_client = session.client("s3")

print("Session 생성 완료")
print(session)

print("\nEC2 Client 생성 완료")
print(ec2_client)

print("\nS3 Client 생성 완료")
print(s3_client)
