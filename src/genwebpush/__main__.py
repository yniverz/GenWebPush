from importlib.resources import files
import argparse
import time
from flask import Flask, Response, request, abort, send_file
from models import PushConfig, PushDevice, SubKey, Subscription
from core import create_device_file, send_push_notification
from pywebpush import WebPushException

parser = argparse.ArgumentParser(description="Push notification server")
parser.add_argument("--mailto", type=str, required=True, help="The email address of the sender. (with or without 'mailto:')")
parser.add_argument("--public_key", type=str, help="The VAPID public key.")
parser.add_argument("--private_key", type=str, help="The VAPID private key.")
args = parser.parse_args()
config = PushConfig(
    subject_email=args.mailto,
    public_key=args.public_key,
    private_key=args.private_key
)

app = Flask(__name__)

@app.route("/")
def index():
    index_file = files("genwebpush.assets").joinpath("index.html")
    with open(index_file, "r") as f:
        content = f.read().replace("<--VAPID_PUBLIC_KEY-->", config.public_key)
    return Response(content, mimetype="text/html")

@app.route("/offline.html")
def offline():
    return send_file(files("genwebpush.assets").joinpath("offline.html"))

@app.route("/manifest.json")
def manifest():
    return send_file(files("genwebpush.assets").joinpath("manifest.json"))

@app.route("/sw.js")
def sw():
    return send_file(files("genwebpush.assets").joinpath("sw.js"))

@app.post("/subscribe")
def subscribe():
    """
    required fields in the payload:
    - device_name
    - endpoint
    - keys.p256dh
    - keys.auth
    """

    data = request.get_json()
    if not data or not all(k in data for k in ("device_name", "endpoint", "keys")):
        abort(400, "Invalid subscription payload")
    
    key = SubKey(
        p256dh=data["keys"]["p256dh"],
        auth=data["keys"]["auth"]
    )
    subscription = Subscription(
        endpoint=data["endpoint"],
        keys=key
    )
    device = PushDevice(
        device_name=data["device_name"],
        config=config,
        subscription=subscription
    )
    
    create_device_file(device)
    
    time.sleep(1)

    return ("OK" if push_test(device) else "ERROR", 204)

def push_test(device: PushDevice):
    payload = {
        "title": "Hello, world!",
        "body":  "Your Safari push worked!!"
    }
    
    try:
        send_push_notification(device, payload)
    except WebPushException as ex:
        print("WebPushException: ", ex)
        print("Response: ", ex.response)
        return False
    return True


def main():
    app.run(debug=False, host="0.0.0.0", port=5000, ssl_context="adhoc")

if __name__ == "__main__":
    main()