# 🛡️ Veritas AI | Hybrid Fake News Detector

**Veritas AI** is an advanced, hybrid fake news detection system designed to combat misinformation. Unlike traditional detectors that rely solely on static datasets, Veritas AI combines a **Local Machine Learning Model** (for stylistic analysis) with **Google Gemini AI** and **Real-Time Web Search** (DuckDuckGo) to verify facts against live sources.

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AI Model](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Key Features

* **🧠 Hybrid Intelligence:**
    * **Local Model:** Uses TF-IDF & Logistic Regression to detect sensationalist/fake writing styles instantly.
    * **Cloud AI:** Uses Google Gemini 2.0 Flash to analyze logic, context, and cross-reference facts.
* **🌐 Real-Time Verification:** Integrates `DuckDuckGo` search to find the latest articles. It doesn't just guess; it checks if the event actually happened.
* **🔗 Source Linking:** Automatically provides a direct link to a verified news source if the claim is true.
* **📊 Confidence Scoring:** Displays a "High Confidence" verdict with a percentage probability from the local model.
* **🎨 Premium Dashboard:** A modern, responsive UI built with Tailwind CSS, featuring glassmorphism, dynamic theming (Red for Fake, Green for Real), and smooth animations.

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **ML/NLP:** Scikit-learn (TF-IDF Vectorizer, Logistic Regression), Pickle
* **LLM Integration:** Google Gemini API (Generative AI)
* **Search Engine:** DuckDuckGo Search API (`ddgs`)
* **Frontend:** HTML5, Tailwind CSS, JavaScript

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/veritas-ai.git](https://github.com/somukumar45)
    cd veritas-ai
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up API Key**
    * Get a free API Key from [Google AI Studio](https://aistudio.google.com/).
    * Open `app.py` and paste your key in the `GOOGLE_API_KEY` variable (or use a .env file).

4.  **Run the Application**
    ```bash
    python app.py
    ```

5.  **Access the Dashboard**
    * Open your browser and go to: `http://127.0.0.1:5000`

## 🧠 How It Works

1.  **Input:** User enters a news headline or URL.
2.  **Style Analysis (Local):** The internal ML model (trained on the Kaggle Fake News dataset) analyzes the text patterns and predicts if the *style* sounds fake (e.g., clickbait, caps lock abuse).
3.  **Fact Retrieval (Web):** The system searches DuckDuckGo for live evidence regarding the claim.
4.  **Synthesis (Gemini AI):** The LLM reviews the Local Prediction + Search Evidence to make a final decision.
    * *Example:* If a headline sounds fake but is actually true (verified by sources), the AI marks it as **REAL**.
5.  **Output:** The user sees a verdict, a detailed explanation, and a link to the source.

## 🔮 Future Improvements
* [ ] Multilingual support (Hindi/Kannada) via fine-tuned Transformer models.
* [ ] Browser Extension for real-time social media filtering.
* [ ] Image analysis for deepfake detection.

## 📜 License
This project is open-source and available under the MIT License.
