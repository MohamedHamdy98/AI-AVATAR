from flask import Flask, request, jsonify, send_file, send_from_directory
from gtts import gTTS
import os
import speech_recognition as sr
from pydub import AudioSegment


app = Flask(__name__)

def synthesize_speech(text, output_path):
    tts = gTTS(text=text, lang='ar')  # Adjust language code if needed
    tts.save(output_path)

@app.route('/')
def index():
    return send_from_directory('.', 'index2.html')

@app.route('/testing/synthesize', methods=['POST'])
def api_synthesize():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Define output path
    output_path = r"H:\Projects VEEM\AI Avatar\CHAT GPT API\testing\output.mp3"

    try:
        # Ensure the file doesn't exist before creating it
        if os.path.exists(output_path):
            os.remove(output_path)

        synthesize_speech(text, output_path)

        # Return the file and ensure it is properly closed
        response = send_file(output_path, as_attachment=True, mimetype='audio/mp3')

        return response
    except Exception as e:
        # Log the error for debugging
        app.logger.error(f'Error occurred: {str(e)}')
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    finally:
        # Clean up temporary file
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except PermissionError as e:
                app.logger.error(f'PermissionError occurred: {str(e)}')

def convert_to_wav(audio_path):
    audio = AudioSegment.from_file(audio_path)
    wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
    audio.export(wav_path, format="wav")
    return wav_path

def recognize_speech(audio_path):
    recognizer = sr.Recognizer()

    if not audio_path.lower().endswith('.wav'):
        audio_path = convert_to_wav(audio_path)

    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    
    try:
        # Recognize speech using Google Web Speech API (offline option also available)
        transcribed_text = recognizer.recognize_google(audio, language="ar")  # Adjust language as needed
        return transcribed_text
    except sr.UnknownValueError:
        return "Speech recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results; {e}"
    
####################################################################

@app.route('/testing/recognize', methods=['POST'])
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


if __name__ == '__main__':
    app.run(debug=True)














