// DOM Elements
const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');
const uploadSection = document.getElementById('uploadSection');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const removeBtn = document.getElementById('removeBtn');
const languageSelect = document.getElementById('languageSelect');
const genreSelect = document.getElementById('genreSelect');
const contextInput = document.getElementById('contextInput');
const submitBtn = document.getElementById('submitBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const songTitle = document.getElementById('songTitle');
const songArtist = document.getElementById('songArtist');
const songSummary = document.getElementById('songSummary');
const spotifyLink = document.getElementById('spotifyLink');
const googleSearchLink = document.getElementById('googleSearchLink');
const tryAgainBtn = document.getElementById('tryAgainBtn');
const spotifyEmbed = document.getElementById('spotifyEmbed');
const spotifyPlayer = document.getElementById('spotifyPlayer');
const resultImagePreview = document.getElementById('resultImagePreview');
const igSongTitle = document.getElementById('igSongTitle');
const igSongArtist = document.getElementById('igSongArtist');

// State
let selectedFile = null;
let uploadedImageDataUrl = null;
let loadingMessageInterval = null;

// API Base URL - change this if deploying
const API_BASE_URL = 'https://song-suggestor-production.up.railway.app';  // Local development server

// Loading Messages Array - Persuasive and engaging messages
const loadingMessages = [
    "Hang In There, Your Perfect Track Is Loading ✨",
    "Curating The Ideal Vibe Just For You 🎵",
    "Analyzing Your Aesthetic Energy 📸",
    "Matching Beats To Your Mood 💫",
    "Your Soundtrack Is Almost Ready 🎧",
    "Finding That Perfect Story Song 📱",
    "Vibes Are Loading... This Is Gonna Be Good 🔥",
    "Creating Your Next Main Character Moment ✨",
    "Almost There, Trust The Process 💜",
    "Your Perfect Match Is Worth The Wait 🎯",
    "Cooking Up Something Special For You 👨‍🍳",
    "The Algorithm Is Working Its Magic ✨",
    "Your Story Deserves The Perfect Soundtrack 📖",
    "Matching Frequencies To Your Energy 🌟",
    "Just A Few More Seconds Of Patience 💎"
];

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
    const context = contextInput.value.trim();
    
    // Show loading state
    uploadSection.classList.add('hidden');
    document.querySelector('.options-section').classList.add('hidden');
    submitBtn.classList.add('hidden');
    loading.classList.remove('hidden');
    
    // Hide info sections and footer when generating song
    const infoSections = document.querySelectorAll('.info-section');
    infoSections.forEach(section => section.classList.add('hidden'));
    
    const footer = document.querySelector('.footer');
    if (footer) footer.classList.add('hidden');
    
    // Start loading message rotation
    startLoadingMessages();
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('language', language);
        formData.append('genre', genre);
        if (context) {
            formData.append('context', context);
        }
        
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
        
        // Stop loading message rotation
        stopLoadingMessages();
        
        // Hide loading and show results
        loading.classList.add('hidden');
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        
        // Stop loading message rotation
        stopLoadingMessages();
        
        loading.classList.add('hidden');
        showNotification(`😢 ${error.message}`, 'error');
        
        // Show form again
        uploadSection.classList.remove('hidden');
        document.querySelector('.options-section').classList.remove('hidden');
        submitBtn.classList.remove('hidden');
        
        // Show info sections and footer again on error
        const infoSections = document.querySelectorAll('.info-section');
        infoSections.forEach(section => section.classList.remove('hidden'));
        
        const footer = document.querySelector('.footer');
        if (footer) footer.classList.remove('hidden');
    }
}

// Loading Message Management
function startLoadingMessages() {
    const loadingMessage = document.getElementById('loadingMessage');
    let currentIndex = 0;
    
    // Set the first message
    loadingMessage.textContent = loadingMessages[currentIndex];
    
    // Create interval to cycle through messages
    loadingMessageInterval = setInterval(() => {
        // Fade out current message
        loadingMessage.classList.add('fade-out');
        
        setTimeout(() => {
            // Update to next message
            currentIndex = (currentIndex + 1) % loadingMessages.length;
            loadingMessage.textContent = loadingMessages[currentIndex];
            
            // Fade in new message
            loadingMessage.classList.remove('fade-out');
            loadingMessage.classList.add('fade-in');
            
            setTimeout(() => {
                loadingMessage.classList.remove('fade-in');
            }, 300);
        }, 300);
    }, 2500); // Change message every 2.5 seconds
}

function stopLoadingMessages() {
    if (loadingMessageInterval) {
        clearInterval(loadingMessageInterval);
        loadingMessageInterval = null;
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
        googleSearchLink.classList.add('hidden');
    } else if (data.google_search_url) {
        // Show Google search link when Spotify is not available
        googleSearchLink.href = data.google_search_url;
        googleSearchLink.classList.remove('hidden');
        spotifyLink.classList.add('hidden');
        
        // Show notification about fallback
        if (data.spotify_error) {
            showNotification('🔍 Song not found on Spotify, try Google search!', 'info');
        }
    } else {
        spotifyLink.classList.add('hidden');
        googleSearchLink.classList.add('hidden');
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
    
    // Show info sections and footer again when resetting
    const infoSections = document.querySelectorAll('.info-section');
    infoSections.forEach(section => section.classList.remove('hidden'));
    
    const footer = document.querySelector('.footer');
    if (footer) footer.classList.remove('hidden');
    
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
