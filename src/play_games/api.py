import os
import openai
# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

openai.api_key = os.environ.get('OPENAI_API_KEY')
openai.organization = os.environ.get('OPENAI_API_ORG')


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def api_complete(system_prompt, prompt, model="gpt-3.5-turbo", temperature=0.0):
    completion = openai.ChatCompletion.create(
    model=model,
    temperature=temperature,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    )
    return completion.choices[0].message['content']