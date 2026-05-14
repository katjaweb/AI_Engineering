import asyncio
import logfire
from pydantic_ai import Agent
import questionary
from dotenv import load_dotenv

from opentelemetry import context as otel_context

from trivia_tools import TriviaTools
trivia_tools = TriviaTools()

logfire.configure()
logfire.instrument_pydantic_ai()

load_dotenv()

# print(trivia_tools.get_categories())

instructions = """You are a trivia quizmaster. When asked to play trivia:
1. Use the available tools to fetch trivia questions
2. Ask the player one question at a time with multiple choice options
3. Wait for their answer before moving to the next question
4. When the player answers, explain why the correct answer is correct - add interesting context and facts
5. After all questions, give the final score
"""

trivia_agent = Agent(
    'openai:gpt-4o-mini',
    tools=[trivia_tools.get_categories, trivia_tools.get_questions],
    instructions=instructions,
)

def ask_feedback():
    result = questionary.select(
        "How was the trivia session?",
        choices=["👍 Good", "👎 Bad", "Skip"],
    ).ask()

    if result is None or result == "Skip":
        return None

    return 1 if "Good" in result else -1

async def run(prompt):
    message_history = []

    while True:
        result = await trivia_agent.run(prompt, message_history=message_history)
        
        messages = result.all_messages()

        for m in messages:
            print(m.kind)
            for p in m.parts:
                part_kind = p.part_kind
                if part_kind == 'user-prompt':
                    print('USER:', p.content)
                if part_kind == 'tool-call':
                    print('TOOL CALL:', p.tool_name, p.args)
                if part_kind == 'tool-return':
                    print('TOOL RETURN:', p.tool_name)
                if part_kind == 'text':
                    print(p.content)
            print()
        
        print(result.output)
        message_history = result.all_messages()

        prompt = input("You (write 'stop' to stop): ")
        if not prompt or prompt.lower().strip() == 'stop':
            break


async def tool_call():
    result = await trivia_agent.run("Let's play trivia! Can you give me 3 medium difficulty questions in the Science category?")
    
    messages = result.all_messages()

    for m in messages:
        print(m.kind)
        for p in m.parts:
            part_kind = p.part_kind
            if part_kind == 'user-prompt':
                print('USER:', p.content)
            if part_kind == 'tool-call':
                print('TOOL CALL:', p.tool_name, p.args)
            if part_kind == 'tool-return':
                print('TOOL RETURN:', p.tool_name)
            if part_kind == 'text':
                print(p.content)
        print()
        
async def main():
    with logfire.span("trivia_session"):
        await run("Let's play 5 easy questions from Science & Nature")

        # capture trace context before leaving span
        return otel_context.get_current()


if __name__ == "__main__":
    session_context = asyncio.run(main())

    feedback = ask_feedback()

    if feedback is not None:
        with logfire.attach_context(session_context):
            logfire.info(
                "Trivia feedback received",
                feedback=feedback,
            )
