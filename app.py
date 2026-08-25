import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

from chatbot_configuration import SYSTEM_PROMPT


# ==================================================
# Load Environment Variables
# ==================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


# ==================================================
# Startup Information
# ==================================================

print("====================================")
print("        FoodBuddy AI Starting")
print("====================================")
print("API KEY LOADED:", bool(API_KEY))
print("MODEL:", MODEL_NAME)
print("====================================")


# ==================================================
# Flask App
# ==================================================

app = Flask(__name__)


# ==================================================
# Gemini Client
# ==================================================

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    print("ERROR: GEMINI_API_KEY not found in .env file.")


# ==================================================
# Home Route
# ==================================================

@app.route("/")
def home():
    return render_template("index.html")


# ==================================================
# Chat Route
# ==================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        # --------------------------------------------------
        # Get JSON data
        # --------------------------------------------------

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "reply": "Invalid request. Please try again."
            }), 400


        # --------------------------------------------------
        # Get user message
        # --------------------------------------------------

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "reply": "Please enter a food-related question."
            }), 400


        print("\n====================================")
        print("USER MESSAGE:")
        print(user_message)
        print("====================================")


        # --------------------------------------------------
        # Check Gemini Client
        # --------------------------------------------------

        if client is None:
            return jsonify({
                "reply": (
                    "FoodBuddy AI is not configured correctly. "
                    "Please check your GEMINI_API_KEY in the .env file."
                )
            }), 500


        # --------------------------------------------------
        # Create FoodBuddy Prompt
        # --------------------------------------------------

        prompt = f"""
{SYSTEM_PROMPT}

USER MESSAGE:
{user_message}

Please answer the user naturally and helpfully.
"""


        # --------------------------------------------------
        # Create Gemini Chat
        # --------------------------------------------------

        print("Sending request to Gemini...")

        chat = client.chats.create(
            model=MODEL_NAME
        )


        # --------------------------------------------------
        # Send Message
        # --------------------------------------------------

        response = chat.send_message(prompt)


        print("Gemini response received.")


        # --------------------------------------------------
        # Get Response Text
        # --------------------------------------------------

        if response is None:
            raise Exception("Gemini returned an empty response.")


        bot_reply = response.text


        if not bot_reply:
            raise Exception("Gemini returned no text response.")


        bot_reply = bot_reply.strip()


        print("FoodBuddy response generated successfully.")
        print("====================================\n")


        # --------------------------------------------------
        # Return Response to Frontend
        # --------------------------------------------------

        return jsonify({
            "reply": bot_reply
        })


    # ==================================================
    # Error Handling
    # ==================================================

    except Exception as e:

        print("\n")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("        FOOD BUDDY AI ERROR")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", str(e))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("\n")


        return jsonify({
            "reply": (
                "Sorry! FoodBuddy AI couldn't process your request. "
                "Please try again."
            )
        }), 500


# ==================================================
# Run Flask Application
# ==================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
