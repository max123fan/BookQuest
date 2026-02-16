#refined prompt and formatting with multi-language support

import openai
import requests
import json
import re
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def create_response(user_msg, max_tokens=500):
    system_prompt = """
        You are an assistant that generates book recommendations based on user input.
        Default to 5 books unless user says otherwise.
        Output a JSON array of books, no extra text.

        Each book is an object with
        "title" (string, concise title),
        "author" (string),
        "media_type" ("book" by default, or "audiobook", "ebook" if specified).
        """

    response = openai.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_msg}
        ],
        max_completion_tokens=max_tokens
    )

    print("text:", response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)

def create_response2(user_msg, max_tokens=500):
    system_prompt = """
        You are an assistant that generates book recommendations based on user input.
        Default to 5 books unless user says otherwise.
        Output a JSON array of books, no extra text.

        Each book is an object with
        "title" (string, concise title),
        "author" (string),
        "media_type" ("book" by default, or "audiobook", "ebook" if specified).
        """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=max_tokens
    )

    print("text:", response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)


print(create_response("Recommend some science fiction books."))
