# 🫐 BlueberryBot — Setup Guide

## What You Need
- Python 3.10+
- A Telegram Bot Token (from @BotFather)
- An Anthropic API Key (from console.anthropic.com)

---

## Step 1: Get Your Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send: `/newbot`
3. Choose a name: e.g. `BlueberryMarketBot`
4. Choose a username: e.g. `blueberry_market_bot`
5. BotFather gives you a token like: `7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
6. Save this token!

---

## Step 2: Get Your Anthropic API Key

1. Go to: https://console.anthropic.com
2. Click "API Keys" → "Create Key"
3. Copy your key (starts with `sk-ant-...`)

---

## Step 3: Install & Run

```bash
# Clone or copy the bot files to a folder
cd blueberry_bot

# Install dependencies
pip install -r requirements.txt

# Set your tokens (Linux/Mac)
export TELEGRAM_TOKEN="7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows PowerShell
$env:TELEGRAM_TOKEN="7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:ANTHROPIC_API_KEY="sk-ant-..."

# Run the bot
python bot.py
```

---

## Step 4: Test Your Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. You should see the welcome message with menu buttons!

---

## Deployment (24/7 Running)

### Option A: VPS (recommended)
Use any cheap VPS (DigitalOcean, Hetzner, OVH):
```bash
# Create systemd service
sudo nano /etc/systemd/system/blueberrybot.service

[Unit]
Description=BlueberryBot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/blueberry_bot
Environment="TELEGRAM_TOKEN=YOUR_TOKEN"
Environment="ANTHROPIC_API_KEY=YOUR_KEY"
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target

sudo systemctl enable blueberrybot
sudo systemctl start blueberrybot
```

### Option B: Railway.app (free tier)
1. Push code to GitHub
2. Connect Railway to your repo
3. Add environment variables in Railway dashboard
4. Deploy!

### Option C: Render.com (free tier)
Similar to Railway — connect GitHub, add env vars, deploy.

---

## Bot Features

| Feature | Description |
|---------|-------------|
| 🌍 5 Languages | EN, PL, DE, ES, RU |
| 📊 Market Data | Global $3.5B+ market, CAGR, projections |
| 🌎 20+ Countries | Production, regions, volumes |
| 🚢 Export Stats | Chile, Peru, Spain, Poland, Morocco |
| 🎯 Key Markets | China, USA, EU, Russia breakdowns |
| 💰 Prices | FOB, wholesale, retail by market |
| 🌱 Varieties | 25+ new 2020-2025 varieties |
| 🔍 Live Search | Real-time web search via Claude |
| 💬 Free Chat | Ask anything about blueberries |

---

## Customization

Edit `bot.py` to:
- Add more languages: extend `LANGUAGES`, `WELCOME`, `MENU_LABELS`, `TOPIC_PROMPTS`
- Update knowledge base: edit `BLUEBERRY_KNOWLEDGE` string
- Add new topics: add entries to `TOPIC_PROMPTS` and `main_menu_keyboard()`
- Change model: find `claude-sonnet-4-6` and replace

---

## Cost Estimate (Anthropic API)

| Usage | Estimated Cost/Month |
|-------|---------------------|
| 100 queries/day | ~$5–10 |
| 500 queries/day | ~$25–50 |
| 2000 queries/day | ~$100–200 |

Using `claude-sonnet-4-6` with ~1500 max tokens per response.
