import json
import pathlib
from pywebpush import webpush, WebPushException
from .models import PushDevice

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

def send_push_to_file(file_path: pathlib.Path, payload: dict) -> None:
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

def generate_payload(title: str, body: str, icon: str = None, image: str = None, tag: str = None, renotify: bool = False, requireInteraction: bool = False, navigate: str = None) -> dict:
    """
    Generate a payload for the push notification.
    :param title: The title of the notification.
    :param body: The body of the notification.
    :param icon: The icon of the notification (64x64).
    :param image: The Hero image of the notification.
    :param tag: Same tag will replace the previous notification.
    :param renotify: Will show the notification even if it is already shown due to tag.
    :param requireInteraction: Whether to require interaction or not.
    :param navigate: The URL to navigate to when the notification is clicked.
    :return: The payload for the push notification.
    """
    payload = {
        "title": title,
        "body": body,
        "icon": icon,
        "image": image,
        "tag": tag,
        "renotify": renotify,
        "requireInteraction": requireInteraction,
        "navigate": navigate
    }
    return {k: v for k, v in payload.items() if v not in [None, False, ""]}

def send_simple_notifications(title: str, message: str):
    """
    Send a simple notification to all clients in the `notification_clients` directory.
    """
    send_push_to_all_files(
        pathlib.Path("notification_clients"),
        generate_payload(
            title=title,
            body=message,
        )
    )