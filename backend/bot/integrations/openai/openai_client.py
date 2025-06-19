from openai import NOT_GIVEN

from bot.loader import openai_client


async def answer(prompt: str, *, max_output_tokens: int = NOT_GIVEN) -> str:
    response = await openai_client.responses.create(
        input=prompt,
        model='gpt-4.1',
        max_output_tokens=max_output_tokens,
    )
    return response.output_text


async def chat(messages: list[dict]):
    completion = await openai_client.chat.completions.create(
        model='gpt-4.1',
        messages=messages,
    )
    return completion.choices[0].message.content
