import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

async def main():
    print("=== [0] CONFIGURING SERVER PARAMETERS ===")
    spotify_server = StdioServerParameters(
        command="python",
        args=["top_songs.py"],
    )
    pr_server = StdioServerParameters(
        command="python",
        args=["pr_analyzer.py"],
    )

    print("=== [1] OPENING STDIO CLIENTS TO BOTH MCP SERVERS ===")
    async with stdio_client(spotify_server) as (spotify_read, spotify_write), \
               stdio_client(pr_server) as (pr_read, pr_write):

        print("=== [2] OPENING CLIENT SESSIONS ===")
        async with ClientSession(spotify_read, spotify_write) as spotify_session, \
                   ClientSession(pr_read, pr_write) as pr_session:

            print("    ...initializing Spotify MCP session")
            await spotify_session.initialize()
            print("    ...Spotify session initialized")

            print("    ...initializing PR Analyzer MCP session")
            await pr_session.initialize()
            print("    ...PR Analyzer session initialized")

            print("=== [3] LOADING TOOLS FROM BOTH SERVERS ===")
            spotify_tools = await load_mcp_tools(spotify_session)
            print(f"    ...Loaded {len(spotify_tools)} tools from Spotify MCP: {[tool.name for tool in spotify_tools]}")
            pr_tools = await load_mcp_tools(pr_session)
            print(f"    ...Loaded {len(pr_tools)} tools from PR Analyzer MCP: {[tool.name for tool in pr_tools]}")

            all_tools = spotify_tools + pr_tools
            print("    ...Total combined tools:", [tool.name for tool in all_tools])

            print("=== [4] INITIALIZING LANGCHAIN MODEL AND AGENT ===")
            model = ChatOpenAI(model="gpt-4.1-nano-2025-04-14", temperature=0.5)
            print("    ...Model loaded")

            system_message = SystemMessage(content="You are an assistant with access to Spotify and GitHub PR tools.")
            agent = create_react_agent(model, all_tools)
            print("    ...Agent created with all tools")

            print("=== [5] INVOKING AGENT WITH TEST QUESTION ===")
            user_msg = (
                "What are the top tracks for Taylor Swift? "
                "And also summarize the PR https://github.com/openai/openai-cs-agents-demo/pull/2"
            )
            print(f"    ...Sending to agent: {user_msg}")

            response = await agent.ainvoke({
                "messages": [
                    system_message,
                    HumanMessage(content=user_msg)
                ]
            })

            print("=== [6] PRINTING AGENT RESPONSE MESSAGES ===")
            for i, msg in enumerate(response["messages"]):
                print(f"    [message {i}] {msg.__class__.__name__}: {getattr(msg, 'content', '')}")
                # Optionally print ToolMessage details
                if hasattr(msg, "name"):
                    print(f"        ToolName: {msg.name}")

if __name__ == "__main__":
    try:
        print("====== MCP MULTI-SERVER CLIENT STARTUP ======")
        asyncio.run(main())
        print("====== MCP MULTI-SERVER CLIENT FINISHED ======")
    except Exception as e:
        print(f"[FATAL] Exception at top-level: {e}")
