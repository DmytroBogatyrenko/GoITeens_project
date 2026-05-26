from sqlalchemy import create_engine, text


engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/online_restaurant")

with engine.connect() as conn:
    try:

        conn.execute(text("ALTER TABLE menu ADD COLUMN prep_time INTEGER DEFAULT 15;"))
        conn.commit()
        print("Колонку prep_time успішно виковано і додано до таблиці menu!")
    except Exception as e:
        print(f"Щось пішло не так (можливо, колонка вже є): {e}")