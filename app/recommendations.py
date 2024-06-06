import openai
import os
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("CHATGPT_KEY")

tmdb_api_key = os.getenv("TMDB_API_KEY")
tmdb_access_token = os.getenv("TMDB_ACCESS_TOKEN")

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
            poster_path = data['results'][0]['poster_path']
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return None
    except requests.exceptions.RequestException as e:
        error_message = f"TMDB API error: {e}"
        print(error_message)
        logging.error(error_message)
        return None

def get_recommendations(movie=None, genres=None, mood=None, streaming_services=None):
    prompt = "Please recommend 3 movies or tv shows"

    if genres:
        prompt += f" in the genres: {', '.join(genres)}."
    if mood:
        prompt += f" for someone who is feeling {mood}."
    if movie:
        prompt += f" similar to {movie}. Include a percentage similarity and 1-2 sentences about why they are similar."
    if streaming_services:
        prompt += f" currently available on {', '.join(streaming_services)}. Include which streaming service each recommendation is available on."

    prompt += " For each recommendation, please provide the title, the year it came out, the runtime, the streaming service, the Rotten Tomatoes critic score, the Rotten Tomatoes audience score, a 1-2 sentence synopsis with any well-known actors of the recommended movie or tv show, 1-2 sentences about the reviews, and a link to the IMDB page."

    logging.debug(f"Generated prompt: {prompt}")
    recommendations = chat_with_gpt(prompt)
    logging.debug(f"Recommendations from OpenAI: {recommendations}")

    # Parse recommendations and fetch posters
    recommendations_list = recommendations.split('\n\n')  # Adjust this based on the format of OpenAI response
    recommendations_with_posters = []

    for rec in recommendations_list:
        try:
            details = extract_details(rec)
            logging.debug(f"Parsed details: {details}")
            title = details['title']
            poster_url = get_poster_from_tmdb(title)
            details['poster_url'] = poster_url
            recommendations_with_posters.append(details)
        except Exception as e:
            logging.error(f"Error parsing recommendation: {e}")
    
    logging.debug(f"Final recommendations with posters: {recommendations_with_posters}")
    return recommendations_with_posters

def extract_details(recommendation):
    details = {}
    lines = recommendation.split('\n')
    logging.debug(f"Extracting details from: {lines}")
    
    try:
        if len(lines) > 0:
            details['title'] = extract_title(lines[0])
        if len(lines) > 1:
            details['year'] = extract_year(lines[0])
        if len(lines) > 2:
            details['runtime'] = extract_runtime(lines[1])
        if len(lines) > 3:
            details['streaming_service'] = extract_streaming_service(lines[2])
        if len(lines) > 4:
            details['rotten_tomatoes_critic_score'] = extract_critic_score(lines[3])
        if len(lines) > 5:
            details['rotten_tomatoes_audience_score'] = extract_audience_score(lines[4])
        if len(lines) > 6:
            details['synopsis'] = extract_synopsis(lines[5])
        if len(lines) > 7:
            details['reviews'] = extract_reviews(lines[6])
        if len(lines) > 8:
            details['imdb_link'] = extract_imdb_link(lines[7])
    except IndexError as e:
        logging.error(f"IndexError: {e} - Line: {lines}")
        logging.error(f"Details so far: {details}")
    except Exception as e:
        logging.error(f"Error extracting details: {e}")
        logging.error(f"Details so far: {details}")
    return details

def extract_title(line):
    return line.split('"')[1].strip() if '"' in line else ''

def extract_year(line):
    return line.split('(')[1].split(')')[0].strip() if '(' in line and ')' in line else ''

def extract_runtime(line):
    return line.split(': ')[1].strip() if ': ' in line else ''

def extract_streaming_service(line):
    return line.split(': ')[1].strip() if ': ' in line else ''

def extract_critic_score(line):
    return line.split(': ')[1].strip() if ': ' in line else ''

def extract_audience_score(line):
    return line.split(': ')[1].strip() if ': ' in line else ''

def extract_synopsis(line):
    return line.split(': ')[1].strip() if ': ' in line else ''

def extract_reviews(line):
    return line.strip()

def extract_imdb_link(line):
    return line.split(' ')[-1].strip() if ' ' in line else ''