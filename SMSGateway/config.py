import toml

user_config = {}
ip_device_mapping = {}

def load_user_config(filename: str) -> None:
    global user_config, ip_device_mapping
    user_config = toml.load(filename)

    # generate IP address => device block mapping
    if "device" in user_config:
        for device in user_config["device"]:
            ip_device_mapping[device["ip"]] = device
