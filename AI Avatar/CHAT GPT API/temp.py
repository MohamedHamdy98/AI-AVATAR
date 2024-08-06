
"""
this file is a temp to save code and organize it

"""

from flask import Flask, request, jsonify, send_file
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech
import os

""" 
convert audio to text

"""
def recognize_speech(audio_path):
    client = speech.SpeechClient()

    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()
    
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="ar",  # Adjust this if you want a different language
    )
    
    response = client.recognize(config=config, audio=audio)

    # Combine all transcribed text into a single string
    transcribed_text = ' '.join([result.alternatives[0].transcript for result in response.results])

    return transcribed_text

"""
connect to api

"""
#@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the file temporarily
    audio_path = "temp_audio.wav"
    file.save(audio_path)

    try:
        transcribed_text = recognize_speech(audio_path)
        return jsonify({'transcription': transcribed_text})
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    finally:
        # Clean up the temporary file
        if os.path.exists(audio_path):
            os.remove(audio_path)
###########################################################################################################
""" 
convert text to audio

"""
def synthesize_speech(text, output_path):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="ar-XA",  # Adjust this if you want a different language
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3)
    
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config)
    
    with open(output_path, "wb") as output_file:
        output_file.write(response.audio_content)

"""
connect to api

"""
# @app.route('/api/synthesize', methods=['POST'])
def api_synthesize():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Define output path
    output_path = "output.mp3"

    try:
        synthesize_speech(text, output_path)
        return send_file(output_path, mimetype='audio/mpeg', as_attachment=True, attachment_filename='output.mp3')
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    finally:
        # Clean up the temporary file
        if os.path.exists(output_path):
            os.remove(output_path)