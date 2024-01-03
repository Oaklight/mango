import os
from openai import OpenAI
# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

# openai.api_key = os.environ.get('OPENAI_API_KEY')
# openai.organization = os.environ.get('OPENAI_API_ORG')

@retry(wait=wait_random_exponential(min=20, max=60), stop=stop_after_attempt(6))
def api_complete(system_prompt, prompt, model="gpt-3.5-turbo", temperature=0.0):
    try:
        client = OpenAI(
            # defaults to os.environ.get("OPENAI_API_KEY")
            api_key=os.environ.get('OPENAI_API_KEY'),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
            temperature=temperature,
        )
        return chat_completion.choices[0].message.content # .choices[0].message['content']
    except Exception as e:
        raise