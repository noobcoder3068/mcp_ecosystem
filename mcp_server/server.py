from mcp.server.fastmcp import FastMCP
from db_config import get_db_connection
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()
mcp = FastMCP("SpintlyAssistant")

# ✅ MCP Tool: Fetch all users from the database
@mcp.tool()
def get_all_users() -> list:
    """Returns a list of user names from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"id": row[0], "name": row[1]} for row in rows]
    except Exception as e:
        print("❌ Error fetching users:", e)
        return []

# ✅ MCP Tool: Echo
@mcp.tool()
def echo(message: str) -> str:
    """Returns the same message back."""
    print("🔧 Echo tool triggered")
    return f"Echo: {message}"

if __name__ == "__main__":
    mcp.run()


# the reason why its not runing
# The issue arises from how the MCP server handles input in its default STDIO mode, 
# which is designed for continuous communication with an LLM client over standard input/output streams. 
# When using shell commands like echo '{"tool": ...}' | python server.py, especially on Windows or 
# MINGW terminals, the server does not process or return output as expected because STDIO mode 
# requires a persistent input stream, not a one-shot command. As a result, while internal 
# function calls (like internal.py) work correctly, testing tools via piping fails to yield visible output. 
# To resolve this, we recommend using the FastAPI mode for testing, which allows HTTP-based requests 
# through tools like Postman or curl, making the interface more developer-friendly for debugging and validating MCP tools.
