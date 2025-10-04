import os
import google.generativeai as genai
import json

def analyze_document_with_gemini(raw_text: str) -> dict:
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)

        prompt = f"""
        Analyze the following document text and extract the specified information.
        Return the output as a clean JSON object with the following keys:
        "category", "heading", "summary", "key_terms", "important_dates".
        
        - The "category" should be one of these: [finance, education, health, legal, travel, other].
        - The "heading should be a concised one.
        - The summaries length should be dependent on the content of the document text
        - "Key_terms" should involve the main events and the persons or anyother important specifications that are in the document text
        - "important_dates": [ {{"date": "YYYY-MM-DD", "event": "A brief description of what this date is for"}} ]

        --- RAW TEXT ---
        {raw_text}
        """
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(prompt)

        

        json_string = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_string)

    except Exception as e:
        print(f"❌ An error occurred while using the Gemini API: {e}")
        return {"error": "Failed to analyze document with Gemini."}