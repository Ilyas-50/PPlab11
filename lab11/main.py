import psycopg2
import csv

DB_NAME = "phonebook_db"
DB_USER = "postgres"
DB_PASSWORD = "hello123"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def setup_simple():
    with connect() as conn:
        with conn.cursor() as cur:
            # create table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50) UNIQUE,
                    phone VARCHAR(20)
                );
            """)
            # search by the pattern
            cur.execute("""
                CREATE OR REPLACE FUNCTION search(pattern TEXT)
                RETURNS TABLE(id INT, first_name TEXT, phone TEXT)
                AS $$
                BEGIN
                    RETURN QUERY
                    SELECT * FROM phonebook
                    WHERE first_name ILIKE '%' || pattern || '%'
                    OR phone ILIKE '%' || pattern || '%';
                END;
                $$ LANGUAGE plpgsql;
            """)
            # Простая вставка с обновлением
            cur.execute("""
                CREATE OR REPLACE PROCEDURE insert_or_update(name TEXT, phone TEXT)
                LANGUAGE plpgsql AS $$
                BEGIN
                    INSERT INTO phonebook(first_name, phone)
                    VALUES (name, phone)
                    ON CONFLICT (first_name)
                    DO UPDATE SET phone = EXCLUDED.phone;
                END;
                $$;
            """)
            # Удаление по имени или номеру
            cur.execute("""
                CREATE OR REPLACE PROCEDURE delete_simple(val TEXT)
                LANGUAGE plpgsql AS $$
                BEGIN
                    DELETE FROM phonebook WHERE first_name = val OR phone = val;
                END;
                $$;
            """)
        conn.commit()

def add_simple():
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_or_update(%s, %s)", (name, phone))
        conn.commit()

def show_all():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM phonebook")
            for row in cur.fetchall():
                print(row)

def search_simple():
    pattern = input("Enter pattern: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search(%s)", (pattern,))
            for row in cur.fetchall():
                print(row)

def delete_simple():
    val = input("Enter name or phone to delete: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_simple(%s)", (val,))
        conn.commit()

def menu():
    setup_simple()
    while True:
        print("\n1. Add user")
        print("2. Show all")
        print("3. Search")
        print("4. Delete")
        print("5. Exit")

        choice = input("Choice: ")
        if choice == "1":
            add_simple()
        elif choice == "2":
            show_all()
        elif choice == "3":
            search_simple()
        elif choice == "4":
            delete_simple()
        elif choice == "5":
            break
        else:
            print("Wrong input!")

if __name__ == "__main__":
    menu()
