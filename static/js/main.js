function predictDisease() {
    const fileInput = document.getElementById('imageUpload');

    if (!fileInput.files.length) {
        alert("No file selected.");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    console.log("Uploading file:", fileInput.files[0]);

    fetch('/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultElement = document.getElementById('predictionResult');
        const solutionButton = document.getElementById('solutionButton');

        if (data.disease) {
            resultElement.innerText = `Disease: ${data.disease} (Confidence: ${data.confidence}%)`;
            solutionButton.style.display = 'inline-block';
            solutionButton.onclick = function() {
                window.location.href = data.solution_url;
            };
        } else {
            resultElement.innerText = 'Error: ' + data.error;
            solutionButton.style.display = 'none';
        }
    })
    .catch(error => {
        document.getElementById('predictionResult').innerText = 'Error: ' + error.message;
        document.getElementById('solutionButton').style.display = 'none';
    });
}

function translateText() {
    const translatableElements = document.querySelectorAll('.translatable');
    const lang = document.getElementById('languageSelect').value;

    const textArray = Array.from(translatableElements).map(element => element.innerText.trim());

    const indicesToTranslate = textArray.map((text, index) => text !== '' ? index : null).filter(index => index !== null);

    console.log("Translating text:", textArray, "to language:", lang);

    if (indicesToTranslate.length === 0) {
        console.warn('No text available for translation.');
        return;
    }

    fetch('/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textArray.filter(text => text !== ''), lang })
    })
    .then(response => response.json())
    .then(data => {
        if (data.translated_texts && data.translated_texts.length === indicesToTranslate.length) {
            indicesToTranslate.forEach((originalIndex, translatedIndex) => {
                translatableElements[originalIndex].innerText = data.translated_texts[translatedIndex] || ''; // Maintain null/empty where applicable
            });
        } else {
            console.error('Translation response error:', data);
            alert('Translation failed: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert('Error: ' + error.message);
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
        } else {
            alert('Text-to-Speech conversion failed. Please try again.');
        }
    })
    .catch(error => {
        alert('Error: ' + error.message);
    });
}
