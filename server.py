from mcp.server.fastmcp import FastMCP
from db import get_connection
import json

# Initialize FastMCP server
mcp = FastMCP("sql-assistant")


# ─────────────────────────────────────────────
# TOOL 1: list_tables
# ─────────────────────────────────────────────
@mcp.tool()
def list_tables() -> str:
    """
    List all user-created tables in the connected MS SQL database.
    Returns table names along with their schema.
    """
    query = """
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "No tables found in the database."

        result = "Tables in database:\n\n"
        for schema, table in rows:
            result += f"  [{schema}].[{table}]\n"
        return result

    except Exception as e:
        return f"Error fetching tables: {str(e)}"


# ─────────────────────────────────────────────
# TOOL 2: describe_table
# ─────────────────────────────────────────────
@mcp.tool()
def describe_table(table_name: str, schema: str = "dbo") -> str:
    """
    Describe the structure of a specific table — columns, data types, nullability.

    Args:
        table_name: Name of the table (e.g. Customers)
        schema: Schema name, default is 'dbo'
    """
    query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ? AND TABLE_SCHEMA = ?
        ORDER BY ORDINAL_POSITION
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (table_name, schema))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"Table [{schema}].[{table_name}] not found or has no columns."

        result = f"Structure of [{schema}].[{table_name}]:\n\n"

        for col_name, data_type, max_len, nullable, default in rows:
            max_len = max_len if max_len else "-"
            default = default if default else "-"
            
            result += f"{col_name} | {data_type} | {max_len} | {nullable} | {default}\n"

        return result

    except Exception as e:
        return f"Error describing table: {str(e)}"


# ─────────────────────────────────────────────
# TOOL 3: run_query
# ─────────────────────────────────────────────
@mcp.tool()
def run_query(sql: str, max_rows: int = 50) -> str:
    """
    Run a SELECT SQL query on the MS SQL database and return results.
    Only SELECT statements are allowed for safety.

    Args:
        sql: A valid T-SQL SELECT query
        max_rows: Maximum rows to return (default 50, max 200)
    """
    # Safety check — block destructive statements
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE", "EXEC"]
    sql_upper = sql.strip().upper()

    for keyword in forbidden:
        if sql_upper.startswith(keyword) or f" {keyword} " in sql_upper:
            return f"❌ '{keyword}' statements are not allowed. Only SELECT queries are permitted."

    max_rows = min(max_rows, 200)  # hard cap

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchmany(max_rows)
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        if not rows:
            return "Query executed successfully. No rows returned."

        # Format as a readable table
        col_widths = [max(len(str(col)), max((len(str(row[i])) for row in rows), default=0)) for i, col in enumerate(columns)]

        header = " | ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns))
        separator = "-+-".join("-" * w for w in col_widths)
        result_lines = [header, separator]

        for row in rows:
            line = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
            result_lines.append(line)

        result_lines.append(f"\n({len(rows)} rows returned)")
        return "\n".join(result_lines)

    except Exception as e:
        return f"Query error: {str(e)}"


# ─────────────────────────────────────────────
# TOOL 4: explain_query
# ─────────────────────────────────────────────
@mcp.tool()
def explain_query(sql: str) -> str:
    """
    Show the estimated execution plan for a SELECT query using SET SHOWPLAN_TEXT.
    Helps understand how SQL Server processes the query.

    Args:
        sql: A valid T-SQL SELECT query to explain
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SET SHOWPLAN_TEXT ON")
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.execute("SET SHOWPLAN_TEXT OFF")
        conn.close()

        if not rows:
            return "No execution plan returned."

        plan_lines = [str(row[0]) for row in rows]
        return "Execution Plan:\n\n" + "\n".join(plan_lines)

    except Exception as e:
        return f"Error fetching execution plan: {str(e)}"


# ─────────────────────────────────────────────
# TOOL 5: get_table_sample
# ─────────────────────────────────────────────
@mcp.tool()
def get_table_sample(table_name: str, schema: str = "dbo", rows: int = 5) -> str:
    """
    Preview the first N rows of any table quickly.

    Args:
        table_name: Name of the table
        schema: Schema name, default is 'dbo'
        rows: Number of rows to preview (default 5)
    """
    sql = f"SELECT TOP {min(rows, 20)} * FROM [{schema}].[{table_name}]"
    return run_query(sql)


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()