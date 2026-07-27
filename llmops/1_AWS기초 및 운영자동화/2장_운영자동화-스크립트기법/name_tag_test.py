def get_name_tag(instance):
    tags = instance.get("Tags", [])

    for tag in tags:
        if tag["Key"] == "Name":
            return tag["Value"]

    return "NoName"

sample_instance = {
    "InstanceId": "i-1111",
    "State": {"Name": "running"},
    "Tags": [
        {"Key": "Name", "Value": "web-1"},
        {"Key": "Env", "Value": "dev"}
    ]
}

print(get_name_tag(sample_instance))
