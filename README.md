# CaORE
Chaos and Order Reverse Engineered

## What is this?

A set of scripts/stubs/proxies to make possible running an original "Order & Chaos Online" iOS against a private "offline" server

## Prerequisites

- Already running private server compatible with version "1.0.3j"
- Decryped iOS IPA of OaC, version "1.0.3"
- Python3/Flask

## How to use?

Assuming that gameserver is already running on `192.1.168.78:7011` and your proxy device has IP `192.168.1.78`
All devices are in the same network.

TODO: remove hardcoded IPs from scripts

- Add following entry to `/etc/hosts` on iOS device `192.1.168.78 gllive.gameloft.com`
- Run following commands in separate terminals:

```
# for GLLive stub (after installing Flask)
cd app
. .venv/bin/activate
flask run --host=0.0.0.0 --port 80

# for lobby
python3 lobby.py

# for proxy
python3 proxy.py --source_host=0.0.0.0 --source_port=9998 --target_host=192.168.1.87 --target_port=7011
```

## How does it work?

TODO
