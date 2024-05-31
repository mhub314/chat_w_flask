import openai
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("CHATGPT_KEY")

if openai.api_key is None:
    error_message = "Error: CHATGPT_KEY not found in environment variables."
    print(error_message)
    logging.error(error_message)
    raise ValueError(error_message)

def chat_with_gpt(prompt):
    try:
        logging.debug(f"Sending prompt to OpenAI API: {prompt}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        logging.debug("Received response from OpenAI API")
        return response.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        error_message = f"OpenAI API error: {e}"
        print(error_message)
        logging.error(error_message)
        raise
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        print(error_message)
        logging.error(error_message)
        raise

# def get_recommendations(mood):
#     prompt = f"Please simply list 3 movies or TV shows for someone who is feeling {mood}."
#     logging.debug(f"Generated prompt: {prompt}")
#     return chat_with_gpt(prompt)

def get_recommendations(movie=None, genres=None, mood=None, streaming_services=None):
    prompt = "Please recommend 3 movies or tv shows"

    # if movie:
    #     prompt += f" similar to {movie}."
    if genres:
        prompt += f" In the genres: {', '.join(genres)}."
    if mood:
        prompt += f" for someone who is feeling {mood}"
    if movie:
        prompt += f" similar to {movie}. Include a percentage similarity and 1-2 sentences about why they are similar."
    if streaming_services:
        prompt += f" currently available on {', '.join(streaming_services)}. Include which streaming service each recommendation is available on."

    prompt += " for each recommendation, please provide the title, the runtime, the Rotten Tomatoes score, a 1-2 sentence synopsis with any well-known actors of the recommended movie or tv show, and a link to the IMDB page."

    logging.debug(f"Generated prompt: {prompt}")
    return chat_with_gpt(prompt)

# add actors to synopsis, not separated on another line
# remove similarity percentage when no user input - DONE - ONLY WORKS SOME TIME??
