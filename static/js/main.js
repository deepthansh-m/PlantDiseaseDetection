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
        const resultElement = document.getElementById('predictionResult');
        const solutionButton = document.getElementById('solutionButton');

        if (data.disease) {
            // Display prediction result with disease name and confidence
            resultElement.innerText = `Disease: ${data.disease} (Confidence: ${data.confidence}%)`;

            // Enable and configure the solution button
            solutionButton.style.display = 'inline-block';
            solutionButton.onclick = function() {
                window.location.href = data.solution_url;
            };
        } else {
            // Handle error returned from the prediction endpoint
            resultElement.innerText = 'Error: ' + data.error;
            solutionButton.style.display = 'none';
        }
    })
    .catch(error => {
        // Handle network or unexpected errors
        document.getElementById('predictionResult').innerText = 'Error: ' + error.message;
        document.getElementById('solutionButton').style.display = 'none';
    });
}

function translateText() {
    const translatableElements = document.querySelectorAll('.translatable');
    const lang = document.getElementById('languageSelect').value;

    console.log("Translating text:", textArray, "to language:", lang);

    const textArray = Array.from(translatableElements).map(element => element.innerText);

    fetch('/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textArray, lang }) // Ensure lang is a valid language code
    })
    .then(response => response.json())
    .then(data => {
        if (data.translated_texts && data.translated_texts.length === textArray.length) {
            translatableElements.forEach((element, index) => {
                element.innerText = data.translated_texts[index];
            });
        } else {
            console.error('Translation response error:', data); // Log error for debugging
            alert('Translation failed: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Fetch error:', error); // Log fetch errors for debugging
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
            // Play the audio returned by the server
            const audio = new Audio(data.audio_url);
            audio.play();
        } else {
            // Handle error from the text-to-speech endpoint
            alert('Text-to-Speech conversion failed. Please try again.');
        }
    })
    .catch(error => {
        // Handle network or unexpected errors
        alert('Error: ' + error.message);
    });
}
