from flask import Flask, render_template, request, jsonify
import tensorflow as tf
from PIL import Image
import numpy as np
from googletrans import Translator
from gtts import gTTS
import os

app = Flask(__name__)

model = tf.keras.models.load_model('model/plant_disease_model.h5')

num_classes = model.output_shape[-1]

disease_classes = [f'Class {i}' for i in range(num_classes)]

translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']
    if file:
        img = Image.open(file).resize((256, 256))
        img_array = np.array(img) / 255.0

        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class]

        disease_name = disease_classes[predicted_class]

        return jsonify({
            'disease': disease_name,
            'confidence': f"{confidence:.2f}"
        })
    return jsonify({'error': 'No file uploaded'})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    target_language = data.get('lang')
    if text and target_language:
        translation = translator.translate(text, dest=target_language)
        return jsonify({'translated_text': translation.text})
    return jsonify({'error': 'Invalid data'})

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text')
    if text:
        tts = gTTS(text=text, lang='en')
        tts.save('static/audio/output.mp3')
        return jsonify({'audio_url': '/static/audio/output.mp3'})
    return jsonify({'error': 'Invalid text'})

if __name__ == '__main__':
    app.run(debug=True)
