// main.js - Music Player & Navigation
console.log('main.js: Initializing...');

// ============================================
// GLOBAL HELPER FUNCTIONS (accessible from anywhere)
// ============================================

window.playSong = function (songId) {
    console.log('DEBUG: playSong llamado con ID:', songId);
    console.log('DEBUG: Redirigiendo al reproductor...');
    // Se cambia de / a /player/ porque el reproductor está en esa ruta
    window.location.href = `/player/?id=${songId}`;
};

window.openArtist = function (artistId) {
    console.log('main.js: openArtist called for ID:', artistId);
    window.location.href = `/artista/${artistId}/`;
};

window.openAlbum = function (albumId) {
    console.log('main.js: openAlbum called for ID:', albumId);
    window.location.href = `/album/${albumId}/`;
};

window.openPlaylist = function (playlistId) {
    console.log('main.js: openPlaylist called for ID:', playlistId);
    alert('Funcionalidad de playlists en desarrollo');
};

// ============================================
// INITIALIZATION - Se ejecuta cuando el DOM está listo
// ============================================

document.addEventListener("DOMContentLoaded", function () {
    console.log('main.js: DOMContentLoaded - Starting initialization');

    // ============================================
    // 1. DETECTAR SI ESTAMOS EN LA PÁGINA DE REPRODUCTOR
    // ============================================
    const audioPlayer = document.getElementById('audioPlayer');
    const isPlayerPage = audioPlayer !== null;

    if (isPlayerPage) {
        console.log('main.js: Player page detected - Setting up player features');
        try {
            setupPlayerFeatures();
        } catch (e) {
            console.error('main.js: ERROR setting up player:', e);
        }
    }

    // ============================================
    // 2. DETECTAR SI ESTAMOS EN LA PÁGINA DE LIBRERÍA
    // ============================================
    const isLibraryPage = document.getElementById('librarySearch') !== null;

    if (isLibraryPage) {
        console.log('main.js: Library page detected - Setting up library features');
        setupLibraryFeatures();
    }

    // ============================================
    // 3. SETUP SEARCH SUGGESTIONS (Global)
    // ============================================
    setupSearchSuggestions();

    // ============================================
    // 4. SETUP GLOBAL EVENT DELEGATION (funciona en todas las páginas)
    // ============================================
    setupGlobalEventDelegation();

    // ============================================
    // 5. SETUP GLOBAL KEYBOARD SHORTCUTS
    // ============================================
    setupKeyboardShortcuts();

    console.log('main.js: Initialization complete');
});

// ============================================
// PLAYER FEATURES (solo para index.html)
// ============================================

function setupPlayerFeatures() {
    console.log('main.js: Setting up player features');

    const audio = document.getElementById("audioPlayer");
    if (!audio) {
        console.error('main.js: No audio element found');
        return;
    }

    // Elementos del DOM
    const playBtn = document.querySelector(".play");
    const progressBar = document.querySelector(".playbar_inner");
    const playbar = document.querySelector(".playbar");
    const shuffleBtn = document.getElementById("shuffleBtn");
    const repeatBtn = document.getElementById("repeatBtn");
    const nextBtn = document.getElementById("nextBtn");
    const prevBtn = document.getElementById("prevBtn");
    const volumeControl = document.getElementById("volumeControl");
    const currentTimeElement = document.getElementById("currentTime");
    const durationTimeElement = document.getElementById("durationTime");

    // Datos de la playlist
    const listaCancionesElement = document.getElementById("listaCanciones");
    const currentIdElement = document.getElementById("currentId");

    let listaIds = [];
    let currentId = null;
    let currentIndex = -1;
    let isShuffle = false;
    let isRepeat = false;
    let originalList = [];

    // Cargar datos de la playlist
    if (listaCancionesElement && currentIdElement) {
        try {
            listaIds = JSON.parse(listaCancionesElement.value);
            currentId = parseInt(currentIdElement.value);
            currentIndex = listaIds.indexOf(currentId);
            originalList = [...listaIds];

            console.log('main.js: Playlist data loaded', {
                totalSongs: listaIds.length,
                currentId: currentId,
                currentIndex: currentIndex
            });
        } catch (error) {
            console.error('main.js: Error parsing playlist data:', error);
        }
    }

    // ================= FUNCIONES UTILITARIAS =================
    function formatTime(seconds) {
        if (isNaN(seconds) || seconds === Infinity || seconds === undefined) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    function shuffleArray(array) {
        const newArray = [...array];
        for (let i = newArray.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
        }
        return newArray;
    }

    function playNextSong() {
        if (listaIds.length === 0) return;
        let nextIndex = currentIndex + 1;
        if (nextIndex >= listaIds.length) nextIndex = 0;
        const nextId = listaIds[nextIndex];
        console.log('main.js: Playing next song ID:', nextId);
        // Usar /player/ para mantenerse en el reproductor
        window.location.href = `/player/?id=${nextId}`;
    }

    function playPrevSong() {
        if (listaIds.length === 0) return;
        let prevIndex = currentIndex - 1;
        if (prevIndex < 0) prevIndex = listaIds.length - 1;
        const prevId = listaIds[prevIndex];
        console.log('main.js: Playing prev song ID:', prevId);
        // Usar /player/ para mantenerse en el reproductor
        window.location.href = `/player/?id=${prevId}`;
    }

    // ================= INICIALIZAR AUDIO =================
    audio.addEventListener('loadedmetadata', function () {
        console.log("main.js: Metadata loaded. Duration:", audio.duration);
        if (durationTimeElement && audio.duration && !isNaN(audio.duration)) {
            durationTimeElement.textContent = formatTime(audio.duration);
        }
    });

    audio.addEventListener('canplay', () => {
        console.log("main.js: Audio can play now.");
    });

    // Intentar reproducción automática si hay una canción cargada
    if (audio.src || audio.querySelector('source')) {
        // En Chrome, a veces hay que llamar a load() antes de play() tras un cambio de página
        audio.load();

        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise.then(() => {
                console.log("main.js: Auto-play successful");
            }).catch(error => {
                console.log("main.js: Auto-play prevented. Waiting for user interaction.", error);
                // Si falla, nos aseguramos que el botón muestre 'Play'
                if (playBtn) {
                    playBtn.classList.remove('bi-pause-circle-fill');
                    playBtn.classList.add('bi-play-circle-fill');
                }
            });
        }
    }

    // ================= BARRA DE PROGRESO (CLICK & DRAG) =================
    if (playbar && progressBar && audio) {
        let isDragging = false;

        const updateProgress = (e) => {
            const rect = playbar.getBoundingClientRect();
            const clickPosition = e.clientX - rect.left;
            const percentage = (clickPosition / rect.width) * 100;
            const clampedPercentage = Math.max(0, Math.min(100, percentage));

            progressBar.style.width = `${clampedPercentage}%`;

            if (audio.duration && !isNaN(audio.duration)) {
                const newTime = (clampedPercentage / 100) * audio.duration;
                audio.currentTime = newTime;
                if (currentTimeElement) {
                    currentTimeElement.textContent = formatTime(newTime);
                }
            }
        };

        playbar.addEventListener('mousedown', (e) => {
            isDragging = true;
            updateProgress(e);
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) updateProgress(e);
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        // Click simple también funciona a través de mousedown
    }

    // ================= ACTUALIZAR BARRA AUTOMÁTICAMENTE =================
    let lastUpdate = 0;
    audio.addEventListener('timeupdate', () => {
        const now = Date.now();
        if (now - lastUpdate < 200) return; // Limitar a 5 veces por segundo
        lastUpdate = now;

        if (audio.duration && !isNaN(audio.duration) && audio.duration !== Infinity && audio.duration > 0) {
            requestAnimationFrame(() => {
                const percent = (audio.currentTime / audio.duration) * 100;
                progressBar.style.width = `${Math.min(100, percent)}%`;
                if (currentTimeElement) {
                    currentTimeElement.textContent = formatTime(audio.currentTime);
                }
            });
        }
    });

    // Manejar errores específicos de la fuente de audio
    audio.addEventListener('error', (e) => {
        console.error("main.js: Audio Error Event:", e);
        console.error("main.js: Error Code:", audio.error ? audio.error.code : 'unknown');
        console.error("main.js: Error Message:", audio.error ? audio.error.message : 'no message');

        if (audio.error && audio.error.code === 4) {
            console.warn("main.js: Source not supported or file not found.");
        }
    });

    // ================= BOTÓN PLAY/PAUSE =================
    if (playBtn) {
        playBtn.addEventListener('click', function () {
            if (audio.paused) {
                audio.play().catch(err => console.error("Error al reproducir tras clic:", err));
            } else {
                audio.pause();
            }
        });

        audio.addEventListener('play', () => {
            playBtn.classList.remove('bi-play-circle-fill');
            playBtn.classList.add('bi-pause-circle-fill');
        });

        audio.addEventListener('pause', () => {
            playBtn.classList.remove('bi-pause-circle-fill');
            playBtn.classList.add('bi-play-circle-fill');
        });

        // Sincronizar estado inicial si ya está reproduciendo
        if (!audio.paused) {
            playBtn.classList.remove('bi-play-circle-fill');
            playBtn.classList.add('bi-pause-circle-fill');
        }
    }

    // ================= BOTÓN SHUFFLE =================
    if (shuffleBtn) {
        const savedShuffle = localStorage.getItem('playerShuffle');
        if (savedShuffle === 'true') {
            isShuffle = true;
            shuffleBtn.classList.add('active');
            let tempList = [...originalList].filter(id => id !== currentId);
            listaIds = [currentId, ...shuffleArray(tempList)];
            currentIndex = 0;
        }

        shuffleBtn.addEventListener('click', () => {
            isShuffle = !isShuffle;
            shuffleBtn.classList.toggle('active', isShuffle);
            localStorage.setItem('playerShuffle', isShuffle);

            if (isShuffle) {
                let tempList = [...originalList].filter(id => id !== currentId);
                listaIds = [currentId, ...shuffleArray(tempList)];
            } else {
                listaIds = [...originalList];
            }
            currentIndex = listaIds.indexOf(currentId);
        });
    }

    // ================= BOTÓN REPEAT =================
    if (repeatBtn) {
        const savedRepeat = localStorage.getItem('playerRepeat');
        if (savedRepeat === 'true') {
            isRepeat = true;
            repeatBtn.classList.add('active');
        }

        repeatBtn.addEventListener('click', () => {
            isRepeat = !isRepeat;
            repeatBtn.classList.toggle('active', isRepeat);
            localStorage.setItem('playerRepeat', isRepeat);
        });
    }

    // ================= BOTONES NEXT/PREV =================
    if (nextBtn) {
        nextBtn.addEventListener('click', playNextSong);
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', playPrevSong);
    }

    // ================= CONTROL DE VOLUMEN =================
    if (volumeControl) {
        volumeControl.addEventListener('input', (e) => {
            audio.volume = parseFloat(e.target.value);
        });
        audio.volume = volumeControl.value || 0.5;
    }

    // ================= CUANDO TERMINA LA CANCIÓN =================
    audio.addEventListener('ended', () => {
        if (isRepeat) {
            audio.currentTime = 0;
            audio.play();
        } else {
            playNextSong();
        }
    });
}

// ============================================
// LIBRARY FEATURES (solo para library.html)
// ============================================

function setupLibraryFeatures() {
    console.log('main.js: Setting up library features');

    const librarySearch = document.getElementById('librarySearch');
    if (librarySearch) {
        librarySearch.addEventListener('input', function (e) {
            const searchTerm = e.target.value.toLowerCase().trim();

            document.querySelectorAll('.item-card.cancion').forEach(card => {
                const title = card.querySelector('.item-name')?.textContent.toLowerCase() || '';
                const artist = card.querySelector('.item-subtitle')?.textContent.toLowerCase() || '';
                card.style.display = (title.includes(searchTerm) || artist.includes(searchTerm)) ? 'block' : 'none';
            });

            document.querySelectorAll('.song-item').forEach(item => {
                const title = item.querySelector('.song-title')?.textContent.toLowerCase() || '';
                const artist = item.querySelector('.song-artist')?.textContent.toLowerCase() || '';
                item.style.display = (title.includes(searchTerm) || artist.includes(searchTerm)) ? 'flex' : 'none';
            });

            document.querySelectorAll('.item-card.artist').forEach(card => {
                const name = card.querySelector('.item-name')?.textContent.toLowerCase() || '';
                card.style.display = name.includes(searchTerm) ? 'block' : 'none';
            });

            document.querySelectorAll('.item-card.album').forEach(card => {
                const title = card.querySelector('.item-name')?.textContent.toLowerCase() || '';
                const artist = card.querySelector('.item-subtitle')?.textContent.toLowerCase() || '';
                card.style.display = (title.includes(searchTerm) || artist.includes(searchTerm)) ? 'block' : 'none';
            });
        });
    }

    const navItems = document.querySelectorAll('.library-sidebar .nav-item');
    const sections = document.querySelectorAll('.library-section');

    if (navItems.length > 0 && sections.length > 0) {
        function showSection(sectionId) {
            sections.forEach(section => section.style.display = 'none');
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.style.display = 'block';
                setTimeout(() => {
                    targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 50);
            }
        }

        navItems.forEach(item => {
            item.addEventListener('click', function (e) {
                e.preventDefault();
                navItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                const sectionId = this.getAttribute('href').substring(1);
                showSection(sectionId);
            });
        });

        showSection('recientes');
    }
}

// ============================================
// GLOBAL EVENT DELEGATION
// ============================================

function setupGlobalEventDelegation() {
    document.addEventListener('click', function (e) {
        // Clic en elementos con data-id
        const elementWithDataId = e.target.closest('[data-id]');
        if (elementWithDataId && !e.target.closest('a')) {
            const dataId = elementWithDataId.getAttribute('data-id');
            const cls = elementWithDataId.className;
            if (dataId) {
                e.preventDefault();
                e.stopPropagation();
                if (cls.includes('cancion') || cls.includes('song')) window.playSong(dataId);
                else if (cls.includes('artist')) window.openArtist(dataId);
                else if (cls.includes('album')) window.openAlbum(dataId);
            }
        }
    });
}

function setupSearchSuggestions() {
    const searchInput = document.getElementById('searchInput');
    const suggestionsBox = document.getElementById('suggestionsBox');

    if (!searchInput || !suggestionsBox) return;

    searchInput.addEventListener('input', function () {
        const query = this.value.trim();
        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }

        fetch(`/api/sugerencias/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                suggestionsBox.innerHTML = '';
                if (data.results && data.results.length > 0) {
                    data.results.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'suggestion-item';
                        div.innerHTML = `
                            <div class="s-title">${item.titulo}</div>
                            <div class="s-artist">${item.artista}</div>
                        `;
                        div.onclick = () => window.playSong(item.id);
                        suggestionsBox.appendChild(div);
                    });
                    suggestionsBox.style.display = 'block';
                } else {
                    suggestionsBox.style.display = 'none';
                }
            })
            .catch(err => console.error('Error fetching suggestions:', err));
    });

    // Cerrar sugerencias al hacer clic fuera
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = 'none';
        }
    });
}

// ============================================
// GLOBAL KEYBOARD SHORTCUTS
// ============================================

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function (e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) return;

        const audio = document.getElementById("audioPlayer");
        if (!audio) return;

        switch (e.code) {
            case 'Space':
                e.preventDefault();
                const playBtn = document.querySelector(".play");
                if (playBtn) playBtn.click();
                break;
            case 'ArrowRight':
                if (e.ctrlKey) {
                    const nextBtn = document.getElementById("nextBtn");
                    if (nextBtn) nextBtn.click();
                } else {
                    audio.currentTime = Math.min(audio.duration, audio.currentTime + 10);
                }
                break;
            case 'ArrowLeft':
                if (e.ctrlKey) {
                    const prevBtn = document.getElementById("prevBtn");
                    if (prevBtn) prevBtn.click();
                } else {
                    audio.currentTime = Math.max(0, audio.currentTime - 10);
                }
                break;
            case 'KeyM':
                if (e.ctrlKey) audio.muted = !audio.muted;
                break;
        }
    });
}