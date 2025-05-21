import base64
from dataclasses import dataclass
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from py_vapid import Vapid01

@dataclass
class PushConfig:
    subject_email: str
    public_key: str
    private_key: str
    
    def __init__(self, subject_email: str, public_key: str = None, private_key: str = None):
        """
        :param subject_email: The email address of the sender. (with or without "mailto:")
        :param public_key: The VAPID public key.
        :param private_key: The VAPID private key.
        
        If public_key or private_key are not provided, they will both be generated.
        """

        self.subject_email = subject_email if subject_email.startswith("mailto:") else "mailto:" + subject_email
        self.public_key = public_key
        self.private_key = private_key

        if not self.public_key or not self.private_key:
            vapid = Vapid01()
            vapid.generate_keys()

            self.public_key = self.vapid_public_key_b64url(vapid.private_key)
            self.private_key = self.vapid_private_key_b64url(vapid.private_key)

    def vapid_public_key_b64url(self, priv: "ec.EllipticCurvePrivateKey") -> str:
        raw_bytes = priv.public_key().public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        return base64.urlsafe_b64encode(raw_bytes).rstrip(b"=").decode()
    
    def vapid_private_key_b64url(self, priv: "ec.EllipticCurvePrivateKey") -> str:
        # 32-byte big-endian scalar (the secret number d)
        d_bytes = priv.private_numbers().private_value.to_bytes(32, 'big')
        return base64.urlsafe_b64encode(d_bytes).rstrip(b"=").decode()
            

@dataclass
class SubKey:
    p256dh: str
    auth: str

    def to_json(self) -> dict:
        """
        Convert the SubKey object to a JSON payload.
        :return: The JSON payload.
        """
        return {
            "p256dh": self.p256dh,
            "auth": self.auth
        }

@dataclass
class Subscription:
    endpoint: str
    keys: SubKey

    def to_json(self) -> dict:
        """
        Convert the Subscription object to a JSON payload.
        :return: The JSON payload.
        """
        return {
            "endpoint": self.endpoint,
            "keys": self.keys.to_json()
        }

@dataclass
class PushDevice:
    device_name: str
    config: PushConfig
    subscription: Subscription

    def from_json(data: dict) -> "PushDevice":
        """
        Create a PushDevice object from a JSON payload.
        :param data: The JSON payload.
        :return: The PushDevice object.
        """
        return PushDevice(
            device_name=data["device_name"],
            config=PushConfig(
                subject_email=data["config"]["subject_email"],
                public_key=data["config"]["public_key"],
                private_key=data["config"]["private_key"]
            ),
            subscription=Subscription(
                endpoint=data["subscription"]["endpoint"],
                keys=SubKey(
                    p256dh=data["subscription"]["keys"]["p256dh"],
                    auth=data["subscription"]["keys"]["auth"]
                )
            )
        )

    def to_json(self) -> dict:
        """
        Convert the PushDevice object to a JSON payload.
        :return: The JSON payload.
        """
        return {
            "device_name": self.device_name,
            "config": {
                "subject_email": self.config.subject_email,
                "public_key": self.config.public_key,
                "private_key": self.config.private_key
            },
            "subscription": {
                "endpoint": self.subscription.endpoint,
                "keys": {
                    "p256dh": self.subscription.keys.p256dh,
                    "auth": self.subscription.keys.auth
                }
            }
        }
