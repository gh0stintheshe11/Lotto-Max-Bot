# Lotto Max Bot

A GitHub-based bot that scrapes Lotto Max results, analyzes historical data, and generates smart number recommendations based on various statistical patterns.

## Features

- 🤖 Automated scraping of Lotto Max results
- 📊 Historical data analysis since July 2019 (RNG era)
- 🎯 Smart number recommendations using multiple strategies:
  - Historical frequency analysis
  - High/Low number balance
  - Even/Odd distribution
  - Pattern recognition
- 🔄 Runs automatically after each draw (Wednesday and Saturday)
- 📱 Discord notifications with recommendations

> [!IMPORTANT]
> This bot is for entertainment purposes only. There's no guarantee of winning. Please gamble responsibly.

## Setup Instructions

### 1. Repository Setup

1. Fork or clone this repository
2. Enable GitHub Actions:
   - Go to your repository's Settings
   - Navigate to "Actions" under "Security"
   - Select "Read and write permissions" under "Workflow permissions"
   - Click "Save"

### 2. Discord Webhook Setup

1. Create a Discord server (or use existing one)
2. Create a channel for lottery recommendations
3. Create a webhook:
   - Click the gear icon next to your channel
   - Select "Integrations"
   - Click "Create Webhook"
   - Name it (e.g., "Lotto Max Bot")
   - Copy the webhook URL
4. Add webhook to GitHub secrets:
   - Go to your repository's Settings
   - Navigate to "Secrets and variables" → "Actions"
   - Click "New repository secret"
   - Name: `DISCORD_WEBHOOK`
   - Value: Your Discord webhook URL
   - Click "Add secret"

## How It Works

### Data Collection
- Scrapes latest Lotto Max results after each draw
- Stores data in JSON and CSV formats
- Maintains historical records in the repository

### Analysis
The bot analyzes:
- Individual number frequencies
- High/Low number patterns
- Even/Odd distributions
- Number pair relationships
- Gap patterns between numbers

### Recommendation Strategies
Generates combinations using different weight combinations:
- Historical weight (0.7/0.2): Importance of historical patterns
- Balance weight (0.7/0.2): Importance of number distribution
- Pattern weight (0.7/0.2): Importance of recognized patterns

### Automated Schedule
- Runs at 03:00 UTC on Wednesday and Saturday
- Can be manually triggered through GitHub Actions

## Files Structure

```
max-bot/
├── scrape.py           # Data scraping script
├── formatter.py        # Data formatting utilities
├── recommender.py      # Number recommendation engine
├── lottery_results.csv # Formatted historical data
├── recommendation_history/ # Historical recommendations
└── .github/workflows/  # GitHub Actions workflow
```

## Manual Trigger

1. Go to the "Actions" tab in your repository
2. Select "Lottery Data Scraper"
3. Click "Run workflow"
4. Select branch and click "Run workflow"
