import pytest 

from sql_tools import SQLTools, get_connection
from sql_agent import create_agent, SQLAgentConfig
from tests.utils import run_agent_test

from tests.judge import assert_criteria


@pytest.fixture(scope="module")
def agent():
    con = get_connection()
    tools = SQLTools(con)
    agent_config = SQLAgentConfig()
    return create_agent(agent_config, tools)


@pytest.mark.asyncio
async def test_agent_uses_tools(agent):
    user_prompt = 'Which hour of the day has the highest average fare amount?'
    result = await run_agent_test(agent, user_prompt)

    await assert_criteria(result, [
        "makes at least 2 tool calls",
        "Return schema information for the trips table using the 'get_schema' tool",
        "Execute a SQL query using 'run_sql' tool",
    ])
    
    print("\n=== TEST 1 OUTPUT ===")
    print(result.output)

@pytest.mark.asyncio
async def test_average_tip_credit_card(agent):
    user_prompt = (
        "What is the average tip amount for credit card payments?"
    )

    result = await run_agent_test(agent, user_prompt)

    await assert_criteria(result, [
        "makes at least 2 tool calls",
        "Uses the get_schema tool before querying",
        "Uses the run_sql tool to calculate the average tip amount",
        "Filters for credit card payments",
        "Returns a numeric average tip amount",
    ])

    print("\n=== TEST 2 OUTPUT ===")
    print(result.output)


@pytest.mark.asyncio
async def test_most_common_pickup_location(agent):
    user_prompt = (
        "Which pickup location (PULocationID) has the most trips?"
    )

    result = await run_agent_test(agent, user_prompt)

    await assert_criteria(result, [
        "makes at least 2 tool calls",
        "Uses the get_schema tool before querying",
        "Uses the run_sql tool",
        "Groups trips by PULocationID",
        "Counts the number of trips per pickup location",
        "Returns the pickup location with the highest trip count",
    ])

    print("\n=== TEST 3 OUTPUT ===")
    print(result.output)
    

@pytest.mark.asyncio
async def test_average_fare_long_trips(agent):
    user_prompt = (
        "What is the average fare for trips longer than 10 miles?"
    )

    result = await run_agent_test(agent, user_prompt)

    await assert_criteria(result, [
        "makes at least 2 tool calls",
        "Uses the get_schema tool before querying",
        "Uses the run_sql tool",
        "Filters trips longer than 10 miles",
        "Calculates the average fare amount",
        "Returns a numeric average fare",
    ])

    print("\n=== TEST 4 OUTPUT ===")
    print(result.output)


@pytest.mark.asyncio
async def test_zero_passenger_trips(agent):
    user_prompt = (
        "How many trips had zero passengers recorded?"
    )

    result = await run_agent_test(agent, user_prompt)

    await assert_criteria(result, [
        "makes at least 2 tool calls",
        "Uses the get_schema tool before querying",
        "Uses the run_sql tool",
        "Filters trips where passenger_count equals 0",
        "Counts matching trips",
        "Returns the total number of zero-passenger trips",
    ])

    print("\n=== TEST 5 OUTPUT ===")
    print(result.output)


@pytest.mark.asyncio
async def test_busiest_day_of_week(agent):
    user_prompt = (
        "What is the busiest day of the week for taxi trips?"
    )

    result = await run_agent_test(agent, user_prompt)

    await assert_criteria(result, [
        "makes at least 2 tool calls",
        "Uses the get_schema tool before querying",
        "Uses the run_sql tool",
        "Extracts the day of the week from pickup datetime",
        "Counts trips by weekday",
        "Returns the busiest weekday",
    ])

    print("\n=== TEST 6 OUTPUT ===")
    print(result.output)
    
@pytest.mark.asyncio
async def test_zero_passenger_query_uses_correct_column(agent):
    user_prompt = (
        "How many trips had zero passengers recorded?"
    )

    result = await run_agent_test(agent, user_prompt)

    output = result.output

    # Ensure SQL query was generated
    assert output.sql_query is not None
    assert output.sql_query.strip() != ""

    sql = output.sql_query.lower()

    # Correct column should be used
    assert "passenger_count" in sql

    # Ensure incorrect columns are NOT used
    assert "tip_amount" not in sql
    assert "fare_amount" not in sql
    assert "trip_distance" not in sql

    print("\n=== ZERO PASSENGER SQL ===")
    print(output.sql_query)