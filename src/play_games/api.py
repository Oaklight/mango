import os
import openai

openai.api_key = os.environ.get('OPENAI_API_KEY')

def api_complete(system_prompt, prompt, model="gpt-3.5-turbo"):
    completion = openai.ChatCompletion.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    )
    return completion.choices[0].message['content']