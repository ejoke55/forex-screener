# 🔧 RENDER CONFIGURATION SETTINGS

## ⚠️ IMPORTANT: Manual Configuration Required

Render is auto-detecting the wrong start command. You need to **manually configure** it.

---

## 🎯 CORRECT RENDER SETTINGS

Go to your Render dashboard → Your service → Settings

### Build & Deploy Section

Set these **EXACT values**:

| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |
| **Environment** | Python 3 |

### Important Notes

- ❌ **DO NOT use** `gunicorn` command
- ❌ **DO NOT use** `web_dashboard_pythonanywhere:app`
- ✅ **USE** `python app.py`

---

## 📋 STEP-BY-STEP FIX

### Step 1: Update Files on GitHub

```bash
cd C:\Users\rayog\Documents\TradingBot\V3_forex_screener

git add .
git commit -m "Fix Render start command"
git push origin main
```

### Step 2: Configure Render Dashboard

1. Go to: https://dashboard.render.com/
2. Click your **forex-screener** service
3. Click **"Settings"** tab (left sidebar)
4. Scroll to **"Build & Deploy"**
5. Find **"Start Command"**
6. Change from:
   ```
   gunicorn --bind 0.0.0.0:$PORT web_dashboard_pythonanywhere:app
   ```
   To:
   ```
   python app.py
   ```
7. Click **"Save Changes"**

### Step 3: Redeploy

1. Go to **"Manual Deploy"** tab
2. Click **"Deploy latest commit"**
3. Wait 2-3 minutes
4. ✅ Should work now!

---

## 🔍 Why This Happened

Render **auto-detected** your app as a Flask app and:
- Found an old file reference: `web_dashboard_pythonanywhere:app`
- Assumed you wanted to use gunicorn
- Ignored your Procfile

**Solution**: Manually override the start command in Render settings.

---

## ✅ Expected Success Log

After fixing, you should see:

```
==> Running 'python app.py'
================================================================================
V3 FOREX SCREENER WEB DASHBOARD
================================================================================
Starting web server...
[INFO] Running initial scan...
[08:30:00] Analyzing EURUSD...
  ✓ EURUSD: BUY (MA Cross, 75% confidence)
[OK] Initial scan complete: 11 instruments analyzed
[OK] Dashboard ready!

 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://0.0.0.0:10000
```

---

## 📱 Screenshot Guide

If unclear, here's what to change:

**BEFORE** (Wrong):
```
Start Command: gunicorn --bind 0.0.0.0:$PORT web_dashboard_pythonanywhere:app
```

**AFTER** (Correct):
```
Start Command: python app.py
```

---

## 🐛 Alternative: Use Gunicorn (Production-Ready)

If you want to use gunicorn (recommended for production):

1. The requirements.txt already has gunicorn now
2. Create `wsgi.py`:

```python
from app import app

if __name__ == "__main__":
    app.run()
```

3. Set Start Command in Render to:
```
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
```

But **for now, just use `python app.py` to get it working**.

---

## ✨ Quick Summary

1. **Update GitHub** (push latest files)
2. **Go to Render Settings**
3. **Change Start Command to**: `python app.py`
4. **Save Changes**
5. **Manual Deploy**
6. **Success!** ✅

---

**👉 START WITH STEP 2 ABOVE - Go to Render Dashboard Settings**
