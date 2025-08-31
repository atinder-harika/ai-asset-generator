// Get references to DOM elements
const generateBtn = document.getElementById('generateBtn');
const promptInput = document.getElementById('prompt');
const loadingIndicator = document.getElementById('loadingIndicator');
const imageContainer = document.getElementById('imageContainer');
const generatedImage = document.getElementById('generatedImage');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

// This is the new backend API endpoint.
const backendUrl = 'http://localhost:5000/generate-image';

// Function to handle image generation
async function generateImage() {
    // Hide previous results and show loading indicator
    imageContainer.classList.add('hidden');
    errorMessage.classList.add('hidden');
    loadingIndicator.classList.remove('hidden');
    generateBtn.disabled = true;

    const userPrompt = promptInput.value.trim();
    if (!userPrompt) {
        // Show error if prompt is empty
        loadingIndicator.classList.add('hidden');
        errorMessage.classList.remove('hidden');
        errorText.textContent = "Please enter a prompt.";
        generateBtn.disabled = false;
        return;
    }

    try {
        // The API call is now to our local Python backend
        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: userPrompt })
        });

        const result = await response.json();

        if (response.ok) {
            // Update the image source with the base64-encoded image
            if (result.image) {
                const imageUrl = `data:image/png;base64,${result.image}`;
                generatedImage.src = imageUrl;
                imageContainer.classList.remove('hidden');
            } else {
                throw new Error(result.error || "API response was successful but no image data was found.");
            }
        } else {
            throw new Error(result.error || "An unknown error occurred.");
        }

    } catch (error) {
        // Handle any errors during the fetch or parsing
        console.error("Error generating image:", error);
        errorText.textContent = `An error occurred: ${error.message}`;
        errorMessage.classList.remove('hidden');
    } finally {
        // Hide loading indicator and enable the button
        loadingIndicator.classList.add('hidden');
        generateBtn.disabled = false;
    }
}

// Add event listener to the button
generateBtn.addEventListener('click', generateImage);

// Allow generating on 'Enter' key press
promptInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        generateImage();
    }
});