"""
Module: llm_intent_extraction.py

This module provides an intent classification and parameter extraction system
for a structured assistant using an LLM backend (e.g., Mistral-7B GGUF via llama-cpp).

Functionalities:
- Classifies user input as 'chat' or 'task'
- Extracts structured information (intent + parameters)
- Recovers missing parameters via LLM if not found initially
- Returns final structured task or prompts user for missing info

Dependencies:
- llama-cpp-python
- Python 3.7+

Usage:
  from llm_intent_extraction import extract_intent
  result = extract_intent("What is Bob's attendance for last month?")
  print(result)
"""

import re
from llama_cpp import Llama

# === Load the LLM Model ===
llm = Llama(
    model_path="/content/drive/MyDrive/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=4,
    verbose=False
)

# === Core Config ===
REQUIRED_PARAMS = {
    "Attendance": ["employees", "timeframe"]
}

# === Main Extraction Entry ===
def extract_intent(user_input: str) -> dict:
    prompt = f"""
You're an assistant that classifies user messages into either:
- A **chat** type if it's general conversation (e.g., greetings, small talk).
- A **task** type if it's requesting structured action or information (like attendance, leave, etc.).

Respond in one of the following formats **only**:

type: chat
output: <your natural reply>

OR

type: task
output: intent=<intent_name>, params=<key1=value1, key2=value2, ...>

---
User: "{user_input}"
Your response:
"""

    try:
        output = llm(prompt, max_tokens=256)["choices"][0]["text"].strip()

        if output.startswith("type: chat"):
            content = output[len("type: chat"):].strip().replace("output:", "").strip()
            return {"type": "chat", "output": content}

        elif output.startswith("type: task"):
            content = output[len("type: task"):].strip().replace("output:", "").strip()
            if content.startswith("intent=Attendance"):
                return process_attendance_task(content, user_input)
            return {"type": "task", "raw_output": content}

        else:
            return {"type": "unknown", "raw_output": output}

    except Exception as e:
        return {
            "error": "LLM failed to classify prompt",
            "details": str(e),
            "raw": output if 'output' in locals() else None
        }

# === Attendance Specific Processing ===
def process_attendance_task(raw_output: str, user_input: str) -> dict:
    match = re.match(r"intent=Attendance,\s*params={(.*)}", raw_output)
    if not match:
        return {"error": "Could not parse raw output", "raw_output": raw_output}

    param_string = match.group(1)
    extracted_params = {}

    for pair in param_string.split(","):
        if "=" in pair:
            k, v = map(str.strip, pair.split("="))
            extracted_params.setdefault(k, []).append(v)

    missing = get_missing_params("Attendance", extracted_params)

    for param in missing:
        recovered = extract_single_param(user_input, param)
        if recovered:
            extracted_params[param] = [recovered]

    still_missing = get_missing_params("Attendance", extracted_params)

    if still_missing:
        return {
            "type": "chat",
            "output": f"Could you please provide the following missing info: {', '.join(still_missing)}?"
        }

    return {
        "type": "task",
        "intent": "Attendance",
        "params": extracted_params
    }

# === Util: Required param checker ===
def get_missing_params(intent: str, extracted_params: dict) -> list:
    required = REQUIRED_PARAMS.get(intent, [])
    return [param for param in required if param not in extracted_params or not extracted_params[param]]

# === Util: Ask LLM to recover a specific param ===
def extract_single_param(user_input: str, param: str) -> str:
    prompt = f"""
Extract only the value of `{param}` from this sentence if present.
If not present, return `None`.

Sentence: "{user_input}"
Value:
"""
    output = llm(prompt, max_tokens=64)["choices"][0]["text"].strip()
    return None if output.lower().startswith("none") else output
