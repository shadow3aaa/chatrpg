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

async def get_reflex_impact(event_description: str, current_body_state: dict) -> dict | None:
    """
    Calls a compatible API to get the physiological impact of an event.
    Returns a dictionary with the changes, or None if an error occurs.
    """
    if not API_KEY:
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        return None

    system_prompt = """你是一个生理反射模拟器。根据当前身体状态和发生的事件，计算此事件对身体造成的【直接、瞬时】的冲击。

【输出格式要求】:
1. 必须只输出JSON格式。
2. 所有键名必须是小写字母和下划线的组合 (snake_case)。
3. 表示变化的键必须以 '_change' 结尾，表示一次性冲击的键必须以 '_shock' 结尾。
4. 数值必须是数字(integer or float)，而不是字符串。

【输出格式范例】:
{"fullness_change": 50.0, "heart_rate_change": 10.0, "adrenaline_shock": 30.0}

【任务开始】
只输出JSON格式的【状态变化量】。不要输出任何解释。"""
    
    user_prompt = f"""[CURRENT BODY STATE]:
{json.dumps(current_body_state, indent=2)}

[EVENT]:
\"{event_description}\"
"""

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
