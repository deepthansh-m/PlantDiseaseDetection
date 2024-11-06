function predictDisease() {
    const fileInput = document.getElementById('imageUpload');
    const resultElement = document.getElementById('predictionResult');
    const solutionButton = document.getElementById('solutionButton');

    // Reset previous results
    resultElement.innerText = '';
    solutionButton.style.display = 'none';

    // Validate file input
    if (!fileInput.files || !fileInput.files[0]) {
        resultElement.innerText = 'Please select an image file first';
        return;
    }

    const file = fileInput.files[0];

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
        resultElement.innerText = 'Please select a valid image file (JPG, PNG, or GIF)';
        return;
    }

    // Validate file size
    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
        resultElement.innerText = 'File size too large. Please select an image under 16MB.';
        return;
    }

    // Show loading state
    resultElement.innerText = 'Analyzing image...';
    const loadingDots = setInterval(() => {
        if (resultElement.innerText.endsWith('...')) {
            resultElement.innerText = 'Analyzing image';
        } else {
            resultElement.innerText += '.';
        }
    }, 500);

    const formData = new FormData();
    formData.append('file', file);

    fetch('/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        clearInterval(loadingDots);

        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            });
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
        resultElement.innerText = `Error: ${error.message}`;
        // Add debugging information
        console.log('File details:', {
            name: file.name,
            type: file.type,
            size: file.size
        });
    })
    .finally(() => {
        clearInterval(loadingDots);
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
