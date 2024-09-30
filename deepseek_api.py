import requests
import json
from typing import Iterator, Tuple

API_KEY = None
API_URL = "https://api.deepseek.com/v1/chat/completions"

def set_api_key(key: str):
    global API_KEY
    API_KEY = key

def generate_response(prompt: str, use_cot: bool) -> Iterator[str]:
    if not API_KEY:
        raise ValueError("API key is not set. Please set the API key before making requests.")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    system_message = (
        "You are a helpful AI assistant. Provide clear, concise, and accurate answers to user queries." if not use_cot else
        "You are a helpful AI assistant that explains your reasoning step by step to help the user understand your thought process. For each step:\n\n- **Step Title**: Summarize what you're doing in this step.\n- **Explanation**: Provide a detailed explanation or calculation.\n\nYour reasoning should include at least three logical steps that build upon each other. After explaining your steps, provide a final conclusion starting with '**Final Conclusion:**' where you summarize your answer clearly.\n\nAdditional Guidelines:\n\n- Ensure each step is necessary and directly contributes to solving the problem.\n- Use clear and professional language that's easy to understand.\n- Avoid unnecessary information or overly complex terminology.\n- Keep the user's perspective in mind and aim to enhance their understanding."
    )

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "stream": True
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, stream=True)
        response.raise_for_status()

        current_step = ""
        for line in response.iter_lines():
            if line:
                try:
                    json_line = json.loads(line.decode('utf-8').split('data: ')[1])
                    content = json_line['choices'][0]['delta'].get('content', '')
                    if content:
                        if use_cot:
                            if content.startswith("**Step"):
                                if current_step:
                                    yield current_step
                                current_step = content
                            elif content.startswith("**Final Conclusion:**"):
                                if current_step:
                                    yield current_step
                                yield content
                                current_step = ""
                            else:
                                current_step += content
                        else:
                            yield content
                except json.JSONDecodeError:
                    continue

        if current_step:
            yield current_step

    except requests.RequestException as e:
        yield f"Error: {str(e)}"
