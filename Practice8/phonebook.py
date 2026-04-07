import psycopg2 
import csv
from psycopg2 import sql
from connect import get_connection, get_cursor
 
def create_table(cursor, conn):
    """Создаёт таблицу contacts если её нет"""
    query = """
    CREATE TABLE IF NOT EXISTS contacts(
        name VARCHAR(100),
        phone VARCHAR(20) UNIQUE
    )
    """
    cursor.execute(query)
    conn.commit()
    print("Таблица contacts готова к работе")
 
 
def all_contacts(cursor, conn):
    """Возвращает все контакты из базы данных"""
    query = "SELECT name, phone FROM contacts ORDER BY name"
    cursor.execute(query)
    result = cursor.fetchall()
    return result
 
 
def add_contact(cursor, conn, name, phone):
    """
    Добавляет или обновляет контакт используя процедуру upsert_contact
    Если контакт существует - обновляет телефон
    """
    try:
        cursor.execute("CALL upsert_contact(%s, %s)", (name, phone))
        conn.commit()
        print("=" * 50)
        print(f'✓ Операция выполнена для контакта {name}')
        print("=" * 50)
    except Exception as e:
        conn.rollback()
        print("=" * 50)
        print(f"Ошибка при добавлении контакта: {e}")
        print("=" * 50)
 
 
def csv_add_contact(cursor, conn):
    """Импортирует контакты из CSV файла"""
    print("=" * 50)
    filename = input("Название файла (пример - contacts.csv): ")
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
        print("Все контакты из файла обработаны")
        print("=" * 50)
    except FileNotFoundError:
        print("=" * 50)
        print(f"Файл {filename} не найден")
        print("=" * 50)
    except Exception as e:
        print("=" * 50)
        print(f"Ошибка при чтении файла: {e}")
        print("=" * 50)
 
 
def search_by_pattern(cursor, conn):
    print("=" * 50)
    pattern = input("Введите паттерн для поиска (имя или часть телефона): ")
    print("=" * 50)
    
    try:
        cursor.execute("SELECT * FROM search_contacts_by_pattern(%s)", (pattern,))
        result = cursor.fetchall()
        
        if result:
            print("=" * 50)
            print(f"НАЙДЕНО КОНТАКТОВ: {len(result)}")
            for name, phone in result:
                print(f"  {name} - {phone}")
            print("=" * 50)
            return result
        else:
            print("=" * 50)
            print(f"Контакты с паттерном '{pattern}' не найдены")
            print("=" * 50)
            return None
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        return None
 
 
def get_paginated_contacts(cursor, conn):

    print("=" * 50)
    try:
        page_size = int(input("Введите количество записей на странице: "))
        page_number = int(input("Введите номер страницы: "))
    except ValueError:
        print("Некорректные данные")
        print("=" * 50)
        return None
    
    print("=" * 50)
    
    try:
        cursor.execute("SELECT * FROM get_contacts_paginated(%s, %s)", 
                      (page_size, page_number))
        result = cursor.fetchall()
        
        if result:
            print("=" * 50)
            print(f"СТРАНИЦА {page_number} (по {page_size} записей):")
            for name, phone in result:
                print(f"  {name} - {phone}")
            print("=" * 50)
            return result
        else:
            print("=" * 50)
            print(f"На странице {page_number} нет записей")
            print("=" * 50)
            return None
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None
 
 
def delete_contact_menu(cursor, conn):
    """
    Меню удаления контакта используя процедуру delete_contact
    """
    print("=" * 50)
    print("УДАЛЕНИЕ КОНТАКТА")
    print("1. Удалить по имени")
    print("2. Удалить по телефону")
    print("3. Удалить по имени И телефону")
    print("4. Назад")
    print("=" * 50)
    
    try:
        choice = int(input("Выберите вариант: "))
    except ValueError:
        print("Это не номер операции")
        return
    
    try:
        if choice == 1:
            name = input("Введите имя для удаления: ")
            cursor.execute("CALL delete_contact(p_name := %s)", (name,))
            conn.commit()
        elif choice == 2:
            phone = input("Введите телефон для удаления: ")
            cursor.execute("CALL delete_contact(p_phone := %s)", (phone,))
            conn.commit()
        elif choice == 3:
            name = input("Введите имя: ")
            phone = input("Введите телефон: ")
            cursor.execute("CALL delete_contact(%s, %s)", (name, phone))
            conn.commit()
        elif choice == 4:
            return
        else:
            print("Неверный выбор")
            return
        
        print("=" * 50)
        print("✓ Операция удаления выполнена")
        print("=" * 50)
    except Exception as e:
        conn.rollback()
        print("=" * 50)
        print(f"Ошибка при удалении: {e}")
        print("=" * 50)
 
 
def insert_multiple_contacts_menu(cursor, conn):
    """
    Вставка множества контактов с валидацией
    Использует функцию insert_multiple_contacts
    """
    print("=" * 50)
    print("МАССОВОЕ ДОБАВЛЕНИЕ КОНТАКТОВ")
    print("Введите контакты в формате: имя;телефон")
    print("Для завершения ввода введите пустую строку")
    print("=" * 50)
    
    names = []
    phones = []
    
    while True:
        line = input("Контакт (имя;телефон) или Enter для завершения: ")
        if not line:
            break
        
        parts = line.split(';')
        if len(parts) != 2:
            print("Неверный формат. Используйте: имя;телефон")
            continue
        
        names.append(parts[0].strip())
        phones.append(parts[1].strip())
    
    if not names:
        print("Нет данных для добавления")
        return
    
    try:
        cursor.execute(
            "SELECT * FROM insert_multiple_contacts(%s, %s)",
            (names, phones)
        )
        results = cursor.fetchall()
        conn.commit()
        
        print("=" * 50)
        print("РЕЗУЛЬТАТЫ МАССОВОГО ДОБАВЛЕНИЯ:")
        print("=" * 50)
        
        success_count = 0
        error_count = 0
        
        for status, name, phone, message in results:
            if status == 'SUCCESS':
                success_count += 1
                print(f"added {name} ({phone}): {message}")
            else:
                error_count += 1
                print(f"added {name} ({phone}): {message}")
        
        print("=" * 50)
        print(f"Успешно добавлено: {success_count}")
        print(f"Ошибок/дубликатов: {error_count}")
        print("=" * 50)
        
    except Exception as e:
        conn.rollback()
        print("=" * 50)
        print(f"Ошибка при массовом добавлении: {e}")
        print("=" * 50)
 
 
def export_to_csv(cursor):
    print("=" * 50)
    filename = input("Введите название файла (например, export.csv): ")
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
 
 
def main():
    """Главное интерактивное меню"""
    print("=" * 50)
    print("📞 ТЕЛЕФОННАЯ КНИГА PostgreSQL")
    print("   Версия 2.0 с функциями и процедурами")
    print("=" * 50)
    
    conn = get_connection()
    if not conn:
        print("Не удалось подключиться к базе данных")
        print("Проверьте настройки в config.py")
        return
    
    cursor = get_cursor(conn)
    if not cursor:
        print("Не удалось создать курсор")
        return
    
    create_table(cursor, conn)
    
    while True:
        print("=" * 50)
        print("ГЛАВНОЕ МЕНЮ:")
        print("=" * 50)
        print("1.  Просмотреть все контакты")
        print("2.  Добавить/обновить контакт (upsert)")
        print("3.  Импортировать контакты из CSV")
        print("4.  Поиск по паттерну (функция)")
        print("5.  Просмотр с пагинацией (функция)")
        print("6.  Массовое добавление (процедура)")
        print("7.  Удалить контакт (процедура)")
        print("8.  Экспортировать в CSV")
        print("9.  Выход")
        print("=" * 50)
        
        try:
            func = int(input("Введите номер операции: "))
        except ValueError:
            print("Это не номер операции")
            continue
        
        if func == 1:
            contacts = all_contacts(cursor, conn)
            print("=" * 50)
            print(f"ВСЕГО КОНТАКТОВ В БАЗЕ: {len(contacts)}")
            print("=" * 50)
            for name, phone in contacts:
                print(f"  {name} - {phone}")
            print("=" * 50)
            
        elif func == 2:
            print("=" * 50)
            name = input("Введите имя контакта: ")
            phone = input("Введите номер контакта: ")
            print("=" * 50)
            add_contact(cursor, conn, name, phone)
            
        elif func == 3:
            csv_add_contact(cursor, conn)
            
        elif func == 4:
            search_by_pattern(cursor, conn)
            
        elif func == 5:
            get_paginated_contacts(cursor, conn)
            
        elif func == 6:
            insert_multiple_contacts_menu(cursor, conn)
            
        elif func == 7:
            delete_contact_menu(cursor, conn)
            
        elif func == 8:
            export_to_csv(cursor)
            
        elif func == 9:
            print("=" * 50)
            print("Выход из программы...")
            print("=" * 50)
            cursor.close()
            conn.close()
            break
            
        else:
            print("=" * 50)
            print("Такой операции нет в меню")
            print("=" * 50)
 
 
if __name__ == "__main__":
    main()
 