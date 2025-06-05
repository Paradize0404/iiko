import os
import httpx
import json
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()


ORG_ID = os.getenv("IIKO_ORG_ID")
PG_HOST = os.getenv("PGHOST")
PG_PORT = os.getenv("PGPORT", 5432)
PG_USER = os.getenv("PGUSER")
PG_PASSWORD = os.getenv("PGPASSWORD")
PG_DATABASE = os.getenv("PGDATABASE")
DATABASE_URL = os.getenv("DATABASE_URL")







# Получаем токен из таблицы iiko_access_tokens
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT token FROM iiko_access_tokens
        ORDER BY created_at DESC
        LIMIT 1
    """)
    result = cursor.fetchone()

    if not result:
        raise Exception("❌ Токен не найден в таблице iiko_access_tokens")

    token = result[0]

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Ошибка при получении токена из базы данных: {e}")
    exit()



headers = {"Authorization": f"Bearer {token}"}

try:
    response = httpx.post(
        "https://api-ru.iiko.services/api/1/nomenclature",
        headers=headers,
        json={"organizationId": ORG_ID},
        timeout=60
    )
    response.raise_for_status()
    nomenclature = response.json()
except Exception as e:
    print(f"❌ Ошибка при получении номенклатуры: {e}")
    exit()

# Подключение к БД
try:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE
    )
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nomenclature (
        id TEXT PRIMARY KEY,
        name TEXT,
        code TEXT,
        parentGroup TEXT,
        isDeleted BOOLEAN,
        measureUnit TEXT,
        modifiers JSONB
    )""")

    items = nomenclature.get("products", [])
    data = [
        (
            item["id"],
            item["name"],
            item.get("code"),
            item.get("parentGroup"),
            item.get("isDeleted", False),
            item.get("measureUnit"),
            json.dumps(item.get("modifiers", []))
        )
        for item in items
    ]

    cursor.execute("DELETE FROM nomenclature")
    execute_values(
        cursor,
        """
        INSERT INTO nomenclature (id, name, code, parentGroup, isDeleted, measureUnit, modifiers)
        VALUES %s
        """,
        data
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Номенклатура обновлена в PostgreSQL")

except Exception as e:
    print(f"❌ Ошибка работы с базой данных: {e}")
