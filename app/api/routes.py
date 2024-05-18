# import os
# from . import api
# # from app import app
# from flask import jsonify

from . import api
from flask import request, jsonify
from app.recommendations import get_recommendations
import logging
# from flask import jsonify

logging.basicConfig(level=logging.DEBUG)

# @api.route('/test', methods=['GET'])
# def test_route():
#     return jsonify({"message": "this is a test endpoint"})

@api.route('/recommendations', methods=['POST'])
def recommendations():
    try:
        data = request.get_json()
        logging.debug(f'Received data: {data}')
        mood = data.get('mood', '')  

        if not mood:
            return jsonify({"error": "Mood is required"}), 400
    
        recommendations = get_recommendations(mood)
        logging.debug(f"Recommendations: {recommendations}")
        return jsonify({"recommendations": recommendations})
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500



