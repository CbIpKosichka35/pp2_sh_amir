import psycopg2
from psycopg2 import sql
import csv

def create_table(cursor, conn):
    query =  """
    CREATE TABLE IF NOT EXISTS contacts(
    name VARCHAR(100),
    phone VARCHAR(20) UNIQUE
    )
    """
    cursor.execute(query)
    conn.commit()

"""ФУНКЦИЯ ALL 1 KZKZKZ"""
def all_contacts(cursor, conn):
    query = "SELECT name, phone FROM contacts ORDER BY name"
    cursor.execute(query)
    result = cursor.fetchall()
    return result
"""ФУНКЦИЯ ALL 1 KZKZKZ"""

"""ФУНКЦИЯ ADD 2 KZKZKZ ПРОШЛОЕ"""
"""def add_contact(cursor, conn, name, phone):
    query = "INSERT INTO contacts (name, phone) VALUES (%s, %s)"
    cursor.execute(query, (name, phone))
    conn.commit()
    print("=" * 50)
    print(f'Контакт {name} был успешно добавлен. Телефон: {phone}')
    print("=" * 50)"""
"""ФУНКЦИЯ ADD 2 KZKZKZ ПРОШЛОЕ"""
"""ФУНКЦИЯ ADD 2 KZKZKZ"""
def add_contact(cursor, conn, name, phone):
    try:
        query = "INSERT INTO contacts (name, phone) VALUES (%s, %s)"
        cursor.execute(query, (name, phone))
        conn.commit()
        print("=" * 50)
        print(f'Контакт {name} был успешно добавлен. Телефон: {phone}')
        print("=" * 50)
    except Exception as e:
        conn.rollback()
        print("=" * 50)
        print("Ошибка: такой номер уже существует или проблема с базой")
        print(e)
        print("=" * 50)
"""ФУНКЦИЯ ADD 2 KZKZKZ"""



"""ФУНКЦИЯ CSV ADD 3 KZKZKZ"""
def csv_add_contact(cursor, conn):
    print("=" * 50)
    filename = input("название файла(пример - contacts.csv):" )
    print("=" * 50)
    if not filename:
        filename = "contacts.csv"
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for contact_row in reader:
                name = contact_row.get('name')
                phone = contact_row.get('phone')
                if name and phone:
                    add_contact(cursor, conn, name, phone)
        print("=" * 50)
        print("Все файлы были добавлены")
        print("=" * 50)
    except:
        print("=" * 50)
        print("Такого файла не найдено или есть ошибка")
        print("=" * 50)
"""ФУНКЦИЯ CSV ADD 3 KZKZKZ"""



"""ФУНКЦИЯ SEARCH 4 KZKZKZ"""
def search(cursor, conn):
    print("=" * 50)
    print("1. Поиск по номеру Телефона")
    print("2. Поиск по Имени")
    print("3. go back")
    print("=" * 50)

    try:
        choice = int(input())
    except:
        print("!=" * 19)
        print("это не номер операции, а бред какой-то")
        print("!=" * 19)
        return
    if choice == 1:
        res = search_phone(cursor, conn)
        return res
    elif choice == 2:
        res = search_name(cursor, conn)
        return res
    elif choice == 3:
        return

def search_phone(cursor, conn):
    phone_seaching = input("Введите номер телефона: ")
    query = "SELECT * FROM contacts WHERE phone = %s ORDER by name "
    cursor.execute(query, (phone_seaching,))
    result = cursor.fetchall()
    if result:
        return result
    else:
        print("!=" * 19)
        print(f"Нет такого номера {phone_seaching}")
        print("!=" * 19)
        return


def search_name(cursor, conn):
    name_searching = input("Введите имя: ")
    query = "SELECT * FROM contacts where name = %s ORDER by name"
    cursor.execute(query, (name_searching,))
    result = cursor.fetchall()
    if result:
        return result
    else:
        print("!=" * 19)
        print(f"Нет такого имени {name_searching}")
        print("!=" * 19)
        return
"""ФУНКЦИЯ SEARCH 4 KZKZKZ"""



"""ФУНКЦИЯ UPDATE 5 KZKZKZ"""
def update_contact(cursor, conn):
    print("=" * 50)
    print("ИЗМЕНЕНЕНЕНИЕ ДАННЫХ КОНТАКТА")
    print("=" * 50)
    print("1. Изменить Телефон")
    print("2. Изменить Имя")
    print("3. ВЫйти")
    try:
        choice = int(input())
    except:
        print("!=" * 19)
        print("это не номер операции, а бред какой-то")
        print("!=" * 19)
        return
    if choice == 1:
        res = update_phone(cursor, conn)
        if res:
            return res
        else:
            print("Что-то пошло не так...")
    if choice == 2:
        res = update_name(cursor, conn)
        if res:
            return res
        else:
            print("Что-то пошло не так...")
    if choice == 3:
        return
        
def update_name(cursor, conn):
    print("Найдите контакт для изменения имени:")
    results = search_name(cursor, conn)
    if results:
        old_name, phone = results[0]
        new_name = input(f"Введите новое имя для контакта {old_name} (тел: {phone}): ")

        query = "UPDATE contacts SET name = %s WHERE name = %s AND phone = %s"
        cursor.execute(query, (new_name, old_name, phone))
        conn.commit()
        print("=" * 50)
        print(f"Имя успешно обновлено! с {old_name} на {new_name} (тел. {phone})")
        print("=" * 50)
        return True
    else:
        print("!Ошибка! Данные введены неверно или ошибка в коде")

def update_phone(cursor, conn):
    print("Найдите контакт для изменения имени:")
    results = search_phone(cursor, conn)
    if results:
        name, old_phone = results[0]
        new_phone = input(f"Введите новый телефон для контакта {name} (тел: {old_phone}): ")

        query = "UPDATE contacts SET phone = %s WHERE name = %s AND phone = %s"
        cursor.execute(query, (new_phone, name, old_phone))
        conn.commit()
        print("=" * 50)
        print(f"телефон успешно обновлен! с {old_phone} на {new_phone} (кон. {name})")
        print("=" * 50)
        return True
    else:
        print("!Ошибка! Данные введены неверно или ошибка в коде")
"""ФУНКЦИЯ UPDATE 5 KZKZKZ"""



"""ФУНКЦИЯ DELETE 6 KZKZKZ"""
def delete_con(cursor, conn):
    print("=" * 50)
    print("!Удаление контакта из списка!")
    print("1. Удалить контакт")
    print("2. Назад")
    try:
        choice = int(input())
    except:
        print("!=" * 19)
        print("это не номер операции, а бред какой-то")
        print("!=" * 19)
        return
    print("=" * 50)
    if choice == 1:
        del_contact = input("Введите имя контакта которого хотите удалить: ")
        del_contact_phone = input("Введите номер контакта которого хотите удалить: ")
        query = "DELETE FROM contacts WHERE name = %s AND phone = %s"
        cursor.execute(query, (del_contact, del_contact_phone))
        conn.commit()
        print("=" * 50)
        print(f"Котакт {del_contact} успешно удален!")
        print("=" * 50)
    elif choice == 2:
        return
    else:
        print("!=" * 19)
        print("это не номер операции, а бред какой-то")
        print("!=" * 19)
        return
"""ФУНКЦИЯ DELETE 6 KZKZKZ"""



"""ФУНКЦИЯ EXPORT CSV 7 KZKZKZ"""
def export_to_csv(cursor):
    print("=" * 50)
    filename = input("Введите название файла для сохранения (например, export.csv): ")
    if not filename:
        filename = "contacts_export.csv"
    
    try:
        query = "SELECT name, phone FROM contacts ORDER BY name"
        cursor.execute(query)
        contacts = cursor.fetchall()

        if not contacts:
            print("База данных пуста. Нечего экспортировать.")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['name', 'phone'])
            writer.writerows(contacts)

        print("=" * 50)
        print(f"Данные успешно экспортированы в файл: {filename}")
        print("=" * 50)
    except Exception as e:
        print("=" * 50)
        print(f"Ошибка при экспорте: {e}")
        print("=" * 50)
"""ФУНКЦИЯ EXPORT CSV 7 KZKZKZ"""


def main():
    """Интерактивное меню"""
    print("=" * 50)
    print("Телефонная книга написанная кровью слона из SQL")
    print("=" * 50)
    try:
        conn = psycopg2.connect(
        database="phonebook",
        user="postgres",
        password="adminpp2"
        )
        cursor = conn.cursor()
    except:
        print("УВЫ. ЧТо-то пошло не так")
        print("Перепроверьте данные или не пробуйте снова")
        return
    
    create_table(cursor, conn)
    while True:
        print("1. Просмотреть все контакты")
        print("2. Добавить новый контакт")
        print("3. Импортировать контакты из CSV")
        print("4. Поиск контакта")
        print("5. Обновить контакт")
        print("6. Удалить контакт")
        print("7. Экспортировать в CSV")
        print("8. Выход")
        try:
            func = int(input("Введите номер операции: "))
        except:
            print("!=" * 19)
            print("это не номер операции, а бред какой-то")
            print("!=" * 19)
            continue
        if func == 1:
            contacts = all_contacts(cursor, conn)
            print("=" * 50)
            print("ВСЕ КОНТАКТЫ ЗАНЕСЕННЫЕ В БАЗУ:")
            for name, phone in contacts:
                print(f"{name} - {phone}")
            print("=" * 50)
        elif func == 2:
            print("=" * 50)
            name = input("Введите имя контакта:" )
            phone = input("Введите номер контакта: ")
            print("=" * 50)
            add_contact(cursor, conn, name, phone)
        elif func == 3:
            csv_add_contact(cursor, conn)
        elif func == 4:
            search_res = search(cursor, conn)
            if search_res:
                print("=" * 50)
                print("РЕЗУЛЬТАТЫ ПОИСКА:")
                for name, phone in search_res:
                    print(f"{name} - {phone}")
                print("=" * 50)
        elif func == 5:
            update_contact(cursor, conn)
        elif func == 6:
            delete_con(cursor, conn)
        elif func == 7:
            export_to_csv(cursor) 
        elif func == 8:
            print("Выход из программы...")
            cursor.close()
            conn.close()
            break
        else:
            print("!=" * 19)
            print("Пока такой операции нет")
            print("!=" * 19)
            


if __name__ == "__main__":
    main()