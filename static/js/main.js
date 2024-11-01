function predictDisease() {
    const fileInput = document.getElementById('imageUpload');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.disease) {
            document.getElementById('predictionResult').innerText = `Disease: ${data.disease} (Confidence: ${data.confidence})`;
        } else {
            document.getElementById('predictionResult').innerText = 'Error: ' + data.error;
        }
    });
}

function translateText() {
    const text = document.getElementById('predictionResult').innerText;
    const lang = document.getElementById('languageSelect').value;

    fetch('/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, lang })
    })
    .then(response => response.json())
    .then(data => {
        if (data.translated_text) {
            document.getElementById('predictionResult').innerText = data.translated_text;
        }
    });
}

function textToSpeech() {
    const text = document.getElementById('predictionResult').innerText;

    fetch('/text_to_speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    })
    .then(response => response.json())
    .then(data => {
        if (data.audio_url) {
            const audio = new Audio(data.audio_url);
            audio.play();
        }
    });
}
