import pyodbc
import os
from dotenv import load_dotenv
from pathlib import Path

# Force load .env from the project folder
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# db.py — support both auth modes
def get_connection():
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")   # new
    password = os.getenv("DB_PASSWORD")  # new

    if username and password:
        conn_str = (
            f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
            f"UID={username};PWD={password};TrustServerCertificate=yes;"
        )
    else:
        conn_str = (
            f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
            "Trusted_Connection=yes;TrustServerCertificate=yes;"
        )
    return pyodbc.connect(conn_str)