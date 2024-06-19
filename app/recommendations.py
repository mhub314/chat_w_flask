import openai
import os
import logging
import requests
from dotenv import load_dotenv
import random

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("CHATGPT_KEY") 

tmdb_api_key = os.getenv("TMDB_API_KEY")
tmdb_access_token = os.getenv("TMDB_ACCESS_TOKEN")

# Checking if the environment variables are set
if openai.api_key is None or tmdb_api_key is None or tmdb_access_token is None:
    error_message = "Error: Missing required environment variables."
    print(error_message)
    logging.error(error_message)
    raise ValueError(error_message)

# Function to prompt and chat with GPT-3
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

# Function to get movie poster from TMDB API
def get_poster_from_tmdb(title):
    try:
        headers = {
            'Authorization': f'Bearer {tmdb_access_token}'
        }
        params = {
            'api_key': tmdb_api_key,
            'query': title
        }
        response = requests.get('https://api.themoviedb.org/3/search/movie', headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data['results']:
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}" #returning the poster url
        return None
    except requests.exceptions.RequestException as e:
        error_message = f"TMDB API error: {e}"
        print(error_message)
        logging.error(error_message)
        return None

# Converts runtime from minutes to hours and minutes
def convert_runtime(runtime): 
    try:
        runtime = int(runtime.split()[0])
        hours = runtime // 60
        remaining_minutes = runtime % 60
        return f"{hours}hr {remaining_minutes}min"
    except Exception as e:
        logging.error(f"Error converting runtime: {e}")
        return runtime

# Function to get recommendations from OpenAI
def get_recommendations(movie=None, genres=None, moods=None, streaming_services=None):
    prompt_options = ["Please recommend 3 movies", "Can you suggest 3 movies", "I would like 3 recommendations for movies"]
    prompt = random.choice(prompt_options)

    if movie:
        prompt += f" similar to {movie}"
    if genres:
        prompt += f" in the genres: {', '.join(genres)}"
    if moods:
        prompt += f" for someone who is looking for something {', '.join(moods)}"
    if streaming_services:
        prompt += f" currently available on {', '.join(streaming_services)}"
    
    if movie:
        prompt += ". Ensure each recommendation includes a percentage similarity and an explanation of 1-2 sentences on why they are similar."

    prompt += " For each recommendation, please provide the title, the year it came out, the runtime, the streaming service, the Rotten Tomatoes critic score, the Rotten Tomatoes audience score, a 2-3 sentence synopsis with any well-known actors of the recommended movie or TV show, 2-3 sentences about the reviews, and a link to the IMDB page. Ensure each piece of information is on a new line and clearly labeled as follows:"

    if movie:
        prompt += """
Similarity: <similarity percentage>; <similarity explanation>
"""

    # Adding a random number to the prompt to make each output unique
    random_number = random.randint(1, 1000)
    unique_context = random.choice(['context', 'variant', 'version'])
    prompt += f" [{unique_context}: {random_number}]"

    prompt += """
Title: <movie title>
Year: <year>
Runtime: <runtime>
Streaming Service: <streaming service>
Rotten Tomatoes Critic Score: <critic score>
Rotten Tomatoes Audience Score: <audience score>
Synopsis: <synopsis>
Reviews: <reviews>
IMDB: <imdb link>
"""
    logging.debug(f"Generated prompt: {prompt}")

    recommendations_with_posters = []

    while len(recommendations_with_posters) < 3:
        recommendations = chat_with_gpt(prompt)
        logging.debug(f"Recommendations from OpenAI: {recommendations}")

        recommendations_list = recommendations.split('\n\n')
        
        for rec in recommendations_list:
            try:
                details = extract_details(rec)
                logging.debug(f"Parsed details: {details}")
                # Skip recommendations without title, similarity, or explanation
                if not details.get('title') or details['similarity'] == "N/A" or details['explanation'] == "No explanation provided.":
                    raise ValueError("Missing title, similarity, or explanation")
                title = details['title']
                poster_url = get_poster_from_tmdb(title)
                if poster_url:
                    details['poster_url'] = poster_url

                if "runtime" in details:
                    details["runtime"] = convert_runtime(details["runtime"])

                recommendations_with_posters.append(details)
                if len(recommendations_with_posters) >= 3:
                    break
            except ValueError as e:
                logging.error(f"Skipping recommendation due to error: {e}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")

    logging.debug(f"Final recommendations with posters: {recommendations_with_posters}")
    return recommendations_with_posters

def extract_details(recommendation):
    details = {}
    lines = recommendation.split('\n')
    logging.debug(f"Extracting details from: {lines}")

    fields = ['Similarity', 'Title', 'Year', 'Runtime', 'Streaming Service', 
              'Rotten Tomatoes Critic Score', 'Rotten Tomatoes Audience Score', 'Synopsis', 
              'Reviews', 'IMDB']

    for field in fields:
        details[field.lower().replace(' ', '_')] = extract_field(lines, f"{field}:")

    # Ensure similarity and explanation are included if a movie is provided
    if 'similarity' in details:
        if ';' in details['similarity']:
            similarity, explanation = details['similarity'].split(';', 1)
            details['similarity'] = similarity.strip()
            details['explanation'] = explanation.strip()
        else:
            details['similarity'] = "N/A"
            details['explanation'] = "No explanation provided."
    else:
        details['similarity'] = "N/A"
        details['explanation'] = "No explanation provided."

    return details

def extract_field(lines, field):
    for line in lines:
        if line.startswith(field):
            logging.debug(f"Extracting field '{field}' from line: {line}")
            return line.split(field, 1)[1].strip()
    return ''