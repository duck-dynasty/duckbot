import groq
from groq.types import Model


def is_chat_model(model: Model) -> bool:
    return model.active and "text" in model.output_modalities and "tools" in getattr(model, "supported_features", [])


def chat_models(client: groq.Groq) -> list[Model]:
    models = [m for m in client.models.list().data if is_chat_model(m)]
    return sorted(models, key=lambda m: m.created, reverse=True)


def complete(client: groq.Groq, prompt: str) -> str:
    """Returns the newest chat model's response to the prompt, falling back to older models when rate limited."""
    for model in chat_models(client):
        try:
            completion = client.chat.completions.create(model=model.id, max_tokens=2000, temperature=0, messages=[{"role": "user", "content": prompt}])
            return completion.choices[0].message.content
        except groq.RateLimitError:
            continue
    raise RuntimeError("every Groq chat model is rate limited or unavailable")
