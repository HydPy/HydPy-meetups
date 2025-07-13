# 🤖 **nanoagents**

---

### _A nano, minimalistic, and lightweight library for building ReACT-based AI agents that use tools to solve tasks._

### **📦 Installation**

```bash
pip install nanoagents
```

### **🕹️ Usage**

```python
from nanoagents import Agent
from groq import Groq

# You can define a function to make any llm call, it should take a string as input.
def call_llm(prompt: str) -> str:
    api_key = "$YOUR_API_KEY"
    client = Groq(api_key=api_key)

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return response.choices[0].message.content


agent = Agent(llm=call_llm)

@agent.tool("add") # Create a tool named "add"
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

result = agent.run("Calculate 2 + 3")
print(result)
```
⚠️  _This is still a work in progress, feel free to contribute!_

