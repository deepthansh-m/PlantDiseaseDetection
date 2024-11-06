function predictDisease() {
    const fileInput = document.getElementById('imageUpload');
    const resultElement = document.getElementById('predictionResult');
    const solutionButton = document.getElementById('solutionButton');

    if (!fileInput.files || !fileInput.files[0]) {
        resultElement.innerText = 'Please select an image file first';
        solutionButton.style.display = 'none';
        return;
    }

    const file = fileInput.files[0];
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
        resultElement.innerText = 'Please select a valid image file (JPG, PNG, or GIF)';
        solutionButton.style.display = 'none';
        return;
    }

    resultElement.innerText = 'Analyzing image...';
    solutionButton.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    fetch('/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }

        if (data.disease) {
            resultElement.innerText = `Disease: ${data.disease} (Confidence: ${data.confidence}%)`;
            sessionStorage.setItem('disease', data.disease);
            solutionButton.style.display = 'inline-block';
            solutionButton.onclick = function() {
                window.location.href = data.solution_url;
            };
        }
    })
    .catch(error => {
        console.error('Error:', error);
        resultElement.innerText = 'Error: ' + error.message;
        solutionButton.style.display = 'none';
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
