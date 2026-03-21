import pyodbc
import os
from dotenv import load_dotenv
from pathlib import Path

# Force load .env from the project folder
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

def get_connection():
    driver = os.getenv("DB_DRIVER")
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")

    # Debug check
    if not all([driver, server, database]):
        raise ValueError(f"Missing env vars — DRIVER: {driver}, SERVER: {server}, DB: {database}")

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)