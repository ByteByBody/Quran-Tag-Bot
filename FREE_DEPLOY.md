# Free 24/7 Deployment Guide

## Option 1: Oracle Cloud Free Tier (Recommended)

### Step 1 — Create a Free VM
1. Go to https://cloud.oracle.com and sign up (requires credit card for verification, **never charged**)
2. Create a **VM.Standard.A1.Flex** instance (4 ARM cores, 24GB RAM — completely free)
3. Choose **Ubuntu 22.04/24.04** as the OS
4. Download the SSH key, then connect:
   ```bash
   ssh -i your-key ubuntu@<vm-ip>
   ```

### Step 2 — Deploy the Bot
```bash
# Install Python
sudo apt update && sudo apt install -y python3 python3-venv git

# Clone the bot (or upload it)
git clone https://github.com/your-repo/quran-bot.git
cd quran-bot

# Copy .env.example → .env and set your BOT_TOKEN
cp .env.example .env
nano .env

# Run setup
chmod +x setup.sh && sudo ./setup.sh

# Deploy as a service (always running)
sudo bash deploy/deploy.sh
```

### Step 3 — Check it's running
```bash
sudo systemctl status quran-bot
bash deploy/healthcheck.sh
```

### Updating the Bot
```bash
bash deploy/update.sh
```

---

## Option 2: Fly.io

```bash
# Install flyctl
curl -fsSL https://fly.io/install.sh | sh

# Login
fly auth login

# Create fly.toml
fly launch --no-deploy

# Set secrets
fly secrets set BOT_TOKEN=your_token BOT_ADMINS=your_id

# Deploy
fly deploy
```

Create `fly.toml`:
```toml
app = "quran-bot"
primary_region = "fra"

[env]
  PYTHONUNBUFFERED = "1"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
```

---

## Option 3: Railway (easiest)

1. Push code to GitHub
2. Go to https://railway.app → New Project → Deploy from GitHub repo
3. Add all `.env` variables in the dashboard
4. Set start command: `python bot.py`
5. Railway keeps it running 24/7 on the free tier

---

## Keeping the bot alive

| Platform | Sleeps? | Best for |
|---|---|---|
| **Oracle Cloud** | ❌ Never | Heavy/always-on |
| **Fly.io** | ❌ Never (with config) | Medium |
| **Railway** | ❌ Never | Light/easy setup |
| **Render** | ⚠️ Yes (15 min idle) | ❌ Not recommended |
