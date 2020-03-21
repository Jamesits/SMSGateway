import toml

user_config = {}
connector_ip_device_mapping = {}


def load_user_config(filename: str) -> None:
    global user_config, connector_ip_device_mapping
    user_config = toml.load(filename)

    # generate IP address => device block mapping
    if "device" in user_config:
        for device in user_config["device"]:
            if device["connector"] not in connector_ip_device_mapping:
                connector_ip_device_mapping[device["connector"]] = {}
            connector_ip_device_mapping[device["connector"]][device["ip"]] = device


def get_devices(connector):
    try:
        return connector_ip_device_mapping[connector]
    except KeyError:
        return {}


def get_device(connector, ip):
    try:
        return connector_ip_device_mapping[connector][ip]
    except KeyError:
        return None
