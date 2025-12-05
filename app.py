from flask import Flask, request, jsonify
from ai.functions import get_marketing_activities, get_challenges, get_attendance, get_goals, get_stuck_detections, get_call_sentiment
from pydantic import ValidationError
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/marketing-activities', methods=['POST'])
def extract_marketing_activities():
    """
    Extract marketing activities from a transcript

    Expected JSON body:
    {
        "transcript": "string - the transcript text to analyze"
    }

    Returns:
    {
        "activities": [...] - list of marketing activities extracted
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        transcript = data.get('transcript')
        date  = data.get('week')

        if not transcript:
            return jsonify({"error": "transcript field is required"}), 400
        if not date:
            return jsonify({"error": "date field is required"}), 400

        

        if not isinstance(transcript, str):
            return jsonify({"error": "transcript must be a string"}), 400

        result = get_marketing_activities(transcript)

        return jsonify(result.model_dump(mode='json')), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.errors()
        }), 422

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/challenges', methods=['POST'])
def extract_challenges():
    """
    Extract challenges from a transcript

    Expected JSON body:
    {
        "transcript": "string - the transcript text to analyze"
    }

    Returns:
    {
        "challenges": [...] - list of challenges extracted
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        transcript = data.get('transcript')

        if not transcript:
            return jsonify({"error": "transcript field is required"}), 400

        if not isinstance(transcript, str):
            return jsonify({"error": "transcript must be a string"}), 400

        result = get_challenges(transcript)

        return jsonify(result.model_dump(mode='json')), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.errors()
        }), 422

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/attendance', methods=['POST'])
def extract_attendance():
    """
    Extract attendance from a transcript

    Expected JSON body:
    {
        "attendance": "string - attendance record",
        "transcript": "string - the transcript text to analyze"
    }

    Returns:
    {
        "attendance": [...] - list of attendance records
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        attendance = data.get('attendance')
        transcript = data.get('transcript')

        if not transcript:
            return jsonify({"error": "transcript field is required"}), 400

        if not attendance:
            return jsonify({"error": "attendance field is required"}), 400

        if not isinstance(transcript, str):
            return jsonify({"error": "transcript must be a string"}), 400

        if not isinstance(attendance, str):
            return jsonify({"error": "attendance must be a string"}), 400

        result = get_attendance(attendance, transcript)

        return jsonify(result.model_dump(mode='json')), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.errors()
        }), 422

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/goals', methods=['POST'])
def extract_goals():
    """
    Extract goals from a transcript

    Expected JSON body:
    {
        "transcript": "string - the transcript text to analyze"
    }

    Returns:
    {
        "goals": [...] - list of goals extracted
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        transcript = data.get('transcript')

        if not transcript:
            return jsonify({"error": "transcript field is required"}), 400

        if not isinstance(transcript, str):
            return jsonify({"error": "transcript must be a string"}), 400

        result = get_goals(transcript)

        return jsonify(result.model_dump(mode='json')), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.errors()
        }), 422

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/stuck-detections', methods=['POST'])
def extract_stuck_detections():
    """
    Extract stuck detections from a transcript

    Expected JSON body:
    {
        "transcript": "string - the transcript text to analyze"
    }

    Returns:
    {
        "detections": [...] - list of stuck detections extracted
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        transcript = data.get('transcript')

        if not transcript:
            return jsonify({"error": "transcript field is required"}), 400

        if not isinstance(transcript, str):
            return jsonify({"error": "transcript must be a string"}), 400

        result = get_stuck_detections(transcript)

        return jsonify(result.model_dump(mode='json')), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.errors()
        }), 422

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/call-sentiment', methods=['POST'])
def extract_call_sentiment():
    """
    Extract call sentiment from a transcript

    Expected JSON body:
    {
        "transcript": "string - the transcript text to analyze"
    }

    Returns:
    {
        "sentiment_score": int - sentiment score 1-5,
        "rationale": string - rationale for the score,
        "dominant_emotion": string - dominant emotion,
        "representative_quotes": [
            {
                "name": string - participant name,
                "emotion": [string] - list of emotions,
                "exact_quotes": [string] - list of quotes,
                "is_negative": bool - whether expressing negative emotion
            }
        ],
        "confidence_score": int - confidence level
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        transcript = data.get('transcript')

        if not transcript:
            return jsonify({"error": "transcript field is required"}), 400

        if not isinstance(transcript, str):
            return jsonify({"error": "transcript must be a string"}), 400

        result = get_call_sentiment(transcript)

        return jsonify(result.model_dump(mode='json')), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.errors()
        }), 422

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
