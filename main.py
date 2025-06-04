import os
from dotenv import load_dotenv
import chainlit as cl
from openai import AsyncOpenAI

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def on_message(prompt: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": prompt.content})

    msg = cl.Message(content="")

    stream = await client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=message_history,
        stream=True,
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()
