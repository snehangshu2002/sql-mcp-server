# SQL Assistant MCP Server

An MCP server that connects Claude to a Microsoft SQL Server database over stdio. Ask Claude to query your database, check table structures, or see how a query runs — without leaving the chat window.

---

## Tools

**list_tables** — Lists every user-created table in the database, grouped by schema.

**describe_table** — Shows columns, data types, nullability, and defaults for a table.

**run_query** — Runs a SELECT query and returns results. Write operations (INSERT, UPDATE, DELETE, DROP, etc.) are blocked.

**explain_query** — Returns SQL Server's estimated execution plan via `SET SHOWPLAN_TEXT`. Useful before running a slow or unfamiliar query.

**get_table_sample** — Returns the first N rows (up to 20) from a table. Default is 5 — pass `rows=10` for more.

---

## Project structure
```
C:/path/to/sql-mcp-server/
├── server.py          # MCP server and tool definitions
├── db.py              # SQL Server connection helper (loads .env)
├── pyproject.toml     # Project metadata and dependencies
├── uv.lock            # Locked dependency versions (uv)
├── .env               # Connection config (not committed)
└── README.md         
```

---

## Setup

### 1. Install dependencies
```bash
pip install mcp[cli] pyodbc python-dotenv
```

You also need the ODBC Driver for SQL Server installed:
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

---

### 2. Configure the database connection

If you're using the Claude Desktop config below, put your credentials in the `env` block — no `.env` file needed.

For local testing only, create a `.env` file:
```env
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=YOUR_SERVER_NAME\\SQLEXPRESS
DB_NAME=your_database_name
```

---

### 3. Register with Claude Desktop

Add this to `claude_desktop_config.json`:
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
        "DB_SERVER": "YOUR_SERVER_NAME\\SQLEXPRESS",
        "DB_NAME": "your_database_name",
        "DB_DRIVER": "ODBC Driver 17 for SQL Server"
      }
    }
  }
}
```

Replace:

- `C:/path/to/sql-mcp-server` → path to the repo on your machine
- `YOUR_SERVER_NAME\\SQLEXPRESS` → your SQL Server instance name
- `your_database_name` → the database you want Claude to access

Restart Claude Desktop after saving.

---

## Usage

With the server running, try asking Claude:

- "What tables are in the database?"
- "Describe the Orders table."
- "Show me 10 rows from Customers."
- "Run: SELECT TOP 5 * FROM Sales.Orders WHERE Status = 'Pending'"
- "Explain this query: SELECT * FROM Products WHERE Price > 100"

---

## Notes

Only SELECT queries run. These are blocked before they reach the database:

`INSERT` `UPDATE` `DELETE` `DROP` `TRUNCATE` `ALTER` `CREATE` `EXEC`

Results cap at 200 rows regardless of `max_rows`.

Don't commit your `.env` file — it has your connection credentials.

---

## Requirements

- Python 3.10+
- SQL Server with ODBC Driver 17 or 18
- Windows (uses Trusted Authentication)
- Claude Desktop with MCP support