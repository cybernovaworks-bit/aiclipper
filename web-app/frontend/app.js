document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const urlInput = document.getElementById('youtube-url');
    const subtitleStyleSelect = document.getElementById('subtitle-style');
    const statusMessage = document.getElementById('status-message');
    const statusText = document.getElementById('status-text');
    const resultsSection = document.getElementById('results');
    const clipsContainer = document.getElementById('clips-container');

    generateBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        const subtitleStyle = subtitleStyleSelect.value;

        if (!url || !url.includes('youtube.com') && !url.includes('youtu.be')) {
            alert('Please enter a valid YouTube URL');
            return;
        }

        // Show loading state
        generateBtn.disabled = true;
        document.querySelector('.btn-text').textContent = 'Processing...';
        statusMessage.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        clipsContainer.innerHTML = '';

        // Simulating the stages of AI processing for UX
        const stages = [
            "Downloading YouTube video...",
            "Transcribing audio with Whisper AI...",
            "Analyzing text for viral hooks...",
            "Cropping clips to 9:16...",
            "Adding magic captions..."
        ];

        let stageIndex = 0;
        const stageInterval = setInterval(() => {
            if (stageIndex < stages.length) {
                statusText.textContent = stages[stageIndex];
                stageIndex++;
            }
        }, 3000);

        try {
            // BACKEND API URL:
            // 1. For Local Testing: "http://127.0.0.1:8000/process-video" (If running via run_backend.bat)
            // 2. For Live Website: "https://<your-space-name>.hf.space/process-video"
            const BACKEND_URL = 'http://127.0.0.1:8000/process-video'; // <-- Isko change karna hoga baad mein

            // Making POST request to FastAPI backend
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    subtitle_style: subtitleStyle
                })
            });

            if (!response.ok) {
                throw new Error("Backend processing failed");
            }

            const data = await response.json();

            clearInterval(stageInterval);

            // Response data from backend
            const mockData = data.clips || [
                {
                    title: "The Ultimate Hook",
                    score: "99/100 Viral Score",
                    videoUrl: "https://www.w3schools.com/html/mov_bbb.mp4" // Placeholder video
                },
                {
                    title: "Mind Blowing Fact",
                    score: "92/100 Viral Score",
                    videoUrl: "https://www.w3schools.com/html/mov_bbb.mp4"
                },
                {
                    title: "Perfect Ending",
                    score: "85/100 Viral Score",
                    videoUrl: "https://www.w3schools.com/html/mov_bbb.mp4"
                }
            ];

            renderClips(mockData);

        } catch (error) {
            clearInterval(stageInterval);
            statusText.textContent = "Error processing video. Please try again.";
            statusText.style.color = "#ff4444";
        } finally {
            // Reset button
            generateBtn.disabled = false;
            document.querySelector('.btn-text').textContent = 'Generate Clips';
            statusMessage.classList.add('hidden');
        }
    });

    function renderClips(clips) {
        resultsSection.classList.remove('hidden');
        // Scroll to results smoothly
        resultsSection.scrollIntoView({ behavior: 'smooth' });

        clips.forEach((clip, index) => {
            const card = document.createElement('div');
            card.className = 'clip-card';
            card.innerHTML = `
                <video class="clip-video" src="${clip.videoUrl}" controls loop muted></video>
                <div class="clip-info">
                    <div class="clip-score"><i class="fa-solid fa-fire"></i> ${clip.score}</div>
                    <h3 class="clip-title">Clip ${index + 1}: ${clip.title}</h3>
                    <a href="${clip.videoUrl}" download="Viral_Clip_${index + 1}.mp4" class="download-btn">
                        <i class="fa-solid fa-download"></i> Download HD
                    </a>
                </div>
            `;
            clipsContainer.appendChild(card);
        });
    }
});