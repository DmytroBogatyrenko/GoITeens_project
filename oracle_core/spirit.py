import json
from google import genai
from google.genai import types
import time

MODEL_NAME = "gemini-3.1-flash-lite-preview"
API_KEY = "AIzaSyDEv-SJBG14YepopGOKAjHzea2V-SjgHmk"

client = genai.Client(api_key=API_KEY)

class OracleManager:
    @staticmethod
    def generate_response(history_data, current_msg, menu_context):
        formatted_contents = []
        
        if history_data:
            for msg in history_data:
                formatted_contents.append(
                    types.Content(role=msg['role'], parts=[types.Part(text=msg['text'])])
                )
        
        formatted_contents.append(
            types.Content(role='user', parts=[types.Part(text=current_msg)])
        )

        short_instruction = (
            f"Ти — магічний Дух таверни 'Цитадель'. Твоя мова — суміш старослов'янського та фентезійного стилів. "
            f"Відповідай дуже коротко (1-2 речення). "
            f"Ось твоя священна книга страв на сьогодні: {menu_context}. "
            f"Твої правила: "
            f"1. Якщо питають про м'ясо — радь 'Вепра на вертелі' (їжа королів). "
            f"2. Якщо подорожній змерз — пропонуй 'Кров Дракона' або 'Юшку лісника'. "
            f"3. На десерт у нас лише 'Яблуко монаха'. "
            f"4. Про ціни кажи 'золотих' замість 'гривень'."
        )

        return client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=formatted_contents,
            config=types.GenerateContentConfig(
                system_instruction=short_instruction,
                temperature=0.7,
                max_output_tokens=150
            )
        )