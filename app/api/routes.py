from . import api
from flask import request, render_template
from app.recommendations import get_recommendations
import logging

# Define the /api/recommendations route
# This route receives a POST request with form data, processes the data, and returns recommendations
# The recommendations are displayed on the recommendations.html page

@api.route('/recommendations', methods=['POST'])
def recommendations():
    logging.debug("Accessed /api/recommendations route")
    print("Accessed /api/recommendations route")
    try:
        data = request.form.to_dict()
        logging.debug(f'Received data: {data}')
        print(f"Received data: {data}")

        if not data:
            error_message = "No data received"
            logging.error(error_message)
            print(error_message)
            return render_template('recommendations.html', error=error_message)
        
        movie = data.get('movie')
        genres = data.get('genres')
        moods = data.get('moods')
        streaming_services = data.get('streaming_services')
        more_recommendations_flag = data.get('moreRecommendationsFlag')

        if genres:
            genres = [genre.strip() for genre in genres.split(",")]

        if moods:
            moods = [mood.strip() for mood in moods.split(",")]

        if streaming_services:
            streaming_services = [service.strip() for service in streaming_services.split(",")]

        if more_recommendations_flag:
            recommendations = get_recommendations(movie, genres, moods, streaming_services)
          

        #Call get_recommendations with the user's input  
        # recommendations = get_recommendations(movie, genres, moods, streaming_services)
        logging.debug(f"Recommendations: {recommendations}")
        print(f"Recommendations: {recommendations}")

        #Render recommendations.html with the new set of recommendatins
        return render_template('recommendations.html', recommendations=recommendations, movie=movie, genres=genres, streaming_services=streaming_services, more_recommendations=True)

    except Exception as e:
        error_message = f"Error: {str(e)}"
        logging.error(error_message)
        print(error_message)
        return render_template('recommendations.html', error=error_message)

