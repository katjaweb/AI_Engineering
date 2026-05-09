import asyncio
from dataclasses import dataclass

from pydantic_ai import Agent, AgentRunResult

from sql_tools import SQLTools, SQLResult, get_connection, setup_database

INSTRUCTIONS = """
You are a SQL agent for a NYC taxi trips database that can execute SQL queries against 
a database containing a 'trips' table.

Always inspect the schema first before writing SQL queries.

Use:
- get_schema() to understand the table structure
- run_sql(query) to execute SQL queries

The database contains a table named 'trips'.
""".strip()


@dataclass
class SQLAgentConfig:
    model = 'openai:gpt-4o-mini'
    name = 'sql_agent'
    instructions = INSTRUCTIONS
    

def create_agent(
    config: SQLAgentConfig,
    sql_tools: SQLTools
) -> Agent:

    tools = [
        sql_tools.get_schema,
        sql_tools.run_sql
    ]

    agent = Agent(
        name=config.name,
        model=config.model,
        instructions=config.instructions,
        tools=tools
    )

    return agent


async def run_agent(
    agent: Agent,
    user_prompt: str,
    message_history=None
) -> SQLResult:

    if message_history is None:
        message_history = []

    result = await agent.run(
        user_prompt,
        message_history=message_history,
        output_type=SQLResult
    )

    return result
 
 
async def main():
    # Setup DB
    setup_database()
    
    con = get_connection()
    sql_tools = SQLTools(con)
    
    # Create agent
    config = SQLAgentConfig()
    agent = create_agent(config, sql_tools)
    
    print("SQL Agent ready.")
    print("Type 'exit' to quit.\n")

    message_history = []

    while True:
        user_prompt = input("You: ")

        if user_prompt.lower() in ["exit", "quit"]:
            break

        try:
            result = await run_agent(
                agent=agent,
                user_prompt=user_prompt,
                message_history=message_history
            )

            print("\nAgent:")
            print(result)
            print()

            message_history.extend(result.new_messages())

        except Exception as e:
            print(f"\nError: {e}\n")
         
        con.close()


if __name__ == "__main__":
   import asyncio
   asyncio.run(main())
