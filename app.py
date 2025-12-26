from flask import Flask, request, render_template
from ddgs import DDGS
import requests
import re
import html
import os
import pickle
import time

app = Flask(__name__)

# ==========================================
# 1. API KEY SETUP
# ==========================================
GOOGLE_API_KEY = "******************"

if not GOOGLE_API_KEY or "PASTE" in GOOGLE_API_KEY:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    # We print a warning but don't crash immediately so you can fix it
    print("⚠️ WARNING: GOOGLE_API_KEY is missing. AI analysis will fail.")

# ==========================================
# 2. LOAD LOCAL ML MODEL
# ==========================================
try:
    local_model = pickle.load(open('model.pkl', 'rb'))
    local_vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
    LOCAL_MODEL_AVAILABLE = True
    print("✅ Local Model Loaded (With Confidence Scores).")
except Exception as e:
    LOCAL_MODEL_AVAILABLE = False
    print(f"⚠️ Local Model NOT found. Running in Cloud-Only mode.")


# ==========================================
# 3. GET AVAILABLE MODELS
# ==========================================
def get_prioritized_models():
    print("🔍 Scanning account for valid models...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GOOGLE_API_KEY}"
    valid_models = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            all_models = [m['name'].replace('models/', '') for m in data.get('models', [])]

            preferred_order = [
                "gemini-1.5-flash", "gemini-1.5-flash-001", "gemini-1.5-flash-8b",
                "gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-pro"
            ]
            for pref in preferred_order:
                if pref in all_models: valid_models.append(pref)
            for m in all_models:
                if "flash" in m and m not in valid_models: valid_models.append(m)

            print(f"✅ Prioritized Model List: {valid_models[:3]}...")
            return valid_models
    except Exception as e:
        print(f"⚠️ Model scan failed: {e}")
    return ["gemini-1.5-flash", "gemini-pro"]


# ==========================================
# 4. HELPER: LOCAL PREDICTION
# ==========================================
def get_local_prediction(text):
    if not LOCAL_MODEL_AVAILABLE: return "N/A"
    try:
        features = local_vectorizer.transform([text])
        if hasattr(local_model, "predict_proba"):
            probs = local_model.predict_proba(features)[0]
            fake_conf = probs[1] * 100
            real_conf = probs[0] * 100
            if fake_conf > 50:
                return f"Fake ({fake_conf:.1f}% confidence)"
            else:
                return f"Real ({real_conf:.1f}% confidence)"
        else:
            pred = local_model.predict(features)[0]
            return "Fake" if pred == 1 else "Real"
    except Exception as e:
        return f"Error: {e}"


# ==========================================
# 5. GEMINI API CALL (Hybrid)
# ==========================================
def call_gemini_direct(claim, evidence, local_style):
    model_list = get_prioritized_models()

    prompt = f"""
    You are a professional fact checker.
    CLAIM: "{claim}"
    INPUT ANALYSIS:
    - Internal Style Model: The writing style suggests it is {local_style}.
    - Web Evidence: {evidence}
    TASK: Verify the claim using the evidence. 
    If the style is "Fake" but facts are TRUE, mark it as REAL.
    FORMAT: STATUS: REAL/FAKE/UNVERIFIED, REASON: 1 sentence explanation.
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for model_name in model_list:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GOOGLE_API_KEY}"
        try:
            print(f"🤖 Calling Gemini ({model_name})...")
            response = requests.post(url, json=payload, timeout=20)
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif response.status_code == 429:
                print(f"⚠️ {model_name} Busy. Switching...")
                continue
            elif response.status_code == 404:
                print(f"⚠️ {model_name} Not Found. Switching...")
                continue
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            continue

    return "STATUS: UNVERIFIED\nREASON: All AI models are busy."


# ==========================================
# 6. HELPER: EXTRACT TITLE
# ==========================================
def extract_title_from_url(url):
    try:
        print(f"🔗 Visiting URL: {url}")
        headers = {"User-Agent": "Mozilla/5.0 Chrome/120.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            match = re.search(r"<title>(.*?)</title>", response.text, re.IGNORECASE)
            if match:
                clean = html.unescape(match.group(1).strip())
                return clean.split(" - ")[0].split(" | ")[0]
    except:
        pass
    return None


# ==========================================
# 7. SEARCH & ROUTES (UPDATED FOR LINKS)
# ==========================================
def google_search_verification(query):
    # 1. If input is URL, extract title
    if query.startswith("http"):
        t = extract_title_from_url(query)
        if t: query = t

    print(f"🔍 Searching: {query[:50]}")

    try:
        results = DDGS().text(query, max_results=4)
        if not results: return None, None  # Return None for both evidence and link

        # 2. Format Evidence for AI
        evidence_text = "\n".join([f"Title: {r.get('title')}\nSnippet: {r.get('body')}" for r in results])

        # 3. Extract the BEST link (the first result) to show the user
        source_link = results[0].get('href')

        return evidence_text, source_link

    except Exception as e:
        print(f"Search Error: {e}")
        return None, None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    user_input = request.form.get("news_text", "") or request.form.get("news_url", "")
    if not user_input: return render_template("index.html", prediction_text="Input needed")

    # 1. Local Style Check
    local_result = get_local_prediction(user_input)
    print(f"📊 Local Prediction: {local_result}")

    # 2. Web Search (UPDATED: Gets both Evidence and Link)
    evidence, source_link = google_search_verification(user_input)

    # 3. AI Verification
    if evidence:
        response = call_gemini_direct(user_input, evidence, local_result)
    else:
        response = "STATUS: UNVERIFIED\nREASON: No reliable sources found."
        source_link = None

    label = "FAKE" if "STATUS: FAKE" in response else "REAL" if "STATUS: REAL" in response else "UNVERIFIED"
    reason = response.split("REASON:")[-1].strip() if "REASON:" in response else response

    # 4. Render Template (PASS THE LINK TO HTML)
    return render_template("index.html",
                           prediction_text=f"{label}: {reason} (Style Analysis: {local_result})",
                           original_text=user_input,
                           source_link=source_link)


if __name__ == "__main__":
    app.run(debug=True)
