
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_name VARCHAR(100),
    p_phone VARCHAR(20)
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Проверяем, существует ли контакт с таким именем
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        -- Обновляем телефон существующего контакта
        UPDATE contacts 
        SET phone = p_phone 
        WHERE name = p_name;
        RAISE NOTICE 'Контакт % обновлён. Новый телефон: %', p_name, p_phone;
    ELSE
        -- Добавляем новый контакт
        INSERT INTO contacts (name, phone) VALUES (p_name, p_phone);
        RAISE NOTICE 'Контакт % добавлен с телефоном: %', p_name, p_phone;
    END IF;
END;
$$;
 

CREATE OR REPLACE FUNCTION insert_multiple_contacts(
    names TEXT[],
    phones TEXT[]
)
RETURNS TABLE(
    status TEXT,
    contact_name TEXT,
    contact_phone TEXT,
    error_message TEXT
) AS $$
DECLARE
    i INT;
    current_name TEXT;
    current_phone TEXT;
    is_valid BOOLEAN;
BEGIN

    IF array_length(names, 1) != array_length(phones, 1) THEN
        RETURN QUERY
        SELECT 'ERROR'::TEXT, 
               NULL::TEXT, 
               NULL::TEXT, 
               'Количество имён и телефонов не совпадает'::TEXT;
        RETURN;
    END IF;
 

    FOR i IN 1..array_length(names, 1) LOOP
        current_name := names[i];
        current_phone := phones[i];
        is_valid := TRUE;
        
        IF current_name IS NULL OR trim(current_name) = '' THEN
            is_valid := FALSE;
            RETURN QUERY
            SELECT 'INVALID'::TEXT,
                   current_name,
                   current_phone,
                   'Пустое имя'::TEXT;
            CONTINUE;
        END IF;
        
        IF current_phone IS NULL OR 
           NOT (current_phone ~ '^[+\d\s\-\(\)]{10,20}$') THEN
            is_valid := FALSE;
            RETURN QUERY
            SELECT 'INVALID'::TEXT,
                   current_name,
                   current_phone,
                   'Некорректный формат телефона'::TEXT;
            CONTINUE;
        END IF;
        
        IF is_valid THEN
            BEGIN
                INSERT INTO contacts (name, phone) VALUES (current_name, current_phone);
                RETURN QUERY
                SELECT 'SUCCESS'::TEXT,
                       current_name,
                       current_phone,
                       'Успешно добавлен'::TEXT;
            EXCEPTION
                WHEN unique_violation THEN
                    RETURN QUERY
                    SELECT 'DUPLICATE'::TEXT,
                           current_name,
                           current_phone,
                           'Телефон уже существует'::TEXT;
                WHEN OTHERS THEN
                    RETURN QUERY
                    SELECT 'ERROR'::TEXT,
                           current_name,
                           current_phone,
                           SQLERRM::TEXT;
            END;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE delete_contact(
    p_name VARCHAR(100) DEFAULT NULL,
    p_phone VARCHAR(20) DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    deleted_count INT;
BEGIN

    IF p_name IS NULL AND p_phone IS NULL THEN
        RAISE EXCEPTION 'Необходимо указать имя или телефон для удаления';
    END IF;
    

    IF p_name IS NOT NULL AND p_phone IS NOT NULL THEN
        DELETE FROM contacts 
        WHERE name = p_name AND phone = p_phone;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
    ELSIF p_name IS NOT NULL THEN
        DELETE FROM contacts 
        WHERE name = p_name;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
    ELSE
        DELETE FROM contacts 
        WHERE phone = p_phone;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
    END IF;
    
    IF deleted_count > 0 THEN
        RAISE NOTICE 'Удалено контактов: %', deleted_count;
    ELSE
        RAISE NOTICE 'Контакт не найден';
    END IF;
END;
$$;
