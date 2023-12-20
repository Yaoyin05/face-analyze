from flask import Flask, render_template, request, redirect,send_from_directory
import os
import cv2
from deepface import DeepFace
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dictionary for translating emotions and other labels
translation_dict = {
    'angry': '生氣',
    'disgust': '厭惡',
    'fear': '害怕',
    'happy': '開心',
    'sad': '傷心',
    'surprise': '驚訝',
    'neutral': '中性',
    'Woman': '女性',
    'Man': '男性',
    'asian': '亞洲人',
    'indian': '印度人',
    'black': '黑人',
    'white': '白人',
    'middle eastern': '中東人',
    'latino hispanic': '拉丁美洲/西班牙裔'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def translate_labels(result):
    translated_result = result.copy()

    # Translate emotion labels
    translated_result[0]['emotion'] = {translation_dict.get(key, key): value for key, value in result[0]['emotion'].items()}
    translated_result[0]['dominant_emotion'] = translation_dict.get(result[0]['dominant_emotion'], result[0]['dominant_emotion'])

    # Translate gender labels
    translated_result[0]['gender'] = {translation_dict.get(key, key): value for key, value in result[0]['gender'].items()}
    translated_result[0]['dominant_gender'] = translation_dict.get(result[0]['dominant_gender'], result[0]['dominant_gender'])

    # Translate race labels
    translated_result[0]['race'] = {translation_dict.get(key, key): value for key, value in result[0]['race'].items()}
    translated_result[0]['dominant_race'] = translation_dict.get(result[0]['dominant_race'], result[0]['dominant_race'])

    return translated_result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        analyze_result = analyze_image(file_path)
        translated_result = translate_labels(analyze_result)
        return render_template('index.html', result=translated_result, image_path=file_path)
    else:
        return redirect(request.url)

def analyze_image(img_path):
    img = cv2.imread(img_path)
    analyze = DeepFace.analyze(img_path)
    return analyze

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)