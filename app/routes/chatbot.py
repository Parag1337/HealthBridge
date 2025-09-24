# app/routes/chatbot.py
from flask import Blueprint, request, jsonify, current_app
import google.generativeai as genai

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot_reply():
    try:
        # 1. Get the user message from frontend
        user_message = request.json.get('message', '')

        # 2. Validate input
        if not user_message or not user_message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400

        # 3. Configure Gemini API with the key from Config
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])

        # 4. Choose a model - use the correct model name
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 5. Generate the response
        response = model.generate_content(user_message)

        # 6. Check if response is valid
        if not response or not response.text:
            return jsonify({'error': 'Failed to generate response from AI'}), 500

        # 7. Send back to frontend
        return jsonify({'reply': response.text})

    except genai.types.generation_types.StopCandidateException:
        return jsonify({'error': 'AI response was blocked due to safety concerns'}), 400

    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500
