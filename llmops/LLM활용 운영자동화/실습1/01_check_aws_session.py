from aws_clients import session, sts_client

identity = sts_client.get_caller_identity()

print("=" * 80)
print("AWS 인증 정보")
print("=" * 80)
print("Account:", identity["Account"])
print("Arn:", identity["Arn"])
print("UserId:", identity["UserId"])
print("Region:", session.region_name)
