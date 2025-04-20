# akaike_assignment
# Email Shield 🛡️

A privacy-first email classification system that detects and masks personally identifiable information (PII) using traditional NLP techniques, and classifies emails using Google Gemini AI.

## 🚀 Features
- 🔍 Detects PII like names, emails, phone numbers, Aadhaar, credit cards, etc.
- 🧠 Classifies email into: Billing Issues, Technical Support, Account Management, or Other.
- 🎯 Strict JSON-based output for integration with internal support tools.

## 🛠️ Tech Stack
- **Backend**: Flask + Google Gemini (via `google-generativeai`)
- **Frontend**: TailwindCSS + JavaScript
- **Hosting**: Hugging Face Spaces (Flask SDK)

## 🧪 How to Use
1. Paste your email content.
2. Click **Analyze**.
3. View masked PII, extracted entities, and category.

## 📦 Setup (for local use)
```bash
pip install -r requirements.txt
python app.py
