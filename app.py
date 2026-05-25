from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

API_URL = "http://43.134.12.202:20128/v1/chat/completions"
API_KEY = "sk-WaGKTcDXJcvYhJDAdekwqzxlz7etoWCCiigwcp7tbA"
MODEL = "xmtp/mimo-v2.5-pro"

SYSTEM_PROMPT = """You are an expert phishing email analyst. Analyze the provided email (header and/or body) for phishing indicators.
Return a JSON object with:
- risk_score: integer 0-100 (0=safe, 100=certain phishing)
- verdict: "SAFE", "SUSPICIOUS", or "PHISHING"
- red_flags: array of strings, each a specific red flag found
- suspicious_urls: array of objects with {url, reason} for any suspicious links
- sender_analysis: object with {domain_reputation, spoofing_indicators, authentication_status}
- tactics: array of social engineering tactics detected (e.g., "urgency", "authority impersonation", "credential harvesting")
- summary: detailed analysis paragraph
- recommendations: array of strings with what to do

Return ONLY valid JSON, no markdown fences."""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    email = data.get("email", "")
    if not email.strip():
        return jsonify({"error": "No email content provided"}), 400
    try:
        resp = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Analyze this email:\n\n{email}"}], "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        result = resp.json()["choices"][0]["message"]["content"]
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011)
