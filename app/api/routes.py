from . import api
from flask import request, jsonify, render_template
from app.recommendations import get_recommendations
import logging

# Route for handling JSON API requests
@api.route('/recommendations', methods=['POST'])
def api_recommendations():
    logging.debug("Accessed /api/recommendations route")
    try:
        if request.content_type != 'application/json':
            logging.error(f"Unsupported Content-Type: {request.content_type}")
            return jsonify({"error": "Content-Type must be application/json"}), 415
        
        data = request.get_json()
        logging.debug(f'Parsed JSON data: {data}')

        if not data:
            logging.error("No data received")
            return jsonify({"error": "No data received"}), 400
        
        movie = data.get('movie')
        genres = data.get('genres', '')
        moods = data.get('moods', '')
        streaming_services = data.get('streaming_services', '')
        more_recommendations_flag = data.get('moreRecommendationsFlag', 'false').lower() == 'true'

        genres = [genre.strip() for genre in genres.split(",")] if genres else []
        moods = [mood.strip() for mood in moods.split(",")] if moods else []
        streaming_services = [service.strip() for service in streaming_services.split(",")] if streaming_services else []

        recommendations = get_recommendations(movie, genres, moods, streaming_services) if not more_recommendations_flag else []

        logging.debug(f"Recommendations: {recommendations}")
        return jsonify(recommendations), 200

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Route for handling form submissions and rendering HTML template
@api.route('/form/recommendations', methods=['POST'])
def form_recommendations():
    logging.debug("Accessed /form/recommendations route")
    try:
        data = request.form.to_dict()
        logging.debug(f'Received form data: {data}')

        if not data:
            return render_template('recommendations.html', error="No data received")
        
        movie = data.get('movie')
        genres = data.get('genres', '')
        moods = data.get('moods', '')
        streaming_services = data.get('streaming_services', '')
        more_recommendations_flag = data.get('moreRecommendationsFlag', 'false').lower() == 'true'


        genres = [genre.strip() for genre in genres.split(",")] if genres else []
        moods = [mood.strip() for mood in moods.split(",")] if moods else []
        streaming_services = [service.strip() for service in streaming_services.split(",")] if streaming_services else []

        recommendations = get_recommendations(movie, genres, moods, streaming_services) if not more_recommendations_flag else [] 

        logging.debug(f"Recommendations: {recommendations}")
        return render_template('recommendations.html', recommendations=recommendations, movie=movie, genres=genres, streaming_services=streaming_services, more_recommendations=more_recommendations_flag)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return render_template('recommendations.html', error=str(e))
