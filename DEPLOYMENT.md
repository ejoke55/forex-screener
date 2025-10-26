# V3 Forex Screener - Deployment Guide

## Quick Deployment to Render (Recommended)

### Step 1: Prepare GitHub Repository

```bash
# Navigate to V3 directory
cd C:\Users\rayog\Documents\TradingBot\V3_forex_screener

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "V3 Forex Screener - Initial commit"

# Add your GitHub remote
git remote add origin https://github.com/ejoke55/forex-screener.git

# Push to main branch
git push -u origin main
```

### Step 2: Create Render Web Service

1. Go to https://render.com/ and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select `ejoke55/forex-screener` repository
5. Configure:
   - **Name**: forex-screener-v3
   - **Region**: Choose closest to you
   - **Branch**: main
   - **Root Directory**: (leave empty if V3 is in root, otherwise specify path)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: Free (or paid for better performance)

### Step 3: Add Environment Variables

In Render dashboard, go to "Environment" and add:

```
OANDA_API_KEY=07050b50de2e9b1e541c7a2542c5d61a-8f0a7a6e27acde0a126234528edcc7bf
OANDA_ACCOUNT_ID=101-001-24355333-001
TELEGRAM_BOT_TOKEN=(your telegram bot token if you have one)
TELEGRAM_CHAT_ID=(your telegram chat ID if you have one)
NEWS_API_KEY=(optional - get from https://newsapi.org/)
PORT=5000
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Wait 3-5 minutes for build to complete
4. Your app will be live at: `https://forex-screener-v3.onrender.com`

### Step 5: Set Up Auto-Deploy

- Render automatically deploys when you push to `main` branch
- To deploy updates:
```bash
git add .
git commit -m "Update message"
git push origin main
```

## Alternative: Manual Deployment from Local Files

If you don't want to use GitHub:

### Using Render CLI

```bash
# Install Render CLI
npm install -g @render/cli

# Login
render login

# Create service
render services create --name forex-screener-v3 --repo https://github.com/ejoke55/forex-screener

# Or deploy from local
render deploy
```

## Deployment Checklist

- [ ] Git repository initialized and pushed to GitHub
- [ ] Render web service created
- [ ] Environment variables added (especially OANDA keys)
- [ ] Build and deployment completed successfully
- [ ] Website accessible at Render URL
- [ ] Initial scan completes (check logs)
- [ ] Telegram alerts working (if configured)
- [ ] All tabs loading correctly

## Post-Deployment

### Monitor Logs

In Render dashboard:
- Go to your service
- Click "Logs" tab
- Watch for:
  - "V3 FOREX SCREENER WEB DASHBOARD"
  - "Initial scan complete"
  - "Dashboard ready!"
  - Any ERROR messages

### Test the Dashboard

Visit your Render URL and check:
1. **High Confidence Tab**: Shows filtered signals
2. **MA Cross Tab**: Shows crossover signals
3. **MA Pullback Tab**: Shows pullback opportunities
4. **Technical Analysis Tab**: Shows pivot points and S/R
5. **News Impact Tab**: Shows forex news
6. **All Instruments Tab**: Shows all 11 instruments

### Verify Auto-Scan

- Check "Last Update" timestamp updates every 5 minutes
- Status should alternate between "Scanning..." and "Idle"
- Scan count should increment

### Test Manual Scan

- Click "🔄 Scan Now" button
- Should see "Scan started" alert
- Dashboard should update with new data

## Troubleshooting

### Build Fails

**Error**: `Could not find requirements.txt`
- **Solution**: Make sure requirements.txt is in root directory

**Error**: `ModuleNotFoundError`
- **Solution**: Check all imports in Python files
- **Solution**: Verify all modules listed in requirements.txt

### Deploy Succeeds But Site Won't Load

**Error**: Application timeout
- **Solution**: Check logs for Python errors
- **Solution**: Verify Flask app.run() uses correct host and port

**Error**: "OANDA connection failed"
- **Solution**: Verify environment variables are set correctly
- **Solution**: Check OANDA API key is valid

### Telegram Alerts Not Working

- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
- Check telegram logs for errors
- Send `/start` to your bot on Telegram
- Lower confidence threshold in config if no signals meet criteria

### News Not Loading

- `NEWS_API_KEY` may be missing (this is optional)
- Free tier has 100 requests/day limit
- Forex Factory calendar should work without API key

## Performance on Free Tier

### Render Free Tier Limitations

- **Sleep after inactivity**: Service sleeps after 15 minutes of no requests
- **Wake-up time**: 30-50 seconds on first request
- **Monthly hours**: 750 hours/month free
- **Memory**: 512 MB RAM

### Optimization for Free Tier

**Keep service awake** (optional):
- Use a service like UptimeRobot to ping your URL every 5 minutes
- Free monitoring at https://uptimerobot.com/

**Reduce memory usage**:
- Service is already optimized for low memory
- 11 instruments vs 19 (42% reduction)
- 5 timeframes vs 6 (17% reduction)

### Upgrade to Paid Tier

For 24/7 operation without sleep:
- **Starter**: $7/month (always on, 512 MB RAM)
- **Standard**: $25/month (always on, 2 GB RAM, better performance)

## Maintenance

### Update Deployment

```bash
# Make changes locally
# Test locally first
python app.py

# Commit and push
git add .
git commit -m "Description of changes"
git push origin main

# Render auto-deploys
```

### Monitor Performance

- Check Render logs daily
- Monitor OANDA API usage
- Track Telegram alert quality
- Review confidence scores for accuracy

### Backup Data

If using database:
```bash
# Export data periodically
pg_dump forex_screener > backup_$(date +%Y%m%d).sql
```

## Support

For deployment issues:
1. Check Render logs first
2. Review environment variables
3. Verify API credentials
4. Check GitHub repo files are complete
5. Refer to main README.md for configuration details

---

**Your deployment URL will be**:
`https://forex-screener-v3.onrender.com` (or similar based on your chosen name)
