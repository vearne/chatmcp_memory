import logging
import argparse
from fastmcp import FastMCP
from fastmcp.tools.tool import FunctionTool

from chatmcp_memory.remember import remember


def create_mcp() -> FastMCP:
    mcp = FastMCP(name="chatmcp_memory")
    mcp.add_tool(FunctionTool.from_function(remember))
    return mcp

def init_logger():
    logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s", level=logging.INFO)

def main() -> None:
    init_logger()
    logging.info("chatmcp_memory:\nversion：%s", "0.0.5")

    # creating a command line argument parser
    parser = argparse.ArgumentParser(description="An MCP server capable of give large language models the power to remember.")
    parser.add_argument("--bind", default="127.0.0.1", help="Specify the IP address to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8902, help="Specify the port number (default: 8902)")
    parser.add_argument("--http", action="store_true", help="Enable http server")

    # parsing command line arguments
    args = parser.parse_args()

    mcp = create_mcp()
    if args.http:
        mcp.run(transport="streamable-http", host=args.bind, port=args.port)
    else:
        mcp.run()

if __name__ == "__main__":
    main()