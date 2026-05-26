import os
import urllib.request
from online_restaurant_db import Session, Menu


FILES_PATH = 'static/menu'
if not os.path.exists(FILES_PATH):
    os.makedirs(FILES_PATH)


dishes = [
    {
        "name": "Вепр на вертелі",
        "ingredients": "М'ясо дикого кабана, лісовий мед, розмарин, часник, груба сіль",
        "description": "Справжня їжа королів та лордів. Величезний шматок м'яса, що повільно запікався на відкритому вогні до утворення хрусткої скоринки. Подається на дерев'яній дошці.",
        "price": 450,
        "weight": "600",
        "prep_time": 45,
        "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=800&auto=format&fit=crop",
        "file_name": "boar.jpg"
    },
    {
        "name": "Юшка лісника",
        "ingredients": "Білі гриби, перлова крупа, корінь селери, цибуля, лісові трави",
        "description": "Густа та навариста юшка, якою гріються мандрівники у придорожніх тавернах. Готується у чавунному казанку над вугіллям.",
        "price": 180,
        "weight": "400",
        "prep_time": 20,
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554?q=80&w=800&auto=format&fit=crop",
        "file_name": "stew.jpg"
    },
    {
        "name": "Пиріг з дичиною",
        "ingredients": "Рублене м'ясо оленя, житнє тісто, чорний перець, смажена цибуля",
        "description": "Традиційний закритий пиріг. Хрустке житнє тісто надійно зберігає гарячий та соковитий м'ясний сік всередині.",
        "price": 280,
        "weight": "350",
        "prep_time": 30,
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?q=80&w=800&auto=format&fit=crop",
        "file_name": "meat_pie.jpg"
    },
    {
        "name": "Запечена форель",
        "ingredients": "Свіжа річкова форель, лимон, чебрець, вершкове масло",
        "description": "Риба, щойно виловлена з гірського струмка. Запікається з духмяними травами та подається з краплинкою кислого соку.",
        "price": 320,
        "weight": "300",
        "prep_time": 25,
        "image_url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=800&auto=format&fit=crop",
        "file_name": "trout.jpg"
    },
    {
        "name": "Дошка Барона",
        "ingredients": "Витриманий сир, виноград, волоські горіхи, житній хліб, мед",
        "description": "Ідеальна закуска до кубка темного елю або вина. Зібрання найкращих сирів із льохів замку.",
        "price": 350,
        "weight": "450",
        "prep_time": 10,
        "image_url": "https://images.unsplash.com/photo-1633504581786-316c8002b1b9?q=80&w=800&auto=format&fit=crop",
        "file_name": "cheese_board.jpg"
    },
    {
        "name": "В'ялена оленина",
        "ingredients": "М'ясо лісового оленя, ялівець, дикий перць",
        "description": "Тонкі скибочки м'яса, висушені на гірському повітрі. Найкраща закуска для довгих розмов.",
        "price": 190, "weight": "100", "prep_time": 5,
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=800",
        "file_name": "venison.jpg"
    },
    {
        "name": "Яйця дракона",
        "ingredients": "Перепелині яйця, гострий соус, попіл з трав",
        "description": "Запечені яйця у таємничій чорній паніровці. Кажуть, вони додають сили справжнім воїнам.",
        "price": 120, "weight": "150", "prep_time": 10,
        "image_url": "https://images.unsplash.com/photo-1569254994521-ddb542a78eb3?q=80&w=800",
        "file_name": "dragon_eggs.jpg"
    },
    {
        "name": "Запечене яблуко монаха",
        "ingredients": "Яблуко, грецькі горіхи, мед, кориця",
        "description": "Солодкий спогад про домашній затишок. Подається гарячим прямо з печі.",
        "price": 110, "weight": "200", "prep_time": 15,
        "image_url": "https://images.unsplash.com/photo-1568571780765-9276ac8b75a2?q=80&w=800",
        "file_name": "apple.jpg"
    },
    {
        "name": "Кров Дракона",
        "ingredients": "Вишневий сік, прянощі, секретний корінь",
        "description": "Густий, темно-червоний напій, що палає зсередини. Зігріє навіть у люту зиму.",
        "price": 95, "weight": "300", "prep_time": 3,
        "image_url": "https://images.unsplash.com/photo-1544145945-f904253d0c7b?q=80&w=800",
        "file_name": "drink_red.jpg"
    },
    {
        "name": "Старий Ель",
        "ingredients": "Ячмінь, хміль, джерельна вода",
        "description": "Класичний темний напій, зварений за рецептом 1243 року.",
        "price": 80, "weight": "500", "prep_time": 2,
        "image_url": "https://images.unsplash.com/photo-1532635241-17e820acc59f?q=80&w=800",
        "file_name": "ale.jpg"
    }
]

print("Починаю підготовку королівського банкету...")

with Session() as db:
    for d in dishes:

        existing_dish = db.query(Menu).filter_by(name=d["name"]).first()
        if not existing_dish:
            filepath = os.path.join(FILES_PATH, d["file_name"])
            

            if not os.path.exists(filepath):
                print(f"Завантажую малюнок для: {d['name']}...")
                try:
                    req = urllib.request.Request(d["image_url"], headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                        out_file.write(response.read())
                except Exception as e:
                    print(f"Помилка завантаження картинки {d['name']}: {e}")
            

            new_dish = Menu(
                name=d["name"],
                ingredients=d["ingredients"],
                description=d["description"],
                price=d["price"],
                weight=d["weight"],
                prep_time=d["prep_time"],
                file_name=d["file_name"]
            )
            db.add(new_dish)
            print(f"Страву '{d['name']}' виковано і додано до меню!")
        else:
            print(f"Страва '{d['name']}' вже є у базі.")
            
    db.commit()

print("\nВсі страви успішно додані! Тепер можеш запускати app.py та відкривати меню.")