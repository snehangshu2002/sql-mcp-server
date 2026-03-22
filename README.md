# SQL Assistant MCP Server

Connects Claude to a Microsoft SQL Server database over stdio. Ask Claude to query your database, inspect table structures, or preview execution plans — without leaving the chat.

---

## Installation

```bash
pip install sql-mcp-server
```

You also need the **ODBC Driver for SQL Server**:  
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

---

## Tools

**list_tables** : Lists all user-created tables, grouped by schema.

**describe_table** : Shows columns, data types, nullability, and defaults for a table.

**run_query** : Runs a SELECT query and returns results. Write operations (INSERT, UPDATE, DELETE, DROP, etc.) are blocked.

**explain_query** : Returns SQL Server's estimated execution plan via `SET SHOWPLAN_TEXT`. Good to run before a slow or unfamiliar query.

**get_table_sample** : Returns the first N rows from a table (max 20, default 5). Pass `rows=10` for more.

---

## Project Structure

```
sql-mcp-server/
├── server.py          # MCP server and tool definitions
├── db.py              # SQL Server connection helper (loads .env)
├── pyproject.toml     # Project metadata and dependencies
├── uv.lock            # Locked dependency versions (uv)
├── .env               # Connection config (not committed)
└── README.md
```

---

## Setup

### 1. Configure the database connection

Create a `.env` file in the project root:

**Windows Authentication:**
```env
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=YOUR_SERVER_NAME\SQLEXPRESS
DB_NAME=your_database_name
```

**SQL Server Authentication:**
```env
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=YOUR_SERVER_NAME\SQLEXPRESS
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

If you're using the Claude Desktop config below, put credentials in the `env` block — no `.env` file needed.

---

### 2. Register with Claude Desktop

Add this to `claude_desktop_config.json` — usually at `%APPDATA%\Claude\claude_desktop_config.json` on Windows.

#### Method 1 — Installed from PyPI (Recommended)

**Windows Authentication:**
```json
{
  "mcpServers": {
    "sql-assistant": {
      "command": "sql-mcp-server",
      "args": [],
      "env": {
        "DB_SERVER": "YOUR_SERVER_NAME\\\\SQLEXPRESS",
        "DB_NAME": "your_database_name",
        "DB_DRIVER": "ODBC Driver 17 for SQL Server"
      }
    }
  }
}
```

**SQL Server Authentication:**
```json
{
  "mcpServers": {
    "sql-assistant": {
      "command": "sql-mcp-server",
      "args": [],
      "env": {
        "DB_SERVER": "YOUR_SERVER_NAME\\\\SQLEXPRESS",
        "DB_NAME": "your_database_name",
        "DB_DRIVER": "ODBC Driver 17 for SQL Server",
        "DB_USER": "your_username",
        "DB_PASSWORD": "your_password"
      }
    }
  }
}
```

#### Method 2 — Run with `uvx` (no install)

```json
{
  "mcpServers": {
    "sql-assistant": {
      "command": "uvx",
      "args": ["sql-mcp-server"],
      "env": {
        "DB_SERVER": "YOUR_SERVER_NAME\\\\SQLEXPRESS",
        "DB_NAME": "your_database_name",
        "DB_DRIVER": "ODBC Driver 17 for SQL Server",
        "DB_USER": "your_username",
        "DB_PASSWORD": "your_password"
      }
    }
  }
}
```

#### Method 3 — Local Installation (For Development)

If you cloned the repository and want to run it from source, use `uv` and specify the absolute path to your project directory.

**Windows Authentication:**
```json
{
  "mcpServers": {
    "sql-assistant": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/path/to/sql-mcp-server",
        "run",
        "server.py"
      ],
      "env": {
        "DB_SERVER": "YOUR_SERVER_NAME\\\\SQLEXPRESS",
        "DB_NAME": "your_database_name",
        "DB_DRIVER": "ODBC Driver 17 for SQL Server"
      }
    }
  }
}
```

**SQL Server Authentication:**
```json
{
  "mcpServers": {
    "sql-assistant": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/path/to/sql-mcp-server",
        "run",
        "server.py"
      ],
      "env": {
        "DB_SERVER": "YOUR_SERVER_NAME\\\\SQLEXPRESS",
        "DB_NAME": "your_database_name",
        "DB_DRIVER": "ODBC Driver 17 for SQL Server",
        "DB_USER": "your_username",
        "DB_PASSWORD": "your_password"
      }
    }
  }
}
```

Replace `C:/path/to/sql-mcp-server` with the actual path to your cloned repo.

Replace all placeholder values with your actual credentials. Restart Claude Desktop after saving.

---

## Usage

With the server connected, try asking Claude:

- "What tables are in the database?"
- "Describe the Orders table."
- "Show me 10 rows from Customers."
- "Run: SELECT TOP 5 * FROM Sales.Orders WHERE Status = 'Pending'"
- "Explain this query: SELECT * FROM Products WHERE Price > 100"

---

## Safety

Only SELECT queries run. These keywords are blocked before reaching the database:

`INSERT` `UPDATE` `DELETE` `DROP` `TRUNCATE` `ALTER` `CREATE` `EXEC`

Table and schema names are validated against injection patterns. Results are capped at 200 rows.

> ⚠️ **Don't commit your `.env` file** — it contains your connection credentials.

---

## Requirements

- Python 3.10+
- SQL Server with ODBC Driver 17 or 18
- Claude Desktop with MCP support

---

## License

MIT