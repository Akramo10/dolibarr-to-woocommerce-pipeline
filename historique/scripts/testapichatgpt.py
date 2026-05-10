import os

from openai import OpenAI


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY manquante. Ajoutez-la dans vos variables d'environnement.")

client = OpenAI(api_key=api_key)

completion = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    messages=[
        {"role": "user", "content": "write a haiku about ai"},
    ],
)

print(completion.choices[0].message.content)
