# Charge HQ and Enphase Integration Script

This Python script pushes solar production and consumption data from your Enphase Envoy to [Charge HQ](https://chargehq.net), enabling smart EV charging based on solar output. Since Charge HQ doesn't offer native Enphase integration, this script bridges the gap.

---

## Features

- Compatible with Enphase firmware D8.x (and similar versions)
- Pushes solar data to Charge HQ every 60 seconds (configurable)
- Exponential backoff on Envoy connection failures
- Graceful shutdown with Ctrl+C
- Docker-ready for running on external servers
- Configuration via environment variables or `.env` file

---

## Prerequisites

- An Enphase solar system with a local Envoy device on your network
- A Charge HQ account ([sign up here](https://chargehq.net))
- Python 3.7+ or Docker

---

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `CHARGEHQ_API_KEY` | Yes | — | Your Charge HQ Push API key (find it in the webapp: My Equipment → Solar/Battery → Push API) |
| `ENVOY_LOCAL_IP` | Yes | — | Local IP address of your Envoy device (e.g. `192.168.1.50`) |
| `ENVOY_ACCESS_TOKEN` | Yes | — | Envoy access token (get one at [entrez.enphaseenergy.com](https://entrez.enphaseenergy.com/)) |
| `LOG_FILE_PATH` | No | *(empty)* | Path to log file. If empty, logs to stdout only |
| `PUSH_INTERVAL` | No | `60` | Seconds between pushes to Charge HQ |
| `BACKOFF_MAX` | No | `300` | Maximum backoff time in seconds when Envoy is unreachable |

### Access Tokens

Envoy access tokens expire (typically after 12 months). When your token expires, generate a new one at [entrez.enphaseenergy.com](https://entrez.enphaseenergy.com/) and update your `.env` file or environment variable.

---

## Running

### With Docker (recommended for servers)

```bash
# Build the image
docker build -t chargehq-enphase .

# Run with .env file
docker run -d --name chargehq-enphase --env-file .env chargehq-enphase

# View logs
docker logs -f chargehq-enphase
```

### Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python chargehq_enphase.py
```

### Running on Boot (Linux)

Using systemd is recommended for reliability:

```bash
sudo cp chargehq-enphase.service /etc/systemd/system/
sudo systemctl enable chargehq-enphase
sudo systemctl start chargehq-enphase
```

Or via crontab:

```bash
crontab -e
# Add:
@reboot /usr/bin/python3 /path/to/chargehq_enphase.py >> /path/to/cron_startup.log 2>&1 &
```

---

## How It Works

The script reads real-time power data from your Envoy's local API and pushes it to Charge HQ. The payload contains:

```json
{
  "apiKey": "your-api-key",
  "siteMeters": {
    "production_kw": 6.845,
    "consumption_kw": 6.719,
    "net_import_kw": -0.126
  }
}
```

- **production_kw** — Solar generation (kW)
- **consumption_kw** — Total site consumption (kW)
- **net_import_kw** — Grid import (positive) or export (negative) in kW

When the Envoy is unreachable, the script doubles the retry delay (exponential backoff) up to `BACKOFF_MAX` seconds, then resets to `PUSH_INTERVAL` once data flows again.

---

## Troubleshooting

- **"Missing required environment variables"** — Make sure `CHARGEHQ_API_KEY`, `ENVOY_LOCAL_IP`, and `ENVOY_ACCESS_TOKEN` are set in your `.env` file or environment.
- **Connection timeout to Envoy** — Ensure the Envoy is reachable from wherever the script runs. If running in Docker on a remote server, the Envoy IP must be accessible from that server.
- **Token expiry** — Tokens typically last ~12 months. Generate a new one at [entrez.enphaseenergy.com](https://entrez.enphaseenergy.com/) and update your configuration.
- **"power values are inconsistent" on Charge HQ** — Check that `consumption_kw ≈ production_kw + net_import_kw`. If your metering setup differs, verify the Envoy CT meter configuration.

---

## Useful Links

- [Charge HQ Push API Documentation](https://chargehq.net/kb/push-api)
- [Enphase Token Generator](https://entrez.enphaseenergy.com/)
- [Charge HQ Official Site](https://chargehq.net)

---

## Need Help Setting It Up?

You can share this GitHub link with any AI assistant (ChatGPT, Claude, etc.) and ask it to help you deploy the script. For example:

> "Help me set up https://github.com/antongulin/chargehq-enphase-python on my server using Docker"

The AI can walk you through cloning, configuring `.env`, building the Docker image, and running it.

**Recommended setup:** Run the Docker container on a mini server (like a Raspberry Pi, Intel NUC, or any always-on Linux box) on the same network as your Envoy. The container is lightweight and designed to run 24/7 with automatic retry and backoff. Example:

```bash
docker run -d --name chargehq-enphase --restart unless-stopped --env-file .env chargehq-enphase
```

The `--restart unless-stopped` flag ensures the container starts automatically after reboots or crashes.

---

## Contributing

If you encounter issues or have improvements, feel free to open an issue or submit a pull request.