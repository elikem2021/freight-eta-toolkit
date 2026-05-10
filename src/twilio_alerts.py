"""
SMS alerts for freight ETA events. Wraps Twilio's REST API directly to keep
the dependency surface small.

Three alert templates:
  - receiver_eta_one_hour: text the consignee when the truck is ~60 min out
  - broker_truck_late: text the broker when delta exceeds threshold
  - broker_truck_stalled: text the broker when truck stops > 2hr off-route
"""
from __future__ import annotations
import os
import requests


def _twilio_post(account_sid: str, auth_token: str, from_: str, to: str, body: str) -> dict:
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    r = requests.post(
        url,
        auth=(account_sid, auth_token),
        data={"From": from_, "To": to, "Body": body},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def receiver_eta_one_hour(to: str, load_id: str, eta_local: str,
                          carrier_name: str, driver_name: str | None = None) -> dict:
    body = (
        f"Heads up: load {load_id} from {carrier_name} is approximately 1 hour out, "
        f"ETA {eta_local}."
    )
    if driver_name:
        body += f" Driver: {driver_name}."
    return _send(to, body)


def broker_truck_late(to: str, load_id: str, delta_min: int, last_location: str) -> dict:
    body = (
        f"⚠️ Load {load_id} is running {delta_min} min late. "
        f"Last GPS: {last_location}. Consider notifying receiver."
    )
    return _send(to, body)


def broker_truck_stalled(to: str, load_id: str, stalled_for_min: int, location: str) -> dict:
    body = (
        f"🛑 Load {load_id} has been stationary for {stalled_for_min} min off-route at {location}. "
        f"Recommend checking in with driver."
    )
    return _send(to, body)


def _send(to: str, body: str) -> dict:
    return _twilio_post(
        account_sid=os.environ["TWILIO_ACCOUNT_SID"],
        auth_token=os.environ["TWILIO_AUTH_TOKEN"],
        from_=os.environ["TWILIO_FROM_NUMBER"],
        to=to,
        body=body,
    )
