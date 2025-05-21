import json
import pathlib
from pywebpush import webpush, WebPushException
from models import PushDevice

def create_device_file(subscription_device: PushDevice) -> str:
    """
    Create a device file for the given subscription payload.
    :param config: The PushConfig object.
    :param subscription_device: The subscription payload.
    :return: The path to the device file.
    """
    device_file = f"{subscription_device.device_name}.json"
    with open(device_file, "w") as f:
        json.dump(subscription_device.to_json(), f, indent=4)
    return device_file

def send_push_notification(device: PushDevice, payload: dict) -> None:
    """
    Send a push notification to the given device.
    :param device: The PushDevice object.
    :param payload: The payload to send.
    """
    webpush(
        subscription_info=device.subscription.to_json(),
        data=json.dumps(payload),
        vapid_private_key=device.config.private_key,
        vapid_claims={
            "sub": device.config.subject_email
        }
    )

def send_push_to_file(file_path: str, payload: dict) -> None:
    """
    Send a push notification to the given device file.
    :param file_path: The path to the device file.
    :param payload: The payload to send.
    """
    with open(file_path, "r") as f:
        device = PushDevice.from_json(json.load(f))
        
    try:
        send_push_notification(device, payload)
    except WebPushException as ex:
        print(f"Failed to send push notification to {device.device_name}: {ex}")
        print("Response: ", ex.response)

def send_push_to_all_files(base_path: pathlib.Path, payload: dict) -> None:
    """
    Send a push notification to all devices.
    :param base_path: The path to the devices directory.
    :param payload: The payload to send.
    """
    for device_file in base_path.glob("*.json"):
        print(f"Sending push notification to {device_file}")

        send_push_to_file(device_file, payload)


