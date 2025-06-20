# langgraph-mcp-multitool

A demo project for using multiple MCP tool servers with LangGraph, LangChain, and OpenAI models.

This project lets you run a single AI agent that can use tools from both a Spotify top songs tool server and a GitHub PR analysis tool server, all in one query!

---

## Features

- 🔗 **Combines tools from multiple MCP servers** (Spotify and GitHub PR analysis)
- 🧠 **Uses LangGraph and LangChain agent logic** for reasoning and tool use
- 🛠️ **Easily extend** to more tool servers or custom tools
- 🗣️ **Ready for integration** with voice/other interfaces

---

## File Overview

- `multiserver_main.py` — Main script to connect to both servers, load tools, and run an agent query
- `pr_analyzer.py` — MCP tool server exposing GitHub PR analysis and Notion page creation tools
- `top_songs.py` — MCP tool server exposing Spotify top track tools

---

## Requirements

- Python 3.9+
- Install dependencies:

```bash
pip install langchain langgraph mcp langchain-mcp-adapters python-dotenv openai requests notion-client
```

- Ensure you have valid API credentials for Spotify and Notion in a `.env` file (see below).

---

## Setup

1. **Clone the repo:**

```bash
git clone https://github.com/aliammar182/langgraph-mcp-multitool.git
cd langgraph-mcp-multitool
```

2. **Create a `.env` file** in the same directory, with:

```env
# For top_songs.py
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# For pr_analyzer.py
NOTION_API_KEY=your_notion_api_key
NOTION_PAGE_ID=your_notion_page_id
```

3. **Install requirements** (see above)

---

## Usage

Run the main script:

```bash
python main.py
```

You'll see debug output for each step and a demonstration of querying both servers/tools at once!

---

## Example Output

```
=== [0] CONFIGURING SERVER PARAMETERS ===
=== [1] OPENING STDIO CLIENTS TO BOTH MCP SERVERS ===
=== [2] OPENING CLIENT SESSIONS ===
    ...initializing Spotify MCP session
    ...Spotify session initialized
    ...initializing PR Analyzer MCP session
    ...PR Analyzer session initialized
=== [3] LOADING TOOLS FROM BOTH SERVERS ===
    ...Loaded 1 tools from Spotify MCP: ['get_top_tracks']
    ...Loaded 2 tools from PR Analyzer MCP: ['fetch_pr', 'create_notion_page']
    ...Total combined tools: ['get_top_tracks', 'fetch_pr', 'create_notion_page']
=== [4] INITIALIZING LANGCHAIN MODEL AND AGENT ===
    ...Model loaded
    ...Agent created with all tools
=== [5] INVOKING AGENT WITH TEST QUESTION ===
    ...Sending to agent: What are the top tracks for Taylor Swift? And also summarize the PR https://github.com/openai/openai-cs-agents-demo/pull/2
=== [6] PRINTING AGENT RESPONSE MESSAGES ===
    [message 0] SystemMessage: ...
    [message 1] HumanMessage: ...
    [message 2] AIMessage: ...
    ...
```

---

## Extending

- **Add more MCP servers** by repeating the session creation/connection and adding their tools to the `all_tools` list.
- You can plug this logic into a LangGraph, LangChain, or custom agentic workflow.
- To add voice or web interfaces, see advanced examples in the LangChain or LangGraph docs.

---

## License

MIT
