import concurrent.futures
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found.")

client = genai.Client(api_key=API_KEY)


def get_ai_response(user_message):

    prompt = f"""
You are EquityX Assistant.

Primary focus:
- Trading
- Investing
- Stock Markets
- Risk Management
- Technical Analysis

Provide clear, concise and beginner-friendly answers.

Limit responses to approximately 250 words.

You may also answer general knowledge questions when asked.

User Question:
{user_message}
"""

    try:

        with concurrent.futures.ThreadPoolExecutor() as executor:

            future = executor.submit(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
            )

            response = future.result(timeout=10)

        if response and response.text:
            return response.text

        return "I could not generate a response at the moment. " "Please try again."

    except concurrent.futures.TimeoutError:

        print("Gemini Timeout Error")

        return "The service is taking longer than expected. " "Please try again later."

    except Exception as error:

        print(f"Gemini Error: {str(error)}")

        error_text = str(error)

        if "429" in error_text:

            return (
                "The service is temporarily busy due to usage limits. "
                "Please try again in a few minutes."
            )

        if "503" in error_text:

            return (
                "The AI service is currently experiencing high demand. "
                "Please try again shortly."
            )

        return "The assistant is currently unavailable. " "Please try again later."
