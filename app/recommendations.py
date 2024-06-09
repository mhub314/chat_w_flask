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

if openai.api_key is None or tmdb_api_key is None or tmdb_access_token is None:
    error_message = "Error: Missing required environment variables."
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
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return None
    except requests.exceptions.RequestException as e:
        error_message = f"TMDB API error: {e}"
        print(error_message)
        logging.error(error_message)
        return None

def get_recommendations(movie=None, genres=None, moods=None, streaming_services=None):
    prompt = "Please recommend 3 movies"
    if movie:
        prompt += f" similar to {movie}"
    if genres:
        prompt += f" in the genres: {', '.join(genres)}"
    if moods:
        prompt += f" for someone who is feeling {', '.join(moods)}"
    if streaming_services:
        prompt += f" currently available on {', '.join(streaming_services)}"
    
    if movie:
        prompt += ". Include a percentage similarity and 1-2 sentences about why they are similar."
    prompt += " For each recommendation, please provide the title, the year it came out, the runtime, the streaming service, the Rotten Tomatoes critic score, the Rotten Tomatoes audience score, a 2-3 sentence synopsis with any well-known actors of the recommended movie or tv show, 2-3 sentences about the reviews, and a link to the IMDB page. Ensure each piece of information is on a new line and clearly labeled as follows:"

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
    recommendations = chat_with_gpt(prompt)
    logging.debug(f"Recommendations from OpenAI: {recommendations}")

    recommendations_list = recommendations.split('\n\n')
    recommendations_with_posters = []

    for rec in recommendations_list:
        try:
            details = extract_details(rec)
            logging.debug(f"Parsed details: {details}")
            if not details.get('title'):
                raise ValueError("Missing title")
            title = details['title']
            poster_url = get_poster_from_tmdb(title)
            if poster_url:
                details['poster_url'] = poster_url
                recommendations_with_posters.append(details)
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

    try:
        details['title'] = extract_field(lines, 'Title:')
        details['year'] = extract_field(lines, 'Year:')
        details['runtime'] = extract_field(lines, 'Runtime:')
        details['streaming_service'] = extract_field(lines, 'Streaming Service:')
        details['rotten_tomatoes_critic_score'] = extract_field(lines, 'Rotten Tomatoes Critic Score:')
        details['rotten_tomatoes_audience_score'] = extract_field(lines, 'Rotten Tomatoes Audience Score:')
        details['synopsis'] = extract_field(lines, 'Synopsis:')
        details['reviews'] = extract_field(lines, 'Reviews:')
        details['imdb_link'] = extract_field(lines, 'IMDB:')
    except (IndexError, ValueError) as e:
        logging.error(f"Error parsing recommendation: {e} - Line: {lines}")
        logging.error(f"Details so far: {details}")
        raise ValueError("Error encountered while extracting details.")
    except Exception as e:
        logging.error(f"Unexpected error extracting details: {e}")
        logging.error(f"Details so far: {details}")
        raise ValueError("Unexpected error encountered while extracting details.")
    return details

def extract_title_and_year(line):
    try:
        # Log the line being processed
        logging.debug(f"Extracting title and year from line: {line}")
        # Use regex to match the format "Title: <title> Year: <year>"
        import re
        match = re.search(r'Title: (.+) Year: (\d{4})', line)
        if match:
            title = match.group(1).strip()
            year = match.group(2).strip()
            logging.debug(f"Extracted title: {title}, year: {year}")
            return title, year
        return '', ''
    except (IndexError, ValueError):
        logging.error(f"Error extracting title and year from line: {line}")
        return '', ''

def extract_field(lines, field):
    for line in lines:
        if field in line:
            logging.debug(f"Extracting field '{field}' from line: {line}")
            return line.split(field)[1].strip()
    return ''


