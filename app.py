from flask import Flask, render_template, request, jsonify, send_file, url_for
import tensorflow as tf
from PIL import Image
import numpy as np
from googletrans import Translator
from gtts import gTTS
from flask import Flask, send_file
from fpdf import FPDF
from langcodes import Language
import os
import logging
import sys
import traceback
from werkzeug.utils import secure_filename

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Increase maximum content length
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure upload folder
UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the model is loaded correctly
try:
    model = tf.keras.models.load_model('model/plant_disease_model.h5')
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

model = tf.keras.models.load_model('model/plant_disease_model.h5')
disease_classes = [
    "Apple Apple scab",
    "Apple Black rot",
    "Apple Cedar apple rust",
    "Apple healthy",
    "Blueberry healthy",
    "Cherry (including sour) Powdery mildew",
    "Cherry (including sour) healthy",
    "Corn (maize) Cercospora leaf spot Gray leaf spot",
    "Corn (maize) Common rust",
    "Corn (maize) Northern Leaf Blight",
    "Corn (maize) healthy",
    "Grape Black rot",
    "Grape Esca (Black Measles)",
    "Grape Leaf blight (Isariopsis Leaf Spot)",
    "Grape healthy",
    "Orange Haunglongbing (Citrus greening)",
    "Peach Bacterial spot",
    "Peach healthy",
    "Pepper, bell Bacterial spot",
    "Pepper, bell healthy",
    "Potato Early blight",
    "Potato Late blight",
    "Potato healthy",
    "Raspberry healthy",
    "Soybean healthy",
    "Squash Powdery_mildew",
    "Strawberry Leaf scorch",
    "Strawberry healthy",
    "Tomato Bacterial spot",
    "Tomato Early blight",
    "Tomato Late blight",
    "Tomato Leaf Mold",
    "Tomato Septoria leaf spot",
    "Tomato Spider mites Two-spotted spider mite",
    "Tomato Target Spot",
    "Tomato Tomato mosaic virus",
    "Tomato Tomato Yellow Leaf Curl Virus",
    "Tomato healthy"
]

translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        logger.debug("Received prediction request")

        # Check if the post request has the file part
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        # If user does not select file
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400

        # Log file details
        logger.debug(f"Received file: {file.filename}, Content type: {file.content_type}")

        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400

        try:
            # Secure the filename
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Save the file
            logger.debug(f"Saving file to {filepath}")
            file.save(filepath)

            # Open and process the image
            logger.debug("Processing image")
            with Image.open(filepath) as img:
                img = img.convert('RGB')
                img = img.resize((64, 64))
                img_array = np.array(img) / 255.0
                img_array = np.expand_dims(img_array, axis=0)

            # Make prediction
            logger.debug("Making prediction")
            predictions = model.predict(img_array)
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            disease_name = disease_classes[predicted_class]

            # Clean up
            logger.debug("Cleaning up temporary file")
            if os.path.exists(filepath):
                os.remove(filepath)

            solution_url = url_for('solution', disease_name=disease_name)

            logger.info(f"Successfully predicted disease: {disease_name}")
            return jsonify({
                'disease': disease_name,
                'confidence': f"{confidence:.2f}",
                'solution_url': solution_url
            }), 200

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}\n{traceback.format_exc()}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}\n{traceback.format_exc()}")
    return jsonify({'error': 'Internal server error. Please check the logs for details.'}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
    return jsonify({'error': 'An unexpected error occurred. Please check the logs for details.'}), 500

disease_solutions = {
    "Apple Apple scab": {
        "solution": "Prune affected areas, apply fungicides, and choose resistant apple varieties.",
        "pesticides": ["Captan", "Myclobutanil"],
        "fertilizers": ["10-10-10 balanced fertilizer"]
    },
    "Apple Black rot": {
        "solution": "Remove infected fruit and leaves, improve air circulation, and apply fungicides.",
        "pesticides": ["Chlorothalonil", "Azoxystrobin"],
        "fertilizers": ["Slow-release nitrogen fertilizers"]
    },
    "Apple Cedar apple rust": {
        "solution": "Remove and destroy fallen leaves, apply fungicides during bud break.",
        "pesticides": ["Propiconazole", "Myclobutanil"],
        "fertilizers": ["Balanced fertilizer with potassium"]
    },
    "Apple healthy": {
        "solution": "Maintain good cultural practices and monitor for pests and diseases.",
        "pesticides": [],
        "fertilizers": ["General-purpose fertilizer"]
    },
    "Blueberry healthy": {
        "solution": "Ensure proper pH and moisture, mulch to retain soil moisture.",
        "pesticides": [],
        "fertilizers": ["Acidic fertilizer for blueberries"]
    },
    "Cherry (including sour) Powdery mildew": {
        "solution": "Apply fungicides early in the season and ensure good air circulation.",
        "pesticides": ["Sulfur", "Myclobutanil"],
        "fertilizers": ["Balanced nitrogen-phosphorus-potassium fertilizer"]
    },
    "Cherry (including sour) healthy": {
        "solution": "Keep trees healthy through proper pruning and watering.",
        "pesticides": [],
        "fertilizers": ["General-purpose fertilizer"]
    },
    "Corn (maize) Cercospora leaf spot Gray leaf spot": {
        "solution": "Rotate crops, apply fungicides, and ensure good drainage.",
        "pesticides": ["Azoxystrobin", "Propiconazole"],
        "fertilizers": ["High nitrogen fertilizer"]
    },
    "Corn (maize) Common rust": {
        "solution": "Choose resistant hybrids and apply fungicides if necessary.",
        "pesticides": ["Chlorothalonil"],
        "fertilizers": ["Nitrogen-rich fertilizer"]
    },
    "Corn (maize) Northern Leaf Blight": {
        "solution": "Remove infected debris and use resistant hybrids.",
        "pesticides": ["Triazole fungicides"],
        "fertilizers": ["Balanced fertilizer"]
    },
    "Corn (maize) healthy": {
        "solution": "Maintain healthy soil and irrigation practices.",
        "pesticides": [],
        "fertilizers": ["Balanced fertilizer"]
    },
    "Grape Black rot": {
        "solution": "Prune affected areas, apply fungicides, and remove fallen fruit.",
        "pesticides": ["Mancozeb", "Chlorothalonil"],
        "fertilizers": ["10-10-10 fertilizer"]
    },
    "Grape Esca (Black Measles)": {
        "solution": "Remove infected vines and maintain good vineyard hygiene.",
        "pesticides": [],
        "fertilizers": ["Balanced fertilizer"]
    },
    "Grape Leaf blight (Isariopsis Leaf Spot)": {
        "solution": "Apply fungicides during early infection stages.",
        "pesticides": ["Copper-based fungicides"],
        "fertilizers": ["Nitrogen-rich fertilizer"]
    },
    "Grape healthy": {
        "solution": "Monitor for pests and diseases, practice good vineyard management.",
        "pesticides": [],
        "fertilizers": ["General-purpose fertilizer"]
    },
    "Orange Haunglongbing (Citrus greening)": {
        "solution": "Remove infected trees and control psyllid vectors.",
        "pesticides": ["Insecticides targeting psyllids"],
        "fertilizers": ["Citrus fertilizer"]
    },
    "Peach Bacterial spot": {
        "solution": "Remove infected leaves and apply copper-based fungicides.",
        "pesticides": ["Copper hydroxide"],
        "fertilizers": ["Balanced fertilizer"]
    },
    "Peach healthy": {
        "solution": "Maintain healthy soil and proper watering.",
        "pesticides": [],
        "fertilizers": ["General-purpose fertilizer"]
    },
    "Pepper, bell Bacterial spot": {
        "solution": "Remove infected plants and apply bactericides.",
        "pesticides": ["Copper-based bactericides"],
        "fertilizers": ["Balanced fertilizer"]
    },
    "Pepper, bell healthy": {
        "solution": "Monitor for pests and diseases and provide adequate water.",
        "pesticides": [],
        "fertilizers": ["General-purpose fertilizer"]
    },
    "Potato Early blight": {
        "solution": "Apply fungicides and remove infected leaves.",
        "pesticides": ["Chlorothalonil", "Azoxystrobin"],
        "fertilizers": ["Balanced fertilizer"]
    },
    "Potato Late blight": {
        "solution": "Use resistant varieties and apply fungicides promptly.",
        "pesticides": ["Metalaxyl", "Mefenoxam"],
        "fertilizers": ["Nitrogen-rich fertilizer"]
    },
    "Potato healthy": {
        "solution": "Practice good crop rotation and monitor for pests.",
        "pesticides": [],
        "fertilizers": ["General-purpose fertilizer"]
    },
    "Raspberry healthy": {
        "solution": "Keep soil moist and well-drained, prune regularly.",
        "pesticides": [],
        "fertilizers": ["Balanced fertilizer"]
    },
    "Soybean healthy": {
        "solution": "Rotate crops and monitor for pests and diseases.",
        "pesticides": [],
        "fertilizers": ["General-purpose fertilizer"]
    },
    "Squash Powdery mildew": {
        "solution": "Apply fungicides and ensure proper air circulation.",
        "pesticides": ["Sulfur", "Potassium bicarbonate"],
        "fertilizers": ["Balanced fertilizer"]
    },
    "Strawberry Leaf scorch": {
        "solution": "Prune affected leaves and apply fungicides.",
        "pesticides": ["Captan", "Thiram"],
        "fertilizers": ["Strawberry fertilizer"]
    },
    "Strawberry healthy": {
        "solution": "Ensure proper watering and soil management.",
        "pesticides": [],
        "fertilizers": ["General-purpose fertilizer"]
    },
    "Tomato Bacterial spot": {
        "solution": "Remove infected plants and apply bactericides.",
        "pesticides": ["Copper-based bactericides"],
        "fertilizers": ["Tomato fertilizer"]
    },
    "Tomato Early blight": {
        "solution": "Apply fungicides and rotate crops.",
        "pesticides": ["Chlorothalonil", "Azoxystrobin"],
        "fertilizers": ["Balanced fertilizer"]
    },
    "Tomato Late blight": {
        "solution": "Use resistant varieties and apply fungicides immediately.",
        "pesticides": ["Metalaxyl", "Mefenoxam"],
        "fertilizers": ["Tomato fertilizer"]
    },
    "Tomato Leaf Mold": {
        "solution": "Increase airflow and apply fungicides.",
        "pesticides": ["Copper-based fungicides"],
        "fertilizers": ["Nitrogen-rich fertilizer"]
    },
    "Tomato Septoria leaf spot": {
        "solution": "Remove affected leaves and apply fungicides.",
        "pesticides": ["Chlorothalonil", "Azoxystrobin"],
        "fertilizers": ["Balanced fertilizer"]
    },
    "Tomato Spider mites Two-spotted spider mite": {
        "solution": "Apply miticides and use insecticidal soap.",
        "pesticides": ["Abamectin", "Bifenthrin"],
        "fertilizers": ["General-purpose fertilizer"]
    },
    "Tomato Target Spot": {
        "solution": "Practice crop rotation and apply fungicides.",
        "pesticides": ["Fungicides with azole or strobilurin"],
        "fertilizers": ["Tomato fertilizer"]
    },
    "Tomato Tomato mosaic virus": {
        "solution": "Remove infected plants and control aphids.",
        "pesticides": ["Insecticides targeting aphids"],
        "fertilizers": []
    },
    "Tomato Tomato Yellow Leaf Curl Virus": {
        "solution": "Control whiteflies and remove infected plants.",
        "pesticides": ["Insecticides targeting whiteflies"],
        "fertilizers": []
    },
    "Tomato healthy": {
        "solution": "Maintain healthy practices and monitor for pests.",
        "pesticides": [],
        "fertilizers": ["General-purpose fertilizer"]
    },
}

@app.route('/solution/<disease_name>')
def solution(disease_name):
    solution_info = disease_solutions.get(disease_name, {})
    solution = solution_info.get("solution", "No solution available.")
    pesticides = solution_info.get("pesticides", [])
    fertilizers = solution_info.get("fertilizers", [])

    return render_template('solution.html',
                           disease_name=disease_name,
                           solution=solution,
                           pesticides=pesticides,
                           fertilizers=fertilizers)


@app.route('/download_solution/<disease_name>')
def download_solution(disease_name):
    os.makedirs('solutions', exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    solution_info = disease_solutions.get(disease_name, {})
    solution = solution_info.get("solution", "No solution available.")
    pesticides = solution_info.get("pesticides", [])
    fertilizers = solution_info.get("fertilizers", [])

    pdf.cell(200, 10, txt=f"Solution for {disease_name}", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Solution: {solution}")

    pdf.ln(5)
    pdf.cell(200, 10, txt="Recommended Pesticides:", ln=True)
    for pesticide in pesticides:
        pdf.cell(200, 10, txt=f"- {pesticide}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Recommended Fertilizers:", ln=True)
    for fertilizer in fertilizers:
        pdf.cell(200, 10, txt=f"- {fertilizer}", ln=True)

    pdf_file_path = f"solutions/{disease_name}.pdf"
    pdf.output(pdf_file_path)

    return send_file(pdf_file_path, as_attachment=True)

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    texts = data.get('text')
    target_language = data.get('lang')

    if texts and isinstance(texts, list) and all(isinstance(text, str) for text in texts) and target_language:
        if not Language.make(target_language).is_valid():
            return jsonify({'error': 'Invalid language code provided.'})

        try:
            translations = [translator.translate(text, dest=target_language).text for text in texts]
            return jsonify({'translated_texts': translations})
        except Exception as e:
            print("Error during translation:", e)  # Log the error
            return jsonify({'error': 'Translation service failed: ' + str(e)})
    return jsonify({'error': 'Invalid data: Ensure "text" is an array of strings and "lang" is a valid language code.'})

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
    try:
        sample_input = np.zeros((1, 64, 64, 3))
        _ = model.predict(sample_input)
        logger.info("Model test prediction successful")
    except Exception as e:
        logger.error(f"Model test prediction failed: {str(e)}")
        raise
    app.run(debug=True)
