import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

# Get model names from environment variables, with sensible defaults
REFLEX_MODEL = os.getenv("REFLEX_MODEL_NAME", "gpt-5")
PERSONA_MODEL = os.getenv("PERSONA_MODEL_NAME", "gpt-5")

async def get_reflex_impact(event_description: str, current_body_state: dict, organs_schema: str | None = None) -> dict | None:
    """
    Calls a compatible API to get the physiological impact of an event.
    Returns a dictionary with the changes, or None if an error occurs.
    """
    if not API_KEY:
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        return None

    schema_prompt_part = ""
    if organs_schema:
        schema_prompt_part = f"""
[ALLOWED ATTRIBUTES SCHEMA]:
You MUST strictly adhere to the following schema. Only use the plugin names and attributes provided below.
{organs_schema}"""

    system_prompt = f"""你是一个生理反射模拟器。根据当前身体状态和发生的事件，计算此事件对身体造成的【直接、瞬时】的冲击。

{schema_prompt_part}
【OUTPUT FORMAT REQUIREMENTS】:
1. MUST only output a JSON object.
2. All top-level keys in the JSON MUST be plugin names as defined in the schema (e.g., "digestive", "circulatory").
3. Each plugin object can only contain attributes listed for it in the schema.
4. Attribute values MUST be strings representing the change, in the format "+=VALUE" or "-=VALUE". VALUE must be a number (integer or float).

【OUTPUT EXAMPLE】:
{{
  "plugin_name_1": {{
    "attribute_name_1": "+=10.0",
    "attribute_name_2": "-=5.0"
  }},
  "plugin_name_2": {{
    "attribute_name_3": "+=25.5"
  }}
}}

【START TASK】
Output ONLY the JSON object representing the state changes. Do not include any explanations.
"""
    
    user_prompt = f"""[CURRENT BODY STATE]:
{json.dumps(current_body_state, indent=2)}

[EVENT]:
\"{event_description}\""""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": REFLEX_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": { "type": "json_object" }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=20.0)
            response.raise_for_status() # Raise an exception for bad status codes
            json_response = response.json()
            # The actual content is a JSON string inside the response, so we parse it again.
            return json.loads(json_response['choices'][0]['message']['content'])
    except (httpx.HTTPStatusError, json.JSONDecodeError, KeyError) as e:
        print(f"Error calling Reflex API: {e}")
        return None


async def get_persona_dialogue(event_description: str, reflex_impact: dict | None, final_body_state: dict, sensations: list[str]) -> str:
    """
    Calls a compatible API to get the persona's dialogue response.
    """
    if not API_KEY:
        return "[ERROR: OPENAI_API_KEY not found]"

    sensation_str = "\n".join(sensations) if sensations else "None"
    impact_str = json.dumps(reflex_impact, indent=2) if reflex_impact else "None"

    system_prompt = """你是一个具有独特个性的女性角色。你名为喵喵。根据当前身体状态、感官体验和发生的事件，生成符合角色个性的对话回应。"""

    user_prompt = f"""[EVENT]:
"{event_description}"\n
[ACTION & RESULT]:
你的身体对该事件的本能反应已经被处理，产生的生理冲击如下：
{impact_str}
你的当前身体状态已经体现了这些变化。

[FINAL BODY STATE]:
{json.dumps(final_body_state, indent=2)}

[CURRENT SENSATIONS]:
{sensation_str}"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": PERSONA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            json_response = response.json()
            return json_response['choices'][0]['message']['content']
    except (httpx.HTTPStatusError, json.JSONDecodeError, KeyError) as e:
        return f"[Error calling Persona API: {e}]"
