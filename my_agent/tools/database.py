import os
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from my_agent.config import DB_USER, DB_PASS, DB_NAME, DB_HOST, DB_PORT

_MCP_MYSQL_ENTRY = os.path.join(
    os.getenv("APPDATA", ""),
    "npm", "node_modules", "@benborla29", "mcp-server-mysql", "dist", "index.js",
)

cloud_sql_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="node",
        args=[_MCP_MYSQL_ENTRY],
        env={
            **os.environ,
            "MYSQL_HOST": DB_HOST,
            "MYSQL_PORT": str(DB_PORT),
            "MYSQL_USER": DB_USER,
            "MYSQL_PASS": DB_PASS,
            "MYSQL_DB": DB_NAME,
        },
    )
)
