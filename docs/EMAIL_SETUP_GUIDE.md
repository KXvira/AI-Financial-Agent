# Email Service Setup Guide

## 🎯 Overview

This guide will help you configure the email service to send invoice emails using SendGrid. The system works in **two modes**:

1. **Mock Mode** (Default) - Works without any API key, simulates email sending
2. **Production Mode** - Uses SendGrid to send real emails

## 📧 Current Configuration

Your `.env` file now includes:

```env
# Email Service (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key-here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=AI Financial Agent
```

## 🚀 Quick Start (Mock Mode)

**No configuration needed!** The system is already working in mock mode:

1. Start backend: 
   ```bash
   cd backend
   source ../venv-ocr/bin/activate
   python -m uvicorn standalone_app:app --reload --port 8000
   ```

2. Start frontend:
   ```bash
   cd finance-app
   npm run dev
   ```

3. Test email sending from any invoice page
4. All emails are logged to database
5. Email history shows "Mock" status

## 🔑 Setting Up SendGrid (Production Mode)

### Step 1: Create SendGrid Account

1. Go to https://sendgrid.com
2. Sign up for a free account (100 emails/day free forever)
3. Verify your email address

### Step 2: Verify Sender Email

**Option A: Single Sender Verification (Quick & Easy)**

1. Go to Settings → Sender Authentication
2. Click "Verify a Single Sender"
3. Enter your email (e.g., invoices@yourcompany.com)
4. Fill in sender details
5. Click "Create"
6. Check your email and click verification link
7. ✅ Done! You can now send from this email

**Option B: Domain Authentication (Professional)**

1. Go to Settings → Sender Authentication
2. Click "Authenticate Your Domain"
3. Enter your domain (e.g., yourcompany.com)
4. Follow DNS record setup instructions
5. Wait for DNS propagation (up to 48 hours)
6. ✅ Once verified, you can send from any @yourcompany.com email

### Step 3: Generate API Key

1. Go to Settings → API Keys
2. Click "Create API Key"
3. Name: "AI Financial Agent"
4. Permissions: Select "Full Access" or "Mail Send"
5. Click "Create & View"
6. **COPY THE KEY NOW** - you won't see it again!
7. Should look like: `SG.xxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyy`

### Step 4: Update .env File

Edit `/home/munga/Desktop/AI-Financial-Agent/.env`:

```env
# Replace with your actual values
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyy
SENDGRID_FROM_EMAIL=invoices@yourcompany.com
SENDGRID_FROM_NAME=Your Company Name
```

### Step 5: Restart Backend

```bash
cd /home/munga/Desktop/AI-Financial-Agent/backend
source ../venv-ocr/bin/activate
python -m uvicorn standalone_app:app --reload --port 8000
```

You should see:
```
📬 Email Configuration:
   ✅ SendGrid API Key: SG.xxxxxxxx...
   📧 From: Your Company Name <invoices@yourcompany.com>
```

### Step 6: Test Real Email

1. Go to any invoice in the UI
2. Click "📧 Send Invoice"
3. Enter a real email address
4. Click "Send Invoice"
5. Check the recipient's inbox!

## ✅ Testing Email Configuration

### Test via API

```bash
# Check configuration status
curl http://localhost:8000/api/email/test

# Expected response (configured):
{
  "configured": true,
  "message": "SendGrid is configured and ready",
  "from_email": "invoices@yourcompany.com",
  "from_name": "Your Company Name"
}

# Expected response (not configured):
{
  "configured": false,
  "message": "SendGrid not configured. Using mock email mode for development.",
  "from_email": "noreply@example.com",
  "from_name": "Financial Agent"
}
```

### Test via UI

1. Navigate to http://localhost:3000/invoices
2. Click any invoice
3. Click "📧 Send Invoice" button
4. Fill in email form
5. Send email
6. Check success message
7. Verify email status in "Email History" section

**Mock Mode**: Shows blue "✓ Mock" badge
**SendGrid Mode**: Shows green "✓ Sent" badge

## 📊 Email Delivery Tracking

### View Email History

**Via UI:**
- Go to any invoice detail page
- Scroll to "Email History" section
- Filter by: All, Sent, Failed
- Click refresh to update

**Via API:**
```bash
# All emails in system
curl http://localhost:8000/api/email/history

# Emails for specific invoice
curl http://localhost:8000/api/email/history/INV-2024-001
```

### Email Log Fields

Each sent email is logged with:
- Invoice ID
- Recipient email & name
- Subject line
- Send timestamp
- Status (sent/failed)
- Method (sendgrid/mock)
- Error message (if failed)
- CC recipients
- PDF attachment flag

## 🎨 Email Templates

### Default HTML Email Structure

```
┌─────────────────────────────────────┐
│ Invoice #INV-2024-001               │
│ from Your Company Name              │
├─────────────────────────────────────┤
│ [Custom Message - Highlighted]      │
├─────────────────────────────────────┤
│ Invoice Details:                    │
│ • Number: INV-2024-001             │
│ • Issue Date: Jan 1, 2024          │
│ • Due Date: Jan 31, 2024           │
│ • Amount Due: KES 50,000           │
├─────────────────────────────────────┤
│ Please find the invoice attached   │
├─────────────────────────────────────┤
│ Payment Instructions:               │
│ [Bank details here]                │
├─────────────────────────────────────┤
│ Thank you for your business!        │
└─────────────────────────────────────┘

📎 Attachment: invoice_INV-2024-001.pdf
```

### PDF Invoice Layout

Professional PDF with:
- Company header/logo area
- Invoice number and dates
- Bill To section
- Itemized table (item, qty, price, amount)
- Subtotal, Tax (16%), Total
- Payment instructions
- Thank you footer

## 🔧 Troubleshooting

### Issue: Emails Not Sending

**Check 1**: Verify API key is set
```bash
curl http://localhost:8000/api/email/test
```

**Check 2**: Check backend logs
```bash
tail -f logs/backend.log
```

**Check 3**: Verify sender email is authenticated in SendGrid

### Issue: Emails Going to Spam

**Solution 1**: Authenticate your domain (not just single sender)

**Solution 2**: Set up SPF, DKIM, DMARC records

**Solution 3**: Use a professional sending domain (not gmail/yahoo)

### Issue: API Key Invalid

**Symptoms**: Error "Invalid API key" or 401 Unauthorized

**Solutions**:
1. Regenerate API key in SendGrid
2. Ensure no extra spaces in .env file
3. Restart backend after updating .env
4. Check API key has "Mail Send" permissions

### Issue: Mock Mode Won't Disable

**Cause**: API key not properly loaded

**Solutions**:
1. Check .env file exists in project root
2. Verify no typos: `SENDGRID_API_KEY` (not `SENDGRID_KEY`)
3. Restart backend server
4. Check startup logs for "SendGrid API Key: SG.xxxxx..."

## 📈 SendGrid Free Tier Limits

- 100 emails/day forever free
- 40,000 emails first 30 days
- Then 100/day after trial
- No credit card required for free tier

## 🎯 Best Practices

1. **Use Domain Authentication** for better deliverability
2. **Monitor SendGrid Dashboard** for bounces/spam reports
3. **Test with Real Email** before going live
4. **Keep API Keys Secret** - never commit to git
5. **Use Professional From Name** - increases open rates
6. **Include Unsubscribe Link** (for marketing emails)
7. **Set Up Webhooks** to track opens/clicks (advanced)

## 🔐 Security Notes

- API keys are sensitive - treat like passwords
- Use different keys for dev/staging/production
- Rotate keys regularly
- Monitor SendGrid activity logs
- Never expose keys in frontend code
- Use environment variables only

## 📚 Additional Resources

- SendGrid Docs: https://docs.sendgrid.com
- Email Best Practices: https://sendgrid.com/blog/email-best-practices/
- Sender Authentication Guide: https://sendgrid.com/docs/ui/account-and-settings/how-to-set-up-domain-authentication/
- API Reference: https://docs.sendgrid.com/api-reference/mail-send/mail-send

## ✉️ Support

If you encounter issues:
1. Check this guide first
2. Review SendGrid documentation
3. Check backend logs
4. Test with curl commands
5. Verify .env configuration

---

**Quick Command Reference:**

```bash
# Start backend
cd backend && source ../venv-ocr/bin/activate && python -m uvicorn standalone_app:app --reload --port 8000

# Start frontend
cd finance-app && npm run dev

# Test email config
curl http://localhost:8000/api/email/test

# View health status
curl http://localhost:8000/health

# Get email history
curl http://localhost:8000/api/email/history
```

---

**Current Status:** ✅ Mock mode active, ready for testing!

**To Enable Production:** Add SendGrid API key to `.env` and restart backend.
