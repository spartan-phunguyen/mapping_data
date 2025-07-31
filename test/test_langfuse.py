
import os
from dotenv import load_dotenv
from langfuse import get_client
import json

# Load environment variables from .env file
load_dotenv()

# Create Langfuse client
langfuse = get_client()

# Example: list traces
traces = langfuse.api.trace.list(user_id="ca912546-119f-408c-bc72-a0a2255bf815")

for trace in traces.data:
    print(f"{trace.id} | {trace.name} | {trace.createdAt} | {trace.user_id}")

# print(json.dumps(trace.dict(), indent=2, ensure_ascii=False, default=str))

# trace = langfuse.api.trace.get("2d2ae1d1db7db18c106988ffee5e6b3c")
