
"""
this is the main file to run the code

"""

from flask import Flask, request, jsonify, send_from_directory
import openai
from openai import OpenAI
client = OpenAI()
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech

app = Flask(__name__)

# Set your OpenAI API key here
# openai.api_key = ''

client = openai.OpenAI(
    api_key="0b6d7af01e734ce7a36e24adcf94f491",
    base_url="https://api.aimlapi.com",
)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

""" 
generate text from gpt api model ai and connect it by api

"""
@app.route('/api', methods=['POST'])
def generate_text():
    data = request.json
    user_input = data.get('input', '')
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    try:
        response = client.chat.completions.create(  
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": user_input}], max_tokens=150, temperature=0.5)
        message_content = response.choices[0].message.content
        return jsonify({'response': message_content})
    except Exception as e:
        # Catch all other errors
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
