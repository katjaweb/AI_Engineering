import pytest

from tests.utils import collect_tools, ToolCall
from sql_tools import SQLTools, setup_database, get_connection
from sql_agent import create_agent, run_agent, SQLAgentConfig, INSTRUCTIONS


def create_test_agent():
    con = get_connection()
    tools = SQLTools(con)

    agent_config = SQLAgentConfig()

    agent = create_agent(agent_config, tools)
    return agent, con


@pytest.mark.asyncio
async def test_agent_runs():
    setup_database()

    agent, con = create_test_agent()

    expected_count = con.execute("""
        SELECT COUNT(*)
        FROM trips
        WHERE passenger_count > 5
    """).fetchone()[0]

    user_prompt = "How many trips had more than 5 passengers?"

    result = await run_agent(agent, user_prompt)

    output = result.output
    
    print("\n=== SQL RESULT ===")
    print("SQL Query:", output.sql_query)
    print("Result Text:", output.result_text)
    print("Row Count:", output.row_count)
    print("==================\n")

    assert output.sql_query is not None
    assert output.sql_query.strip() != ""

    assert output.result_text is not None
    assert output.result_text.strip() != ""

    assert str(expected_count) in output.result_text

    assert output.row_count >= 1

    con.close()
    
@pytest.mark.asyncio
async def test_agent_uses_tools():
    agent, con = create_test_agent()

    user_prompt = 'What is the most common payment type?'
    result = await run_agent(agent, user_prompt)

    messages = result.new_messages()

    tool_calls = collect_tools(messages)
    assert len(tool_calls) >= 2

    search_call = tool_calls[0]
    assert search_call.name == 'get_schema'
    print('First tool call:', search_call.name, search_call.args)

    get_file_call = tool_calls[1]
    assert get_file_call.name == 'run_sql'
    print('Second tool call:', get_file_call.name, get_file_call.args)

print("Test passed!")