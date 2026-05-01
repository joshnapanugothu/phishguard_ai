from model import predict
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def normalize(text):
    return text.replace("https://", "").replace("http://", "").strip()

def confidence_from_score(score, risk):
    if risk == "High":
        return min(95, 75 + score * 3)
    elif risk == "Medium":
        return min(85, 50 + score * 3)
    else:
        return max(30, 40 - score * 2)

@app.route("/")
def home():
    return render_template("index.html")

def strong_rule_engine(text):
    score = 0
    reasons = []

    if any(word in text for word in ["otp", "password", "pin", "cvv"]):
        score += 6
        reasons.append("Sensitive information request")

    if any(word in text for word in ["bank", "upi", "card"]):
        score += 4
        reasons.append("Financial context detected")

    if "account" in text:
        score += 1

    if any(word in text for word in ["verify", "login", "confirm", "secure"]):
        score += 3
        reasons.append("Action requested")

    if "update" in text:
        score += 2
        reasons.append("Update request")

    if any(word in text for word in ["urgent", "immediately", "now"]):
        score += 2
        reasons.append("Urgency detected")

    if "http" in text or "www" in text:
        score += 2
        reasons.append("External link detected")

    if ("otp" in text and ("verify" in text or "login" in text)):
        score += 5
        reasons.append("OTP phishing pattern")

    if ("password" in text and ("reset" in text or "enter" in text)):
        score += 5
        reasons.append("Password attack pattern")

    if any(char.isdigit() for char in text):
        score += 1

    if len(text.split()) > 4 and score >= 3:
        score += 2

    if score >= 11:
        return "High", confidence_from_score(score, "High"), reasons
    elif score >= 5:
        return "Medium", confidence_from_score(score, "Medium"), reasons
    else:
        return "Safe", confidence_from_score(score, "Safe"), reasons

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        text = data.get("input", "").lower().strip()

        if not text:
            return jsonify({
                "risk": "Safe",
                "confidence": 50,
                "reasons": ["Empty input"]
            })

        norm_text = normalize(text)

        if any(phrase in norm_text for phrase in [
            "no action needed",
            "no need",
            "no update required",
            "no update needed",
            "ignore this message",
            "no changes required",
            "everything is fine",
            "no issue",
            "all good",
            "completed successfully",
            "successfully completed",
            "operation successful",
            "update completed"
        ]):
            return jsonify({
                "risk": "Safe",
                "confidence": 90,
                "reasons": ["No action required context"]
            })

        ml_risk, ml_conf = predict(norm_text)
        rule_risk, rule_conf, reasons = strong_rule_engine(norm_text)

        if rule_risk == "High":
            final_risk = "High"
            final_conf = rule_conf
            final_reasons = reasons

        elif ml_risk == "High":
            final_risk = "High"
            final_conf = ml_conf
            final_reasons = ["ML detected phishing pattern"]

        elif rule_risk == "Medium" or ml_risk == "Medium":
            final_risk = "Medium"
            final_conf = max(ml_conf, rule_conf)
            final_reasons = reasons if reasons else ["Moderate risk detected"]

        else:
            final_risk = "Safe"
            final_conf = max(ml_conf, rule_conf)
            final_reasons = ["No strong threat detected"]

        return jsonify({
            "risk": final_risk,
            "confidence": final_conf,
            "reasons": final_reasons[:3]
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "risk": "Safe",
            "confidence": 0,
            "reasons": ["Server error"]
        })

@app.route("/examples")
def examples():
    return jsonify({
        "safe": "https://google.com hello@gmail.com good morning",
        "medium": "http://account-check.com update@profile.com please check your account",
        "high": "http://secure-login-paypal.xyz/verify otp@secure.com enter otp immediately"
    })

if __name__ == "__main__":
    app.run(debug=True)