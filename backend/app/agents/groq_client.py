import base64
from groq import Groq
from app.core.config import settings

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def encode_image(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def vision_chat(prompt: str, image_paths: list[str]) -> str:
    """Send a prompt + one or more images to the Groq vision model."""
    content = [{"type": "text", "text": prompt}]
    for path in image_paths:
        b64 = encode_image(path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
        })

    resp = _get_client().chat.completions.create(
        model=settings.VISION_MODEL,
        messages=[{"role": "user", "content": content}],
        temperature=0.4,
    )
    return resp.choices[0].message.content


def text_chat(prompt: str, system: str = "") -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = _get_client().chat.completions.create(
        model=settings.TEXT_MODEL,
        messages=messages,
        temperature=0.5,
    )
    return resp.choices[0].message.content
