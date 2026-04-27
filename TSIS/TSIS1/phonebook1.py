import csv
import psycopg2
import json
from config import load_config
 
conn = psycopg2.connect(**load_config())
cur = conn.cursor()
 

# ИНИЦИАЛИЗАЦИЯ СХЕМЫ БД
def init_db():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id   SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );
    """)
 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id         SERIAL PRIMARY KEY,
            name       VARCHAR(100) NOT NULL,
            phone      VARCHAR(20)  UNIQUE NOT NULL,
            email      VARCHAR(100),
            birthday   DATE,
            group_id   INT REFERENCES groups(id),
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
 
    cur.execute("""
        CREATE OR REPLACE PROCEDURE add_phone(p_name TEXT, p_phone TEXT)
        LANGUAGE plpgsql AS $$
        BEGIN
            UPDATE phonebook SET phone = p_phone WHERE name = p_name;
        END;
        $$;
    """)
 
    cur.execute("""
        CREATE OR REPLACE PROCEDURE delete_contact(p_name TEXT)
        LANGUAGE plpgsql AS $$
        BEGIN
            DELETE FROM phonebook WHERE name = p_name;
        END;
        $$;
    """)
 
    cur.execute("""
        CREATE OR REPLACE FUNCTION search_contacts(q TEXT)
        RETURNS TABLE(
            id         INT,
            name       VARCHAR,
            phone      VARCHAR,
            email      VARCHAR,
            birthday   DATE,
            group_id   INT,
            created_at TIMESTAMP
        )
        LANGUAGE plpgsql AS $$
        BEGIN
            RETURN QUERY
            SELECT p.id, p.name, p.phone, p.email, p.birthday, p.group_id, p.created_at
            FROM phonebook p
            WHERE p.name  ILIKE '%' || q || '%'
               OR p.phone ILIKE '%' || q || '%'
               OR p.email ILIKE '%' || q || '%';
        END;
        $$;
    """)
 
    conn.commit()
    print("БД инициализирована.")


# HELPER: GET OR CREATE GROUP
def get_group_id(group_name):
    cur.execute("SELECT id FROM groups WHERE name=%s", (group_name,))
    res = cur.fetchone()
    if res:
        return res[0]
    cur.execute("INSERT INTO groups(name) VALUES (%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]


# ADD CONTACT
def add_contact():
    name       = input("Введите Имя: ")
    phone      = input("Введите номер телефона: ")
    email      = input("Введите электронную почту: ")
    birthday   = input("День рождения (YYYY-MM-DD): ")
    group_name = input("Группа: ")
 
    gid = get_group_id(group_name)
 
    cur.execute("SELECT id FROM phonebook WHERE name=%s", (name,))
    existing = cur.fetchone()
 
    if existing:
        choice = input("Контакт существует. Перезаписать? (yes/no): ")
        if choice.lower() != "yes":
            print("Пропущено.")
            return
        cur.execute("""
            UPDATE phonebook
            SET phone=%s, email=%s, birthday=%s, group_id=%s
            WHERE name=%s
        """, (phone, email, birthday, gid, name))
    else:
        cur.execute("""
            INSERT INTO phonebook(name, phone, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, phone, email, birthday, gid))
 
    conn.commit()
    print("Готово!")
 
# ─────────────────────────────────────────────
# ADD PHONE
# ─────────────────────────────────────────────
def add_phone():
    name  = input("Имя: ")
    phone = input("Новый телефон: ")
    cur.execute("CALL add_phone(%s, %s)", (name, phone))
    conn.commit()
    print("Телефон обновлён.")
 
 
# ─────────────────────────────────────────────
# FILTER BY GROUP
# ─────────────────────────────────────────────
def filter_group():
    group_name = input("Группа: ")
    cur.execute("""
        SELECT p.name, p.phone, p.email
        FROM phonebook p
        JOIN groups g ON p.group_id = g.id
        WHERE g.name = %s
    """, (group_name,))
    rows = cur.fetchall()
    if not rows:
        print("Группа пуста или не найдена.")
    for row in rows:
        print(row)
 
 
# ─────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────
def search():
    q = input("Поиск: ")
    cur.execute("SELECT * FROM search_contacts(%s::TEXT)", (q,))
    rows = cur.fetchall()
    if not rows:
        print("Ничего не найдено.")
    for row in rows:
        print(row)
 
 
# ─────────────────────────────────────────────
# SORT
# ─────────────────────────────────────────────
def sort_contacts():
    field = input("Сортировать по (name/birthday/created_at): ")
    if field not in ["name", "birthday", "created_at"]:
        field = "name"
    cur.execute(f"""
        SELECT name, phone, email, birthday
        FROM phonebook
        ORDER BY {field}
    """)
    for row in cur.fetchall():
        print(row)
 
 
# ─────────────────────────────────────────────
# PAGINATION
# ─────────────────────────────────────────────
def paginate():
    limit  = 3
    offset = 0
    while True:
        cur.execute("""
            SELECT name, phone, email
            FROM phonebook
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cur.fetchall()
        if not rows:
            print("Больше данных нет.")
            break
        for r in rows:
            print(r)
        cmd = input("next / prev / quit: ")
        if cmd == "next":
            offset += limit
        elif cmd == "prev":
            offset = max(0, offset - limit)
        else:
            break
 
 
# ─────────────────────────────────────────────
# EXPORT JSON
# ─────────────────────────────────────────────
def export_json():
    cur.execute("""
        SELECT p.name, p.phone, p.email, p.birthday, g.name
        FROM phonebook p
        LEFT JOIN groups g ON p.group_id = g.id
    """)
    data = []
    for row in cur.fetchall():
        data.append({
            "name":     row[0],
            "phone":    row[1],
            "email":    row[2],
            "birthday": str(row[3]),
            "group":    row[4]
        })
    with open("contacts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Экспортировано {len(data)} контакт(ов) в contacts.json.")
 
 
# ─────────────────────────────────────────────
# IMPORT JSON
# ─────────────────────────────────────────────
def import_json():
    try:
        with open("contacts.json", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Файл contacts.json не найден.")
        return
 
    imported = 0
    for c in data:
        gid = get_group_id(c["group"])
        cur.execute("SELECT id FROM phonebook WHERE name=%s", (c["name"],))
        if cur.fetchone():
            choice = input(f"{c['name']} уже существует (skip/overwrite): ")
            if choice == "skip":
                continue
            cur.execute("DELETE FROM phonebook WHERE name=%s", (c["name"],))
        cur.execute("""
            INSERT INTO phonebook(name, phone, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (c["name"], c["phone"], c["email"], c["birthday"], gid))
        imported += 1
 
    conn.commit()
    print(f"Импортировано {imported} контакт(ов).")
 
 
# ─────────────────────────────────────────────
# DELETE CONTACT
# ─────────────────────────────────────────────
def delete_contact():
    name = input("Имя для удаления: ")
    try:
        cur.execute("CALL delete_contact(%s)", (name,))
        conn.commit()
        print("Удалено.")
    except Exception as e:
        conn.rollback()
        print("Ошибка:", e)
 
 
# ─────────────────────────────────────────────
# IMPORT FROM CSV
# ─────────────────────────────────────────────
def insert_from_csv(filepath: str):
    query = """
        INSERT INTO phonebook (name, phone)
        VALUES (%s, %s)
        ON CONFLICT (phone) DO UPDATE SET name = EXCLUDED.name;
    """
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [(row["name"].strip(), row["phone"].strip()) for row in reader]
        cur.executemany(query, rows)
        conn.commit()
        print(f"Вставлено/обновлено {cur.rowcount} запис(ей) из '{filepath}'.")
    except FileNotFoundError:
        print(f"Файл '{filepath}' не найден.")
    except KeyError as e:
        print(f"Колонка {e} не найдена в CSV.")
 
 
# ─────────────────────────────────────────────
# MENU
# ─────────────────────────────────────────────
def menu():
    while True:
        print('=' * 50)
        print("Phonebook — доступные операции:")
        print('=' * 50)
        print("""
1  Добавить контакт
2  Добавить телефон
3  Фильтр по группе
4  Поиск
5  Сортировка
6  Пагинация
7  Экспорт JSON
8  Импорт JSON
9  Удалить контакт
10 Импорт из CSV
0  Выход
""")
        ch = input("Выберите: ")
 
        if   ch == "1":  add_contact()
        elif ch == "2":  add_phone()
        elif ch == "3":  filter_group()
        elif ch == "4":  search()
        elif ch == "5":  sort_contacts()
        elif ch == "6":  paginate()
        elif ch == "7":  export_json()
        elif ch == "8":  import_json()
        elif ch == "9":  delete_contact()
        elif ch == "10":
            filepath = input("Путь к CSV файлу: ")
            insert_from_csv(filepath)
        elif ch == "0":
            print('=' * 50)
            print("Программа закрывается...")
            print('=' * 50)
            break
        else:
            print("!=" * 19)
            print("Такой операции нет.")
            print("!=" * 19)
init_db()
menu()