# chatmcp_memory
An MCP server able to give large language models the power to remember.<br/>
Only supports [daodao97/chatmcp](https://github.com/daodao97/chatmcp)

## Principle
[daodao97/chatmcp](https://github.com/daodao97/chatmcp) uses SQLite to store chat history between users and the LLM.
Therefore, chatmcp_memory can directly query SQLite to retrieve previous conversations, achieving memory retrieval.
## Usage
`chatmcp_memory` will attempt to automatically discover the location of `chatmcp.db`. 
Of course, it can also be specified via environment variables.
```
export DB_FILE_PATH=/tmp/chatmcp.db
```
### 1. use with uvx
"mcpServers": {
    "chatmcp_memory": {
        "command": "uvx",
        "args": ["--from", "chatmcp_memory", "chatmcp_memory"]
    }
}

### 2.Install and Run
```
pip install chatmcp_memory
```
#### Method 1: Run with transport 'stdio'
```
python3 -m chatmcp_memory
```
#### Method 2: Run with transport 'streamable-http'
```
python3 -m chatmcp_memory --http --bind="127.0.0.1" --port=8090
```
Server URL: http://127.0.0.1:8090/mcp/

