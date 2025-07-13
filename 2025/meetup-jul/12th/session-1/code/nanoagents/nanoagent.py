import inspect
import json
import re
from typing import Callable, Dict, List, Optional


def _parse_schema(func):
    """Parse function signature for schema."""
    return [{'name': n, 'type': p.annotation.__name__ if p.annotation != inspect.Parameter.empty else 'str'}
            for n, p in inspect.signature(func).parameters.items() if n != 'self']


class Tool:
    """Represents an agent tool."""

    def __init__(self, name: str, func: Callable, desc: str = None):
        self.name = name
        self.func = func
        self.desc = desc or func.__doc__.strip() or f"{name} tool"
        self.schema = _parse_schema(func)

    def execute(self, **kwargs): return self.func(**kwargs)

    def __str__(self): return f"Tool: {self.name}\nDesc: {self.desc}\nArgs: {self.schema}"


class ToolRegistry:
    """Manages tool collection."""

    def __init__(self): self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool): self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]: return self.tools.get(name)

    def list(self) -> str: return "\n\n".join(map(str, self.tools.values()))

    def decorator(self, name: str, desc: str = None):
        def wrap(func):
            self.register(Tool(name, func, desc))
            return func

        return wrap


class Step:
    """Single reasoning step."""

    def __init__(self, thought: str, index: int = 1):
        self.index = index
        self.thought = thought
        self.action = None
        self.input = None
        self.obs = None

    def set_action(self, action: str, input: dict): self.action, self.input = action, input

    def set_obs(self, obs: str): self.obs = obs

    def __str__(self):
        return f"\n--- Iteration:{self.index} ---\nthought: {self.thought}\n" + \
            (f"action: {self.action}\n" if self.action else "") + \
            (f"action_input: {self.input}\n" if self.input else "") + \
            (f"observation: {self.obs}\n" if self.obs else "")


class ResponseParser:
    """Parses LLM responses."""

    @staticmethod
    def parse(text: str) -> dict:
        if match := re.search(r"```json([\s\S]*?)```", text, re.DOTALL):
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        return {"thought": text, "action": "", "action_input": ""}


class PromptFormatter:
    """Formats LLM prompts."""

    @staticmethod
    def format(task: str, tools: ToolRegistry, history: List[Step]) -> str:
        return f"""
You are an AI agent tasked with {task}. Use critical reasoning and these tools:

Tools:
{tools.list()}

Respond with JSON in markdown code block format:
  "thought": <your internal reasoning>,
  "action": <tool name>,
  "action_input": <params as JSON string>
  "final_answer": <when you have the final answer after a few iterations, provide it here>

History:
{"".join(map(str, history)) if history else "No history present, this is the first iteration"}

Important: Provide only valid JSON without any introduction, explanation, or additional text. No Preamble.
""".strip()


class Agent:
    """ReACT-based agent with retry mechanism."""

    def __init__(self, llm: Callable[[str], str], max_steps: int = 10, max_retries: int = 3):
        self.llm, self.max_steps, self.max_retries = llm, max_steps, max_retries
        self.registry, self.parser = ToolRegistry(), ResponseParser()

    def tool(self, name: str):
        return self.registry.decorator(name)

    def add_tool(self, name: str, func: Callable, desc: str = None):
        self.registry.register(Tool(name, func, desc))

    def _execute_with_retry(self, tool: Tool, inputs: dict) -> str:
        for attempt in range(self.max_retries):
            try:
                return str(tool.execute(**inputs))
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return f"Error after {self.max_retries} retries: {e}"
                continue
        return "Unexpected retry failure"

    def _retry_llm(self, prompt: str, prev_response: str = None) -> dict:
        for attempt in range(self.max_retries):
            if attempt > 0:
                retry_prompt = f"""
Your previous response was not in the correct JSON format:
{prev_response}

Please provide a valid JSON response as specified in the original prompt:
{prompt}
"""
                response = re.sub(r'<think>.*?</think>', '', self.llm(retry_prompt), flags=re.DOTALL)
                resp_dict = self.parser.parse(response)
                if resp_dict.get("thought") and (resp_dict.get("action") or resp_dict.get("final_answer")):
                    print(f"\n{15 * '='} LLM Response After Retrying {15 * '='}\n{response}\n\n")
                    return resp_dict
                prev_response = response
        raise Exception("Max retries reached")

    def run(self, task: str) -> str:
        history: List[Step] = []
        for i in range(self.max_steps):
            prompt = PromptFormatter.format(task, self.registry, history)
            print(f'\nIteration: {i + 1}\n{15 * "="} PROMPT {15 * "="}\n{prompt}\n')

            response = re.sub(r'<think>.*?</think>', '', self.llm(prompt), flags=re.DOTALL)
            print(f"\n{15 * '='} LLM Response {15 * '='}\n{response}\n\n")
            resp_dict = self.parser.parse(response)

            if not (thought := resp_dict.get("thought") and (resp_dict.get("action") or resp_dict.get("final_answer"))):
                resp_dict = self._retry_llm(prompt, response)

            step = Step(thought, i + 1)
            history.append(step)

            if final := resp_dict.get("final_answer"):
                return final

            if action := resp_dict.get("action"):
                inputs = resp_dict["action_input"] if isinstance(resp_dict["action_input"], dict) else json.loads(
                    resp_dict["action_input"])
                tool = self.registry.get(action)
                obs = self._execute_with_retry(tool, inputs) if tool else f"Tool '{action}' not found"
                step.set_action(action, inputs)
                step.set_obs(obs)
            else:
                raise Exception("No action or final answer")

        raise Exception("Max steps reached")
