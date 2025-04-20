from flask import Flask, request, jsonify, render_template
import re
import google.generativeai as genai
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
try:
    genai.configure(api_key="AIzaSyDXZXFjBcpLN3MNRL_5PjVO1jPK9LoR_YE")
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    logger.error(f"Gemini API config failed: {str(e)}")
    raise

# Updated PII patterns with correct classification names
PII_PATTERNS = {
    "full_name": re.compile(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b"),
    "email": re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b"),
    "phone_number": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "dob": re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
    "aadhar_num": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "credit_debit_no": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "cvv_no": re.compile(r"\b\d{3,4}\b"),
    "expiry_no": re.compile(r"\b(0[1-9]|1[0-2])[/-](\d{2}|\d{4})\b")
}


def mask_pii(email_body):
    masked_email = email_body
    entities = []
    replacements = []

    for label, pattern in PII_PATTERNS.items():
        for match in pattern.finditer(email_body):
            start, end = match.span()
            original = match.group()
            replacements.append((start, end, f"[{label}]"))
            entities.append({
                "position": [start, end],
                "classification": label,
                "entity": original
            })

    for start, end, replacement in sorted(replacements, key=lambda x: -x[0]):
        masked_email = masked_email[:start] + replacement + masked_email[end:]

    return masked_email, entities


def classify_email(masked_content):
    try:
        prompt = f"""Strictly classify this email into exactly one of these categories:
- Billing Issues
- Technical Support
- Account Management
- Other

Return ONLY the category name, nothing else. Email:
{masked_content}"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        return "Other"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/classify', methods=['POST'])
def classify():
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({"error": "Email content is required"}), 400

        email_body = data['email']
        if not isinstance(email_body, str) or not email_body.strip():
            return jsonify({"error": "Email must be a non-empty string"}), 400

        masked_email, masked_entities = mask_pii(email_body)
        category = classify_email(masked_email)

        # Strict output format
        response = {
            "input_email_body": email_body,
            "list_of_masked_entities": masked_entities,
            "masked_email": masked_email,
            "category_of_the_email": category
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
