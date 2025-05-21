[![License: NCPUL](https://img.shields.io/badge/license-NCPUL-blue.svg)](./LICENSE.md)

# GenWebPush

*A minimal, zero-backend helper for Web Push notifications.*

GenWebPush spins up a one-file Flask server that:

* serves a progressive-web-app (PWA) shell with friendly, per-browser setup tips  
* generates VAPID keys on the fly (or accepts your own)  
* stores each subscription in a plain JSON file  
* offers straightforward helpers for sending Web Push messages to one device **or all of them** using said JSON files

---

## Features

| What you get |
|-----------------|
| **Automatic VAPID key generation** if none supplied |
| **PWA assets** (manifest, service-worker, offline page) for installable testing |
| **Browser-specific instructions** auto-expanded on load |
| **helpers** to send a notification to one file or an entire folder of devices |
| **Clean JSON device files** you can commit, inspect, or reuse elsewhere |

---

## Quick start

### 1. Install with pip

```bash
pip install genwebpush
```

### 2. Launch the local server

```bash
python -m genwebpush --mailto you@example.com
# optional if you want to use your own VAPID keys:
#   --public_key  VAPID_PUBLIC
#   --private_key VAPID_PRIVATE
```

The server listens on **[https://localhost:5000](https://localhost:5000)** using an ad-hoc cert so modern browsers allow push. Flask will also display your devices IP address if you want to set up notifications on a different device.

### 3. Subscribe a device

Open the URL in your browser/device, click through possible warnings due to adhoc generation of SSL cert, hit **“Got it — Activate Notifications”**, approve the permission prompt, and enter the device Name.
A JSON file with the set Name appears in the working directory.

### 4. Send yourself a push

```python
from pathlib import Path
from genwebpush.core import send_push_to_all_files

payload = {
    "title": "Hello, world!",
    "body":  "Your Safari push worked!!",
    # "navigate": "https://example.com"   # optional deep-link
}

send_push_to_all_files(Path("."), payload)
```

---

## Configuration options

| Flag / field            | Purpose                                     |
| ----------------------- | ------------------------------------------- |
| `--mailto you@host.tld` | **Required** – used as `sub` claim in VAPID |
| `--public_key`          | Re-use an existing VAPID public key         |
| `--private_key`         | Re-use an existing VAPID private key        |
| `device_name` (JS)      | Friendly name written to `<name>.json`      |

If you omit the VAPID keys, GenWebPush creates a fresh pair everytime it runs and injects the public key into the served HTML.

---

## Compatibility notes

* **Safari (macOS & iOS ≥ 17)**: Works out of the box thanks to the PWA install step.
* **Edge / Chrome / Firefox (desktop & mobile)**: Full support.

---

## License

This project is distributed under the **NCPU License** – see [`LICENSE.md`](https://github.com/yniverz/GenWebPush/blob/main/LICENSE.md) for details.