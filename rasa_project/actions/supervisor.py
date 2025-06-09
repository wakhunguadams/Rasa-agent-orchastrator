import os
import requests
import logging
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from dotenv import load_dotenv
import pyttsx3 

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Gemini Config
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"


class ActionSupervisor(Action):
    def name(self):
        return "action_supervise_agents"
    
    def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def call_gemini(self, user_input):
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{
                    "text": """
                    Detect user intent classify it as either onboarding, faq, general
                    onbooarding:
                    faq: Frequently asked questions
                    general 
                    
                    Return onboarding/faq/general: '{user_input}'
                    """
                }]
            }]
        }
        logger.debug("Sending request to Gemini with payload: %s", payload)

        try:
            response = requests.post(f"{GEMINI_URL}?key={GEMINI_KEY}", headers=headers, json=payload)
            logger.debug("Gemini response status: %s", response.status_code)
            response.raise_for_status()  # Raise if not 200 OK
            data = response.json()
            logger.debug("Gemini response JSON: %s", data)
            return data
        except Exception as e:
            logger.error("Error calling Gemini API: %s", str(e))
            return None

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        user_input = tracker.latest_message.get("text")
        logger.info("Received user input: %s", user_input)

        gemini_data = self.call_gemini(user_input)
        if not gemini_data:
            dispatcher.utter_message("Failed to contact Gemini.")
            return []

        try:
            plan_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]
            dispatcher.utter_message(text=f"Gemini Plan: {plan_text}")
        except KeyError as e:
            logger.error("Gemini response missing expected structure: %s", str(e))
            dispatcher.utter_message("Sorry, I couldn't process the plan.")
            return []

        try:
            report = requests.get("http://localhost:8001/generate-report").json()
            summary = requests.post("http://localhost:8002/summarize", json={"text": report["report"]}).json()
            email = requests.post("http://localhost:8003/send-email", json={"body": summary["summary"]}).json()
            logger.info("Report flow completed: %s", email)
        except Exception as e:
            logger.error("Error in report/summarize/email steps: %s", str(e))
            dispatcher.utter_message("An error occurred while generating the report.")
            return []

        dispatcher.utter_message(text="Report generated, summarized, and emailed!")
        self.speak("Report generated, summarized, and emailed!")
        return []
