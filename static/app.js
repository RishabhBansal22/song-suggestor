// DOM Elements
const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');
const uploadSection = document.getElementById('uploadSection');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const removeBtn = document.getElementById('removeBtn');
const languageSelect = document.getElementById('languageSelect');
const genreSelect = document.getElementById('genreSelect');
const submitBtn = document.getElementById('submitBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const songTitle = document.getElementById('songTitle');
const songArtist = document.getElementById('songArtist');
const songSummary = document.getElementById('songSummary');
const spotifyLink = document.getElementById('spotifyLink');
const tryAgainBtn = document.getElementById('tryAgainBtn');
const spotifyEmbed = document.getElementById('spotifyEmbed');
const spotifyPlayer = document.getElementById('spotifyPlayer');
const resultImagePreview = document.getElementById('resultImagePreview');
const igSongTitle = document.getElementById('igSongTitle');
const igSongArtist = document.getElementById('igSongArtist');

// State
let selectedFile = null;
let uploadedImageDataUrl = null;

// API Base URL - change this if deploying
const API_BASE_URL = 'https://song-suggestor-production.up.railway.app';  // Remove trailing slash

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // File input change
    imageInput.addEventListener('change', handleFileSelect);
    
    // Remove button
    removeBtn.addEventListener('click', clearImage);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Submit button
    submitBtn.addEventListener('click', handleSubmit);
    
    // Try again button
    tryAgainBtn.addEventListener('click', resetApp);
}

// File Selection Handlers
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        validateAndPreviewFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const file = event.dataTransfer.files[0];
    if (file) {
        validateAndPreviewFile(file);
    }
}

function validateAndPreviewFile(file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showNotification('❌ oops! need an image file', 'error');
        return;
    }
    
    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showNotification('❌ image too thicc (max 10mb)', 'error');
        return;
    }
    
    selectedFile = file;
    
    // Preview image
    const reader = new FileReader();
    reader.onload = (e) => {
        uploadedImageDataUrl = e.target.result; // Store for later use
        previewImg.src = uploadedImageDataUrl;
        uploadArea.classList.add('hidden');
        imagePreview.classList.remove('hidden');
        submitBtn.disabled = false;
        
        // Add animation
        imagePreview.style.animation = 'fadeIn 0.3s ease-out';
    };
    reader.readAsDataURL(file);
}

function clearImage() {
    selectedFile = null;
    uploadedImageDataUrl = null;
    imageInput.value = '';
    previewImg.src = '';
    imagePreview.classList.add('hidden');
    uploadArea.classList.remove('hidden');
    submitBtn.disabled = true;
}

// Form Submission
async function handleSubmit() {
    if (!selectedFile) {
        showNotification('❌ pick a photo first!', 'error');
        return;
    }
    
    const language = languageSelect.value;
    const genre = genreSelect.value;
    
    // Show loading state
    uploadSection.classList.add('hidden');
    document.querySelector('.options-section').classList.add('hidden');
    submitBtn.classList.add('hidden');
    loading.classList.remove('hidden');
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('language', language);
        formData.append('genre', genre);
        
        // Make API request
        const response = await fetch(`${API_BASE_URL}/suggest-song`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'failed to get song suggestion');
        }
        
        const data = await response.json();
        
        // Hide loading and show results
        loading.classList.add('hidden');
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        loading.classList.add('hidden');
        showNotification(`😢 ${error.message}`, 'error');
        
        // Show form again
        uploadSection.classList.remove('hidden');
        document.querySelector('.options-section').classList.remove('hidden');
        submitBtn.classList.remove('hidden');
    }
}

// Display Results
function displayResults(data) {
    songTitle.textContent = data.song_title;
    songArtist.textContent = `by ${data.artist}`;
    songSummary.textContent = data.summary;
    
    // Display uploaded image in IG story preview
    if (uploadedImageDataUrl) {
        resultImagePreview.src = uploadedImageDataUrl;
        igSongTitle.textContent = data.song_title;
        igSongArtist.textContent = data.artist;
    }
    
    if (data.spotify_url) {
        spotifyLink.href = data.spotify_url;
        spotifyLink.classList.remove('hidden');
    } else {
        spotifyLink.classList.add('hidden');
    }
    
    // Display Spotify Embed if track ID is available
    if (data.spotify_id) {
        const embedUrl = `https://open.spotify.com/embed/track/${data.spotify_id}?utm_source=generator`;
        spotifyPlayer.src = embedUrl;
        spotifyEmbed.classList.remove('hidden');
    } else {
        spotifyEmbed.classList.add('hidden');
    }
    
    // Setup play button on IG preview to scroll to and highlight embed player
    const playButton = document.getElementById('igPlayButton');
    if (playButton && data.spotify_id) {
        playButton.onclick = (e) => {
            e.preventDefault();
            // Scroll to the Spotify embed player
            spotifyEmbed.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Add a pulse highlight effect
            spotifyEmbed.style.animation = 'none';
            setTimeout(() => {
                spotifyEmbed.style.animation = 'highlightPulse 0.6s ease-out';
            }, 10);
            
            showNotification('✨ scroll down to vibe check', 'info');
        };
        playButton.classList.remove('hidden');
    }
    
    results.classList.remove('hidden');
    
    // Confetti effect
    createConfetti();
}

// Reset App
function resetApp() {
    // Reset state
    clearImage();
    
    // Hide results and play button
    results.classList.add('hidden');
    const playButton = document.getElementById('igPlayButton');
    if (playButton) {
        playButton.classList.add('hidden');
    }
    
    // Show form
    uploadSection.classList.remove('hidden');
    document.querySelector('.options-section').classList.remove('hidden');
    submitBtn.classList.remove('hidden');
    
    // Scroll to top smoothly
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Notification System
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Style notification - mobile-first
    Object.assign(notification.style, {
        position: 'fixed',
        top: '1rem',
        left: '50%',
        transform: 'translateX(-50%)',
        background: type === 'error' ? '#ef4444' : '#8b5cf6',
        color: 'white',
        padding: '1rem 1.5rem',
        borderRadius: '12px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        zIndex: '1000',
        animation: 'fadeInDown 0.3s ease-out',
        fontWeight: '600',
        maxWidth: 'calc(100% - 2rem)',
        width: '90%',
        textAlign: 'center',
        fontSize: '0.95rem'
    });
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Confetti Effect
function createConfetti() {
    const colors = ['#8b5cf6', '#ec4899', '#06b6d4', '#10b981', '#f59e0b'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        
        // Random properties
        const left = Math.random() * 100;
        const delay = Math.random() * 2;
        const duration = 2 + Math.random() * 2;
        const color = colors[Math.floor(Math.random() * colors.length)];
        const rotation = Math.random() * 360;
        
        Object.assign(confetti.style, {
            position: 'fixed',
            left: `${left}%`,
            top: '-10px',
            width: '10px',
            height: '10px',
            background: color,
            opacity: '0',
            transform: `rotate(${rotation}deg)`,
            animation: `confettiFall ${duration}s ease-out ${delay}s forwards`,
            pointerEvents: 'none',
            zIndex: '999'
        });
        
        document.body.appendChild(confetti);
        
        // Remove after animation
        setTimeout(() => confetti.remove(), (duration + delay) * 1000);
    }
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }
    
    @keyframes confettiFall {
        0% {
            opacity: 1;
            transform: translateY(0) rotate(0deg);
        }
        100% {
            opacity: 0;
            transform: translateY(100vh) rotate(720deg);
        }
    }
`;
document.head.appendChild(style);

// Prevent default drag behavior on document
document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
});
