[![Maintained by Avalux](https://img.shields.io/badge/Maintained%20by-Avalux.io-3b82f6?style=flat-square)](https://avalux.io)

# Freight ETA Toolkit

> Open-source utilities for freight brokers and 3PLs to build their own driver-tracking and shipper-ETA dashboards on top of Geotab, Samsara, and Motive APIs. Stop the phone-tag. Built and maintained by [Avalux](https://avalux.io) — an AI automation agency for SMB freight, e-commerce, and home services.

## Why this exists

Most small and mid-size freight brokers running 20–50 loads per day still operate the same way they did fifteen years ago: a dispatcher on the phone, texting drivers for ETAs, then relaying those ETAs to receivers. When a truck is late, the broker finds out *from the receiver*, not the driver.

Enterprise platforms like Project44 and FourKites solve this — but they price for $50M+ shippers, not for SMB brokerage. There is no vendor-neutral, owner-operated way for a small brokerage to pull live truck location, geofence pickups and drops, and auto-text receivers when a truck is one hour out.

This toolkit fills that gap. It is a starter codebase, not a SaaS product. You host it. You own the data. You pay only for the underlying telematics subscriptions you already have with your carriers.

## What's in the box

```
src/
  geotab_client.py       Real-time vehicle GPS pull from Geotab MyGeotab API
  samsara_client.py      Vehicle locations + odometer from Samsara fleet API
  motive_client.py       (formerly KeepTruckin) vehicle stats via Motive API
  geofence.py            Haversine + polygon-in/out helpers for pickup/drop zones
  twilio_alerts.py       SMS templates for receiver-out, broker-stuck, late-delta
docs/
  setup.md               How to plug in your carrier telematics credentials
  geofencing.md          How geofencing math works in plain English
  edi214.md              How to map geofence events to EDI 214 status codes
examples/
  three_loads_demo.py    End-to-end demo: 3 fake loads, 3 carriers, live dashboard
```

## Who this is for

- **Small freight brokerages** running 10–200 loads/day on telematics-equipped carriers
- **3PLs** that already pay for Geotab, Samsara, or Motive on their own fleet but lack a unified visibility layer
- **Logistics ops engineers** building internal tooling
- **Owner-operators** who want full data ownership instead of paying enterprise SaaS

This is *not* for shippers without their own carrier relationships, or for brokerages routing exclusively through a single TMS that already includes visibility (in which case use that TMS's native module).

## Quick start

```bash
git clone https://github.com/elikem2021/freight-eta-toolkit
cd freight-eta-toolkit
cp .env.example .env             # add your Geotab/Samsara/Motive credentials
pip install -r requirements.txt
python examples/three_loads_demo.py
```

You'll see three simulated loads moving through pickup/drop geofences with auto-text alerts firing.

## Supported telematics platforms

| Platform                  | API type             | Required credentials                | Status |
|---------------------------|----------------------|-------------------------------------|--------|
| Geotab MyGeotab           | REST + custom        | username, password, database        | ✅ Stable |
| Samsara                   | REST                 | API token                           | ✅ Stable |
| Motive (KeepTruckin)      | REST                 | API key                             | ✅ Stable |
| Verizon Connect Reveal    | REST                 | client_id, client_secret            | 🟡 Roadmap |
| Fleet Complete            | SOAP                 | username, password                  | 🟡 Roadmap |
| ELD-only carriers (PTI)   | EDI 214              | EDI inbox                           | 🟡 Roadmap |

PRs welcome for additional platforms.

## How geofencing works (in 60 seconds)

You define a circular or polygonal "zone" around each pickup and drop address. Every 60–120 seconds, the toolkit pulls the current GPS coordinates of each in-transit truck and asks: *is this point inside the zone?*

When a truck transitions from outside-the-zone to inside-the-zone at the pickup, you log "arrived at pickup." When it transitions from inside-the-zone to outside-the-zone at the pickup, you log "departed pickup with goods." When it crosses into the drop zone, you log "arrived at drop." Compare wall-clock time to the original quoted ETA, fire alerts on delta thresholds.

For most loads a 500m circular geofence is sufficient. For congested urban drops (NYC, Toronto Pearson, LAX air freight) you'll want polygons drawn around the loading area itself.

## Mapping geofence events to EDI 214

If you exchange EDI with shippers who require status messages, the toolkit emits codes mapped to ANSI ASC X12 EDI 214 standard:

| Internal event              | EDI 214 status code | Description |
|-----------------------------|---------------------|-------------|
| `pickup_arrived`            | X1                  | Arrived at pickup location |
| `pickup_departed_with_load` | X3                  | Arrived at delivery location |
| `drop_arrived`              | X1 (drop)           | Arrived at delivery |
| `drop_completed`            | D1                  | Completed loading at pickup |
| `delay_detected`            | AF                  | Carrier departed pickup with load |

See `docs/edi214.md` for the full mapping table.

## Why we built this

Avalux was founded to build operational AI automation for SMBs that big enterprise vendors ignore. We found dozens of freight brokers stuck on Excel + group SMS texts, paying tens of thousands per year in dispatcher overtime that a $200/month telematics integration could eliminate.

Most of them don't need an AI receptionist or AI booking agent or any of the AI-flavored slop that fills LinkedIn. They need a working dashboard that pulls the GPS data they already pay for, geofences the pickup, and texts the receiver when the truck is an hour out.

If you want this built and operated for you, we do that — full transparency, fixed-scope contracts, real APIs only, no fragile portal scraping. See [avalux.io](https://avalux.io) or email [eli@avalux.io](mailto:eli@avalux.io).

## Avalux's other open source projects

- [shopify-quickbooks-sync](https://github.com/elikem2021/shopify-quickbooks-sync) — Shopify ↔ QuickBooks Online order, inventory, and refund sync middleware
- [n8n-self-hosted-toolkit](https://github.com/elikem2021/n8n-self-hosted-toolkit) — Production n8n self-hosted setup for SMB ops automation, the open-source Zapier alternative

## License

MIT. Use it, fork it, ship it.

## Keywords

Freight broker software, freight visibility, freight ETA tracking, fleet management, fleet tracking, Geotab integration, Samsara integration, Motive integration, KeepTruckin integration, real-time freight tracking, Project44 alternative, FourKites alternative, EDI 214 automation, freight broker dashboard, 3PL visibility, trucking automation, dispatch automation, supply chain visibility software, broker TMS integration.
