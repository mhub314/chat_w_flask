import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("CHATGPT_KEY")

def chat_with_gpt(prompt):
    response = openai.ChatCompletion.create(
        model ="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def get_recommendations(mood):
    prompt = f"Please recommend 3 movies or TV shows for someone who is feeling {mood}."
    return chat_with_gpt(prompt)

# if __name__=="__main__":
#     prompt = "Please recommend 3 movies or TV shows for someone who is feeling {mood}."
#     print(chat_with_gpt(prompt))