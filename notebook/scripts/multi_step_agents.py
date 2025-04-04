from langchain_ollama import ChatOllama  # type: ignore
from langgraph_agentflow.multi_step import (
    create_multi_step_agent,
    stream_multi_step_agent,
)

from tumkwe_invest.news import TOOL_DESCRIPTION as NEWS_TOOL_DESCRIPTION
from tumkwe_invest.news import tools as news_tools
from tumkwe_invest.sector import TOOL_DESCRIPTION as SECTOR_TOOL_DESCRIPTION
from tumkwe_invest.sector import tools as sector_tools
from tumkwe_invest.ticker import TOOL_DESCRIPTION as TICKER_TOOL_DESCRIPTION
from tumkwe_invest.ticker import tools as ticker_tools

# Initialize LLM
llm = ChatOllama(model="llama3.3", temperature=0.7)

# Create the multi-step agent
graph = create_multi_step_agent(
    llm=llm,
    agent_tools=[
        {
            "name": "news",
            "tools": news_tools,
            "description": NEWS_TOOL_DESCRIPTION,
        },
        {
            "name": "sector",
            "tools": sector_tools,
            "description": SECTOR_TOOL_DESCRIPTION,
        },
        {
            "name": "ticker",
            "tools": ticker_tools,
            "description": TICKER_TOOL_DESCRIPTION,
        },
        {
            "name": "general",
            "description": "Handles general information and queries not specific to other domains",
        },
    ],
)
config = {"configurable": {"thread_id": "user-thread-1"}}

flag = True
while flag:
    try:
        user_input = input("Enter your query (or 'exit' to quit): ")
        if user_input.lower() in ["exit", "quit", "q"]:
            flag = False
            break

        # Stream the agent's response
        for step in stream_multi_step_agent(graph, user_input, config):
            message = step["messages"][-1]
            message.pretty_print()
    except Exception as e:
        print(f"An error occurred: {e}")
