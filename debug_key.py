import google.generativeai as genai
import os

# --- PASTE YOUR KEY BELOW INSIDE THE QUOTES ---
MY_KEY = "AIzaSyBpolnmZocNQytgGtc0kslKVOYpJPtMNoU"
# ----------------------------------------------

print(f"Testing Key: {MY_KEY[:10]}... (hidden)")

genai.configure(api_key=MY_KEY)

try:
    print("Attempting to connect to Google AI...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hello")
    print("\n✅ SUCCESS! Your API Key works.")
    print(f"AI Response: {response.text}")
except Exception as e:
    print("\n❌ FAILURE. Here is the exact error from Google:")
    print("------------------------------------------------")
    print(e)
    print("------------------------------------------------")
    print("FIX:")
    if "API_KEY_INVALID" in str(e):
        print("-> Your Key is wrong. Go to aistudio.google.com and create a new one.")
    elif "404" in str(e):
        print("-> The model name is wrong. Try using 'gemini-pro' instead.")