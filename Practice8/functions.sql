-- functions.sql
-- SQL-функции для телефонной книги
 
-- 1. Функция поиска записей по паттерну (часть имени или телефона)
-- Возвращает все записи, где имя или телефон содержат указанный паттерн
CREATE OR REPLACE FUNCTION search_contacts_by_pattern(search_pattern TEXT)
RETURNS TABLE(name VARCHAR(100), phone VARCHAR(20)) AS $$
BEGIN
    RETURN QUERY
    SELECT c.name, c.phone
    FROM contacts c
    WHERE c.name ILIKE '%' || search_pattern || '%'
       OR c.phone ILIKE '%' || search_pattern || '%'
    ORDER BY c.name;
END;
$$ LANGUAGE plpgsql;
 
-- Пример использования:
-- SELECT * FROM search_contacts_by_pattern('Иван');
-- SELECT * FROM search_contacts_by_pattern('123');
 
 
-- 4. Функция для получения данных с пагинацией
-- Возвращает записи с учётом лимита и смещения
CREATE OR REPLACE FUNCTION get_contacts_paginated(page_size INT, page_number INT)
RETURNS TABLE(name VARCHAR(100), phone VARCHAR(20)) AS $$
DECLARE
    offset_value INT;
BEGIN
    -- Вычисляем смещение: (номер страницы - 1) * размер страницы
    offset_value := (page_number - 1) * page_size;
    
    RETURN QUERY
    SELECT c.name, c.phone
    FROM contacts c
    ORDER BY c.name
    LIMIT page_size
    OFFSET offset_value;
END;
$$ LANGUAGE plpgsql;
 
-- Пример использования:
-- SELECT * FROM get_contacts_paginated(10, 1);  -- Первая страница, 10 записей
-- SELECT * FROM get_contacts_paginated(5, 2);   -- Вторая страница, 5 записей