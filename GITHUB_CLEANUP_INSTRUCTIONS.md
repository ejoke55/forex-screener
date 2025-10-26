# GitHub Cleanup Instructions - FIX DEPLOYMENT ERROR

## 🔴 Problem
Your GitHub repo has V2 and V3 files mixed together, causing deployment to fail with error 127.

## ✅ Solution: Clean GitHub Repository

### Option 1: Clean Via GitHub Web Interface (Easiest)

1. **Go to your repo**: https://github.com/ejoke55/forex-screener

2. **Delete these OLD V2 files** (click each file → Delete):
   ```
   screener_combined.py
   screener_ema.py
   screener_ma_cross.py
   screener_ma_pullback.py
   screener_supertrend.py
   screener_triple_ema_pullback.py

   ALERT_SETUP_GUIDE.md
   CHANGES_SUMMARY.md
   DEPLOYMENT_GUIDE.md
   PRODUCTION_READY_VERIFICATION.md
   RENDER_DEPLOYMENT_GUIDE.md
   TRIPLE_EMA_PULLBACK_README.md
   UPLOAD_CHECKLIST.txt
   V2_CHANGES_README.md

   pythonanywhere_wsgi.py
   render.yaml
   web_dashboard_pythonanywhere.py

   (The long filename starting with CUsersrayog...)
   ```

3. **Delete these OLD directories**:
   ```
   __pycache__/
   notifications/ (folder, not the .py file)
   outputs/
   ```

4. **Upload NEW files** (from `V3_forex_screener` folder):
   ```
   config/__init__.py
   connectors/__init__.py
   strategies/__init__.py
   utils/__init__.py
   templates/__init__.py
   static/__init__.py
   ```

5. **Commit changes**: "Clean V2 files, add V3 __init__.py files"

---

### Option 2: Clean Via Git Command Line (Faster)

**Run these commands in Git Bash or WSL**:

```bash
# Navigate to your local V3 folder
cd /mnt/c/Users/rayog/Documents/TradingBot/V3_forex_screener

# Remove old V2 files if they exist locally
rm -f screener_combined.py screener_ema.py screener_ma_cross.py
rm -f screener_ma_pullback.py screener_supertrend.py screener_triple_ema_pullback.py
rm -f ALERT_SETUP_GUIDE.md CHANGES_SUMMARY.md DEPLOYMENT_GUIDE.md
rm -f PRODUCTION_READY_VERIFICATION.md RENDER_DEPLOYMENT_GUIDE.md
rm -f TRIPLE_EMA_PULLBACK_README.md UPLOAD_CHECKLIST.txt V2_CHANGES_README.md
rm -f pythonanywhere_wsgi.py render.yaml web_dashboard_pythonanywhere.py
rm -rf __pycache__ notifications outputs

# Add all V3 files including new __init__.py files
git add .

# Commit
git commit -m "Clean V2 files and add V3 __init__.py files"

# Force push to GitHub (this will clean the repo)
git push origin main --force
```

---

### Option 3: Start Fresh GitHub Repo (Nuclear Option)

If above options don't work, create a brand new clean repo:

1. **Create new repo** on GitHub: `forex-screener-v3`

2. **Initialize clean V3**:
```bash
cd /mnt/c/Users/rayog/Documents/TradingBot/V3_forex_screener

# Remove any existing git
rm -rf .git

# Initialize fresh
git init
git add .
git commit -m "Clean V3 Forex Screener"

# Add new remote
git remote add origin https://github.com/ejoke55/forex-screener-v3.git
git branch -M main
git push -u origin main
```

3. **Update Render** to point to new repo

---

## 🔍 After Cleanup - Verify Files

Your GitHub repo should have **exactly these files**:

```
forex-screener/
├── config/
│   ├── __init__.py          ✅ NEW
│   ├── api_config.py
│   ├── instruments.py
│   └── strategies.py
├── connectors/
│   ├── __init__.py          ✅ NEW
│   ├── oanda_connector.py
│   └── yfinance_connector.py
├── strategies/
│   ├── __init__.py          ✅ NEW
│   ├── sma_strategy.py
│   ├── ma_cross_strategy.py
│   ├── ma_pullback_strategy.py
│   └── supertrend_mtf.py
├── utils/
│   ├── __init__.py          ✅ NEW
│   ├── confidence_scorer.py
│   ├── risk_calculator.py
│   ├── technical_analysis.py
│   └── news_fetcher.py
├── templates/
│   ├── __init__.py          ✅ NEW
│   └── dashboard.html
├── static/
│   └── __init__.py          ✅ NEW
├── app.py
├── screener_v3.py
├── notifications.py
├── requirements.txt
├── runtime.txt
├── Procfile
├── .gitignore
├── .env.example
├── database_schema.sql
├── README.md
├── DEPLOYMENT.md
├── CHANGES_V2_TO_V3.md
└── PROJECT_SUMMARY.md
```

**Total**: ~32 files (no V2 files!)

---

## 🚀 After Cleanup - Redeploy

1. **Go to Render dashboard**
2. **Trigger manual deploy** or wait for auto-deploy
3. **Check logs** - should now build successfully
4. **Verify**: Visit your Render URL

---

## 🐛 If Still Failing

Check Render build logs for specific error. Common fixes:

**Error: "No module named 'config'"**
- Solution: Make sure `__init__.py` files are uploaded

**Error: "ModuleNotFoundError: No module named 'yfinance'"**
- Solution: Check `requirements.txt` is uploaded and complete

**Error: "Port already in use"**
- Solution: Render sets PORT automatically, app.py should be: `app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))`

Let me fix that now...
