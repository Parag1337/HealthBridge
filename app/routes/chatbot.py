# app/routes/chatbot.py
from flask import Blueprint, request, jsonify, current_app
import google.generativeai as genai
import google.auth.exceptions
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            logger.error("Gemini API key not found in configuration")
            return jsonify({'error': 'AI service is not properly configured'}), 500

        genai.configure(api_key=api_key)
        logger.info("Gemini API configured successfully")

        # 4. Choose a model - use the correct model name for the current API version
        try:
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            logger.info("Using gemini-1.5-flash model")
        except Exception as model_error:
            logger.warning(f"Failed to load gemini-1.5-flash model: {model_error}")
            # Fallback to other available models
            fallback_models = [
                'models/gemini-1.5-pro',
                'models/gemini-1.5-flash-latest',
                'models/gemini-1.5-pro-latest'
            ]
            model = None
            for fallback_model in fallback_models:
                try:
                    model = genai.GenerativeModel(fallback_model)
                    logger.info(f"Using {fallback_model} model as fallback")
                    break
                except Exception as fallback_error:
                    logger.warning(f"Failed to load {fallback_model}: {fallback_error}")
                    continue

            if model is None:
                logger.error("Failed to load any available model")
                return jsonify({'error': 'AI model is not available'}), 500

        # 5. Generate the response with error handling
        try:
            response = model.generate_content(user_message)
            logger.info("AI response generated successfully")
        except Exception as gen_error:
            logger.error(f"Error generating AI response: {str(gen_error)}")
            return jsonify({'error': 'Failed to generate AI response. Please try again later.'}), 500

        # 6. Check if response is valid
        if not response or not hasattr(response, 'text') or not response.text:
            logger.error("AI response is empty or invalid")
            return jsonify({'error': 'Failed to generate response from AI'}), 500

        # 7. Send back to frontend
        return jsonify({'reply': response.text.strip()})

    except genai.types.generation_types.StopCandidateException as safety_error:
        logger.warning(f"AI response blocked due to safety concerns: {str(safety_error)}")
        return jsonify({'error': 'Your message was flagged by our safety filters. Please rephrase your question.'}), 400

    except google.auth.exceptions.GoogleAuthError as auth_error:
        logger.error(f"Authentication error with Gemini API: {str(auth_error)}")
        return jsonify({'error': 'AI service authentication failed. Please contact support.'}), 500

    except Exception as e:
        logger.error(f"Unexpected chatbot error: {str(e)}", exc_info=True)
        return jsonify({'error': 'An error occurred while processing your request'}), 500
