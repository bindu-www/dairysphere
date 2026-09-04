import sqlite3
from werkzeug.security import generate_password_hash


DATABASE = "dairy.db"


def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


def create_table():

    connection = get_db_connection()


    # ==============================
    # USERS TABLE
    # ==============================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ==============================
    # BRANDS TABLE
    # ==============================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS brands (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            company_type TEXT NOT NULL,

            headquarters TEXT,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ==============================
    # PRODUCTS TABLE
    # ==============================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS products (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            brand_id INTEGER NOT NULL,

            category TEXT NOT NULL,

            quantity TEXT,

            unit TEXT,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (brand_id)
            REFERENCES brands(id)

        )
    """)


    # ==============================
    # PRODUCTION TABLE
    # ==============================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS production (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_name TEXT NOT NULL,

            location TEXT NOT NULL,

            quantity INTEGER NOT NULL,

            production_date TEXT NOT NULL,

            batch_number TEXT NOT NULL,

            status TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ==============================
    # QUALITY TABLE
    # ==============================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS quality (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_name TEXT NOT NULL,

            batch_number TEXT NOT NULL,

            fat REAL,

            snf REAL,

            test_date TEXT NOT NULL,

            result TEXT NOT NULL,

            remarks TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ==============================
    # PROCESSING TABLE
    # ==============================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS processing (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_name TEXT NOT NULL,

            process_type TEXT NOT NULL,

            input_quantity REAL NOT NULL,

            output_quantity REAL NOT NULL,

            processing_date TEXT NOT NULL,

            facility TEXT NOT NULL,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ==============================
    # PACKAGING TABLE
    # ==============================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS packaging (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_name TEXT NOT NULL,

            package_type TEXT NOT NULL,

            package_size TEXT NOT NULL,

            quantity REAL NOT NULL,

            packaging_date TEXT NOT NULL,

            packaging_unit TEXT,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ==============================
    # DISTRIBUTION TABLE
    # ==============================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS distribution (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_name TEXT NOT NULL,

            quantity REAL NOT NULL,

            unit TEXT NOT NULL,

            source TEXT NOT NULL,

            destination TEXT NOT NULL,

            dispatch_date TEXT NOT NULL,

            transport TEXT,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ==============================
    # RETAIL TABLE
    # ==============================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS retail (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_name TEXT NOT NULL,

            brand TEXT NOT NULL,

            quantity REAL NOT NULL,

            unit TEXT NOT NULL,

            outlet TEXT NOT NULL,

            location TEXT NOT NULL,

            retail_date TEXT NOT NULL,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ==============================
    # CREATE DEFAULT ADMIN
    # ==============================

    admin = connection.execute(
        "SELECT * FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()


    if admin is None:

        password = generate_password_hash("1234")

        connection.execute(
            """
            INSERT INTO users
            (username, password)

            VALUES (?, ?)
            """,
            ("admin", password)
        )

        print("Default admin account created.")


    connection.commit()

    connection.close()