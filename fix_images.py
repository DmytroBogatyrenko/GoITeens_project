from online_restaurant_db import Session, Menu

image_fixes = {

    "Вепр на вертелі": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=800",
    "Юшка лісника": "https://images.unsplash.com/photo-1547592180-85f173990554?q=80&w=800",
    "Пиріг з дичиною": "https://images.unsplash.com/photo-1509440159596-0249088772ff?q=80&w=800",
    "Запечена форель": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=800",
    "Дошка Барона": "https://images.unsplash.com/photo-1633504581786-316c8002b1b9?q=80&w=800",
    "Запечене яблуко монаха": "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?q=80&w=800",

    

    "В'ялена оленина": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=800",
    

    "Яйця дракона": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ741thh2Qd1GczHRGAt2kq88qFBnTxp67qZA&s",
    

    "Кров Дракона": "https://assets.dots.live/misteram-public/018d6154-5902-7051-8a36-fd7924d89128-826x0.png",
    

    "Старий Ель": "https://images.unsplash.com/photo-1532635241-17e820acc59f?q=80&w=800"
}


default_img = "https://images.unsplash.com/photo-1600565193348-f74bd3c7ccdf?q=80&w=800"

with Session() as db:
    print("Починаю магічний обряд оновлення меню...")
    
    items = db.query(Menu).all()
    count = 0
    for item in items:

        if item.name in image_fixes:
            item.file_name = image_fixes[item.name]
            print(f"Встановлено унікальне фото для: {item.name}")
            count += 1
        else:

            item.file_name = default_img
            print(f"⚠️ Страва '{item.name}' невідома, встановлено стандартне фото.")
            
    db.commit()
    print(f"\nОбряд завершено! Оновлено {count} унікальних страв.")
    print("Тепер перезапусти сервер (python app.py) та онови сторінку в браузері.")