import os
from nanoagents import Agent
from groq import Groq

def call_llm(prompt: str) -> str:
    """Simulate LLM call."""
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    response = client.chat.completions.create(
        model="qwen-2.5-32b",
        messages=messages,
        temperature=0.9,
        max_tokens=2048
    )
    return response.choices[0].message.content

agent = Agent(call_llm)


@agent.tool("add")
def add(a: int, b: int) -> int: """Use this tool to add two numbers"""; return a + b


agent.add_tool("multiply", lambda a, b: a * b, "Use this tool to multiply two numbers")

result = agent.run("Calculate (5184 + 3348432) * 29")
print(result)