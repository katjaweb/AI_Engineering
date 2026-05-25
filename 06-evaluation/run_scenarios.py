import csv
import json
import time
from datetime import datetime

from recipe_agent import agent

MODEL_PRICES = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


def calculate_cost(usage, model="gpt-4o-mini"):
    prices = MODEL_PRICES[model]
    input_cost = (usage.input_tokens / 1_000_000) * prices["input"]
    output_cost = (usage.output_tokens / 1_000_000) * prices["output"]
    return round(input_cost + output_cost, 6)


def run_all():
    with open('scenarios.csv') as f:
        scenarios = list(csv.DictReader(f))

    results = []

    for i, scenario in enumerate(scenarios):
        question = scenario['question']
        print(f"[{i+1}/{len(scenarios)}] {question}")

        start = time.time()
        result = agent.run_sync(question)
        elapsed = time.time() - start
        
        messages = result.all_messages()
        tool_context = []

        for msg in messages:
            for p in getattr(msg, "parts", []):

                if p.__class__.__name__ == "ToolReturnPart":
                    tool_context.append(p.content)

        usage = result.usage()
        cost = calculate_cost(usage)

        results.append({
            'question': question,
            'category': scenario['category'],
            'type': scenario['type'],
            'tool_context': tool_context,
            'output': result.output,
            'execution_time': round(elapsed, 2),
            'tokens': {
                'input_tokens': usage.input_tokens,
                'output_tokens': usage.output_tokens,
                'total_tokens': usage.total_tokens,
            },
            'cost': cost,
        })

        print(f"  Done in {elapsed:.1f}s (${cost})")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    total_cost = sum(r['cost'] for r in results)
    print(f"\nSaved {len(results)} results to {output_file}")
    print(f"Total cost: ${total_cost:.4f}")

if __name__ == "__main__":
    run_all()
