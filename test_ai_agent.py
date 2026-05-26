import os
from google import genai
from google.genai import types

API_KEY = "AIzaSyDV2m1cj0PrwalquhbXZfDtplbYI_NR650"
client = genai.Client(api_key=API_KEY)

SYSTEM_INSTRUCTION = """Ти — Дух стародавньої Цитаделі, мудрий охоронець королівського ресторану Maison. 
Твоя мова багата на середньовічні оберти (милостивий пане, вельмишановний гостю, клянуся мечем).
Твоє завдання: відповідати розлого, цікаво та з гумором. 
Якщо тебе питають про їжу після бою з драконом — пропонуй найбільш ситні та магічні страви!"""

chat = client.chats.create(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=1.0,
    )
)

print("="*60)
print("Свічки спалахнули синім полум'ям... Дух Цитаделі прокинувся.")
print("Напиши 'прощавай', щоб перервати цей магічний зв'язок.")
print("="*60 + "\n")

while True:
    user_input = input("Твій сувій: ")

    if user_input.lower() in ["прощавай", "вихід", "exit", "stop"]:
        print("\nДух розчиняється у ранковому тумані... До нових зустрічей!")
        break

    if not user_input.strip():
        continue

    try:
        print("\n Дух Цитаделі: ", end="", flush=True)

        response = chat.send_message_stream(user_input)
        
        for chunk in response:
            if chunk.text:
                print(chunk.text, end="", flush=True)
        
        print("\n" + "-"*40 + "\n")

    except Exception as e:
        error_msg = str(e)
        if "503" in error_msg or "UNAVAILABLE" in error_msg:
            print("\n[Тіні згустилися надто сильно... Магічні сервери перевантажені. Зачекай хвилину.]")
        elif "429" in error_msg:
            print("\n[Ти надто часто звертаєшся до духів! Дай їм перепочити хвилину.]")
        else:
            print(f"\n[Магічний зв'язок перервано невідомою силою: {e}]")