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
const tryAgainBtn = document.getElementById('tryAgainBtn');
const resultImagePreview = document.getElementById('resultImagePreview');
const igSongTitle = document.getElementById('igSongTitle');
const igSongArtist = document.getElementById('igSongArtist');

// State
let selectedFile = null;
let uploadedImageDataUrl = null;
let loadingMessageInterval = null;
let spotifyPlayers = []; // Array to track all Spotify iframe players

// API Base URL - dynamically configured
// For Vercel deployment, you need to set this in Vercel dashboard as environment variable
const API_BASE_URL = (() => {
    // Check for localhost
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // For Vercel production - always use Railway backend
    // Make sure CORS is configured on Railway to allow your Vercel domain
    return 'https://song-suggestor-production.up.railway.app';
})();

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
    setupSpotifyMessageListener();
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

// Setup listener for Spotify embed messages
function setupSpotifyMessageListener() {
    window.addEventListener('message', (event) => {
        // Verify the message is from Spotify
        if (event.origin !== 'https://open.spotify.com') {
            return;
        }
        
        try {
            const data = JSON.parse(event.data);
            
            // Check if playback started
            if (data.type === 'playback_update' && data.isPaused === false) {
                // Find which iframe sent this message
                const activeIframe = event.source;
                let activeIndex = -1;
                
                spotifyPlayers.forEach((player, index) => {
                    if (player && player.iframe && player.iframe.contentWindow === activeIframe) {
                        activeIndex = index;
                    }
                });
                
                if (activeIndex !== -1) {
                    pauseOtherPlayers(activeIndex);
                }
            }
        } catch (e) {
            // Ignore parsing errors for non-JSON messages
        }
    });
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
    // data.songs is an array of song objects
    const songs = data.songs || [];
    
    if (songs.length === 0) {
        showNotification('😢 No songs found', 'error');
        resetApp();
        return;
    }
    
    // Get the songs container
    const songsContainer = document.getElementById('songsContainer');
    songsContainer.innerHTML = ''; // Clear any existing content
    
    // Reset spotify players array
    spotifyPlayers = [];
    
    // Display uploaded image in IG story preview (use first song)
    if (uploadedImageDataUrl && songs.length > 0) {
        resultImagePreview.src = uploadedImageDataUrl;
        igSongTitle.textContent = songs[0].song_title;
        igSongArtist.textContent = songs[0].artist;
    }
    
    // Create a card for each song
    songs.forEach((song, index) => {
        const songCard = createSongCard(song, index);
        songsContainer.appendChild(songCard);
    });
    
    // Setup play button on IG preview to scroll to first song
    const playButton = document.getElementById('igPlayButton');
    if (playButton && songs[0].spotify_id) {
        playButton.onclick = (e) => {
            e.preventDefault();
            // Scroll to the songs container
            songsContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            showNotification('✨ scroll down to vibe check', 'info');
        };
        playButton.classList.remove('hidden');
    }
    
    results.classList.remove('hidden');
    
    // Confetti effect
    createConfetti();
    
    // Setup intersection observer for auto-pause on scroll (mobile horizontal scroll)
    setupScrollObserver();
}

// Setup intersection observer to pause players when scrolling away
function setupScrollObserver() {
    const options = {
        root: document.getElementById('songsContainer'),
        threshold: 0.5 // Trigger when 50% of the card is visible
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const songIndex = parseInt(entry.target.getAttribute('data-song-index'));
            
            if (!entry.isIntersecting && spotifyPlayers[songIndex]) {
                // Card scrolled out of view, pause it
                const player = spotifyPlayers[songIndex];
                if (player.isPlaying && player.iframe) {
                    const currentSrc = player.iframe.src;
                    player.iframe.src = currentSrc;
                    player.isPlaying = false;
                }
            }
        });
    }, options);
    
    // Observe all song cards
    document.querySelectorAll('.song-card').forEach(card => {
        observer.observe(card);
    });
}

// Create a song card element
function createSongCard(song, index) {
    const card = document.createElement('div');
    card.className = 'song-card';
    card.setAttribute('data-song-index', index);
    
    // Song info section
    const songInfo = document.createElement('div');
    songInfo.className = 'song-info';
    
    const songNumber = document.createElement('div');
    songNumber.className = 'song-number';
    songNumber.textContent = `Song ${index + 1}`;
    
    const songTitle = document.createElement('h3');
    songTitle.className = 'song-title';
    songTitle.textContent = song.song_title;
    
    const songArtist = document.createElement('p');
    songArtist.className = 'song-artist';
    songArtist.textContent = `by ${song.artist}`;
    
    songInfo.appendChild(songNumber);
    songInfo.appendChild(songTitle);
    songInfo.appendChild(songArtist);
    
    // Spotify Embed section (if available)
    let spotifyEmbed = null;
    if (song.spotify_id) {
        spotifyEmbed = document.createElement('div');
        spotifyEmbed.className = 'spotify-embed';
        
        const embedHeader = document.createElement('div');
        embedHeader.className = 'embed-header';
        embedHeader.innerHTML = `
            <span class="embed-icon">🎧</span>
            <span>Listen First</span>
            <span class="play-hint">▶️ Tap To Play</span>
        `;
        
        const iframeWrapper = document.createElement('div');
        iframeWrapper.className = 'iframe-wrapper';
        
        const iframe = document.createElement('iframe');
        iframe.style.borderRadius = '12px';
        iframe.width = '100%';
        iframe.height = '152';
        iframe.frameBorder = '0';
        iframe.allowfullscreen = '';
        iframe.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture';
        iframe.loading = 'lazy';
        // Add theme parameter and enable IFrame API
        iframe.src = `https://open.spotify.com/embed/track/${song.spotify_id}?utm_source=generator&theme=0`;
        iframe.setAttribute('data-song-index', index);
        iframe.id = `spotify-player-${index}`;
        
        // Add click event listener to iframe wrapper to handle play/pause
        iframeWrapper.addEventListener('click', () => {
            // Small delay to ensure the click registers on the iframe first
            setTimeout(() => {
                pauseOtherPlayers(index);
            }, 100);
        });
        
        // Store reference to this player
        spotifyPlayers[index] = {
            iframe: iframe,
            index: index,
            isPlaying: false
        };
        
        iframeWrapper.appendChild(iframe);
        spotifyEmbed.appendChild(embedHeader);
        spotifyEmbed.appendChild(iframeWrapper);
    }
    
    // Song summary
    const songSummary = document.createElement('div');
    songSummary.className = 'song-summary';
    const summaryP = document.createElement('p');
    summaryP.textContent = song.summary;
    songSummary.appendChild(summaryP);
    
    // Song actions
    const songActions = document.createElement('div');
    songActions.className = 'song-actions';
    
    if (song.spotify_url) {
        const spotifyLink = document.createElement('a');
        spotifyLink.href = song.spotify_url;
        spotifyLink.target = '_blank';
        spotifyLink.className = 'btn-spotify';
        spotifyLink.innerHTML = `
            <span class="spotify-icon">🎵</span>
            Open In Spotify
        `;
        songActions.appendChild(spotifyLink);
    } else if (song.google_search_url) {
        const googleLink = document.createElement('a');
        googleLink.href = song.google_search_url;
        googleLink.target = '_blank';
        googleLink.className = 'btn-google';
        googleLink.innerHTML = `
            <span class="google-icon">🔍</span>
            Search On Google
        `;
        songActions.appendChild(googleLink);
    }
    
    // Assemble the card
    card.appendChild(songInfo);
    if (spotifyEmbed) {
        card.appendChild(spotifyEmbed);
    }
    card.appendChild(songSummary);
    card.appendChild(songActions);
    
    return card;
}

// Pause all other Spotify players except the one at the given index
function pauseOtherPlayers(activeIndex) {
    spotifyPlayers.forEach((player, index) => {
        if (index !== activeIndex && player && player.iframe) {
            // Reload the iframe to stop playback
            // This is the most reliable way to stop Spotify embeds
            const currentSrc = player.iframe.src;
            if (player.isPlaying) {
                player.iframe.src = currentSrc;
                player.isPlaying = false;
                
                // Remove active class from the card
                const card = document.querySelector(`.song-card[data-song-index="${index}"]`);
                if (card) {
                    card.classList.remove('player-active');
                }
            }
        }
    });
    
    // Mark the active player as playing
    if (spotifyPlayers[activeIndex]) {
        spotifyPlayers[activeIndex].isPlaying = true;
        
        // Add active class to the card
        const activeCard = document.querySelector(`.song-card[data-song-index="${activeIndex}"]`);
        if (activeCard) {
            activeCard.classList.add('player-active');
        }
    }
}

// Reset App
function resetApp() {
    // Reset state
    clearImage();
    
    // Stop and clear all spotify players
    spotifyPlayers.forEach(player => {
        if (player && player.iframe) {
            player.iframe.src = '';
        }
    });
    spotifyPlayers = [];
    
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
