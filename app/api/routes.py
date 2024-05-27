from . import api
from flask import request, jsonify, render_template
from app.recommendations import get_recommendations
import logging

@api.route('/recommendations', methods=['POST'])
def recommendations():
    logging.debug("Accessed /api/recommendations route")
    print("Accessed /api/recommendations route")
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        logging.debug(f'Received data: {data}')
        print(f"Received data: {data}")

        if not data:
            error_message = "No data received"
            logging.error(error_message)
            print(error_message)
            return jsonify({"error": error_message}), 400
        
        movie = data.get('movie')
        genres = data.get('genres')
        moods = data.get('moods')
        streaming_services = data.get('streaming_services')

        if genres:
            genres = [genre.strip() for genre in genres.split(",")]

        if moods:
            moods = [mood.strip() for mood in moods.split(",")]

        if streaming_services:
            streaming_services = [service.strip() for service in streaming_services.split(",")]

        # mood = data.get('mood', '')
        # if not mood:
        #     error_message = "Mood is required but not provided"
        #     logging.error(error_message)
        #     print(error_message)
        #     return jsonify({"error": error_message}), 400

        recommendations = get_recommendations(movie, genres, moods, streaming_services)
        logging.debug(f"Recommendations: {recommendations}")
        print(f"Recommendations: {recommendations}")
        return jsonify({"recommendations": recommendations})

    except Exception as e:
        error_message = f"Error: {str(e)}"
        logging.error(error_message)
        print(error_message)
        return jsonify({"error": "Internal Server Error"}), 500

@api.route('/', methods=['GET'])
def home():
    return render_template('form.html')




