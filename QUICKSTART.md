# SCAM DNA - Quick Start Guide

## Installation (5 minutes)

### Option 1: Automatic Setup

**Mac/Linux:**
```bash
cd scam_dna
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
cd scam_dna
setup.bat
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate.bat  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```

## First Use

1. Open browser to `http://127.0.0.1:5000`
2. Click **Analyzer** in the navigation
3. Paste this test message:

```
URGENT: Your PayPal account has been locked due to unusual activity!
Click here to verify your identity within 24 hours: http://paypa1-secure.com
Failure to respond will result in permanent account suspension.
- PayPal Security Team
```

4. Click **Analyze Message**
5. Review the DNA code, patterns, and family assignment
6. Navigate to **Timeline**, **Families**, and **Insights** to explore

## What to Expect

- First analysis takes 2-3 seconds (downloads ML model once)
- Subsequent analyses are instant
- Each message gets assigned to a family
- Similar messages show mutation scores
- System learns patterns as you analyze more messages

## Sample Messages

Try analyzing different types:
- Phishing emails
- SMS scams  
- Social media fraud
- Job offer scams
- Crypto investment schemes

## Troubleshooting

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**Port already in use:**
Edit `main.py` and change port from 5000 to 8080

**Slow first analysis:**
Normal - downloading the ML model (80MB, one-time only)

## Next Steps

1. Analyze 10-15 different scam messages
2. Watch families form automatically
3. Check the Insights page for patterns
4. View family details to see evolution predictions

---

**Need Help?** Check README.md for full documentation
