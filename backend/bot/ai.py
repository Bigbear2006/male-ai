from openai import NOT_GIVEN

from bot.loader import openai_client


async def answer(prompt: str, *, max_output_tokens: int = NOT_GIVEN) -> str:
    return (
        await openai_client.responses.create(
            input=prompt,
            model='gpt-4.1',
            max_output_tokens=max_output_tokens,
        )
    ).output_text
