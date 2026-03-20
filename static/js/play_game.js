document.addEventListener('DOMContentLoaded', function() {
    // Parse initial data from template
    const initialData = window.initialGameData || null;
    
    // DOM elements
    const gameContent = document.getElementById('game-content');
    const noFlagsMessage = document.getElementById('no-flags-message');
    const noFlagsModeSpan = document.getElementById('no-flags-mode');
    const modeTitle = document.getElementById('mode-title');
    const backLink = document.getElementById('back-link');
    
    // Game state
    let currentQuestion = 1;
    let numQuestions = 1;
    let timerDuration = 30;
    let mode = '';
    let modeName = '';
    let isLastQuestion = false;
    let flag = null;
    let aliases = []; // Will store lowercase aliases for case-insensitive matching
    let timeRemaining = 0;
    let timerInterval = null;
    let isAnswered = false;
    
    // Timer elements (will be created when game loads)
    let timerSeconds = null;
    let timerProgress = null;
    let guessInput = null;
    let submitButton = null;
    let skipButton = null;
    let resultMessage = null;
    
    // Initialize game if we have data
    if (initialData && initialData.flag) {
        initializeGame(initialData);
    } else if (initialData) {
        showNoFlagsMessage(initialData);
    }
    
    function initializeGame(data) {
        // Update state
        currentQuestion = data.current_question;
        numQuestions = data.num_questions;
        timerDuration = data.timer_duration;
        mode = data.mode;
        modeName = data.mode_name;
        isLastQuestion = data.is_last_question;
        flag = data.flag;
        // Store aliases in lowercase for case-insensitive comparison, and include the country name
        aliases = [...data.aliases, flag.country_name].map(alias => alias.toLowerCase());
        
        // Update UI
        modeTitle.textContent = modeName + ' Mode';
        if (backLink) {
            backLink.href = window.backUrl || "/flagd/play/";
        }
        
        // Hide no flags message, show game content
        noFlagsMessage.style.display = 'none';
        gameContent.style.display = 'block';
        
        // Render the game
        renderGame();
        
        // Start timer
        startTimer();
    }
    
    function showNoFlagsMessage(data) {
        modeTitle.textContent = data.mode_name + ' Mode';
        if (noFlagsModeSpan) {
            noFlagsModeSpan.textContent = data.mode_name;
        }
        noFlagsMessage.style.display = 'block';
        gameContent.style.display = 'none';
    }
    
    function renderGame() {
        // Create game HTML using Bootstrap classes
        gameContent.innerHTML = `
            <div class="progress mb-4" style="height: 8px;">
                <div id="progress-fill" class="progress-bar" role="progressbar" style="width: 0%"></div>
            </div>
            
            <div class="text-center mb-3">
                <span class="badge bg-light text-dark fs-6">Question <span id="current-question-display">${currentQuestion}</span> of <span id="total-questions-display">${numQuestions}</span></span>
            </div>
            
            <div class="card border-0 shadow-sm bg-white bg-opacity-75">
                <div class="card-body p-4">
                    <div class="text-center mb-4">
                        <div class="d-inline-block bg-light p-3 rounded mb-3">
                            <span id="timer-seconds" class="display-4 fw-bold text-primary">${timerDuration}</span>
                            <span class="text-muted ms-1">seconds</span>
                        </div>
                        <div class="timer-bar">
                            <div id="timer-progress" class="timer-progress"></div>
                        </div>
                    </div>
                    
                    <div class="text-center">
                        <div class="mb-4 p-3 bg-light rounded">
                            <img
                                src="https://flagcdn.com/w320/${flag.country_code}.png"
                                srcset="https://flagcdn.com/w640/${flag.country_code}.png 2x, https://flagcdn.com/w960/${flag.country_code}.png 3x"
                                alt="Flag of ${flag.country_name}"
                                class="img-fluid flag-image"
                                style="max-width: 320px;"
                            />
                        </div>
                        
                        <div class="d-flex gap-2 justify-content-center mb-3">
                            <input type="text" id="guess-input" class="form-control" placeholder="Enter country name..." autocomplete="off" style="max-width: 300px;" />
                            <button type="button" id="submit-guess" class="btn btn-primary-custom">Submit Guess</button>
                            <button type="button" id="skip-button" class="btn btn-outline-custom">Skip</button>
                        </div>
                        
                        <div id="result-message" class="mt-3"></div>
                    </div>
                </div>
            </div>
        `;
        
        // Get references to new elements
        timerSeconds = document.getElementById('timer-seconds');
        timerProgress = document.getElementById('timer-progress');
        guessInput = document.getElementById('guess-input');
        submitButton = document.getElementById('submit-guess');
        skipButton = document.getElementById('skip-button');
        resultMessage = document.getElementById('result-message');
        
        // Update progress bar
        updateProgressBar();
        
        // Add event listeners
        submitButton.addEventListener('click', handleSubmitGuess);
        guessInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                submitButton.click();
            }
        });
        skipButton.addEventListener('click', handleSkip);
    }
    
    function updateProgressBar() {
        const percentage = (currentQuestion / numQuestions) * 100;
        document.getElementById('progress-fill').style.width = percentage + '%';
    }
    
    // Timer functions
    function startTimer() {
        timeRemaining = timerDuration;
        timerSeconds.textContent = timeRemaining;
        timerProgress.style.width = '100%';
        timerProgress.classList.remove('warning', 'danger');
        
        timerInterval = setInterval(function() {
            timeRemaining--;
            timerSeconds.textContent = timeRemaining;
            
            // Update progress bar
            const percentage = (timeRemaining / timerDuration) * 100;
            timerProgress.style.width = percentage + '%';
            
            // Add warning classes based on time remaining
            if (timeRemaining <= 5) {
                timerProgress.classList.add('danger');
                timerProgress.classList.remove('warning');
            } else if (timeRemaining <= 10) {
                timerProgress.classList.add('warning');
            }
            
            // Time's up!
            if (timeRemaining <= 0) {
                clearInterval(timerInterval);
                handleTimeUp();
            }
        }, 1000);
    }
    
    // Save result to session via AJAX
    function saveResult(isCorrect) {
        const data = {
            flag_id: flag.flag_id,
            country_name: flag.country_name,
            country_code: flag.country_code,
            is_correct: isCorrect,
            current_question: currentQuestion,
            num_questions: numQuestions,
            mode: mode
        };
        
        fetch("/flagd/save_quiz_result/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        }).catch(error => console.error('Error saving result:', error));
    }
    
    // Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Load next question via AJAX
    function loadNextQuestion() {
        // Build URL for next question
        let nextUrl = `/flagd/play/${mode}/?timer=${timerDuration}&num_questions=${numQuestions}`;
        if (!isLastQuestion) {
            nextUrl += "&current_question=" + (currentQuestion + 1);
        }
        
        // Make AJAX request
        fetch(nextUrl, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.flag) {
                // Update state with new data
                currentQuestion = data.current_question;
                numQuestions = data.num_questions;
                timerDuration = data.timer_duration;
                mode = data.mode;
                modeName = data.mode_name;
                isLastQuestion = data.is_last_question;
                flag = data.flag;
                // Store aliases in lowercase for case-insensitive comparison, and include the country name
                aliases = [...data.aliases, flag.country_name].map(alias => alias.toLowerCase());
                
                // Update UI
                modeTitle.textContent = modeName + ' Mode';
                document.getElementById('current-question-display').textContent = currentQuestion;
                document.getElementById('total-questions-display').textContent = numQuestions;
                updateProgressBar();
                
                // Update flag image
                const flagImg = document.querySelector('.flag-image');
                if (flagImg) {
                    flagImg.src = "https://flagcdn.com/w320/" + flag.country_code + ".png";
                    flagImg.srcset = "https://flagcdn.com/w640/" + flag.country_code + ".png 2x, https://flagcdn.com/w960/" + flag.country_code + ".png 3x";
                    flagImg.alt = "Flag of " + flag.country_name;
                }
                
                // Reset form and result message
                if (guessInput) guessInput.value = '';
                if (guessInput) guessInput.disabled = false;
                if (submitButton) submitButton.disabled = false;
                if (skipButton) skipButton.disabled = false;
                if (resultMessage) resultMessage.innerHTML = '';
                
                // Reset timer
                clearInterval(timerInterval);
                startTimer();
                
                // Reset answered flag
                isAnswered = false;
            } else {
                // No more flags - show results
                showResults();
            }
        })
        .catch(error => {
            console.error('Error loading next question:', error);
            showErrorMessage('Failed to load next question. Please try again.');
        });
    }
    
    // Show results page
    function showResults() {
        const resultsUrl = `/flagd/results/${mode}/?timer=${timerDuration}&num_questions=${numQuestions}`;
        window.location.href = resultsUrl;
    }
    
    // Handle when time runs out
    function handleTimeUp() {
        if (isAnswered) return;
        isAnswered = true;
        
        guessInput.disabled = true;
        submitButton.disabled = true;
        skipButton.disabled = true;
        
        resultMessage.innerHTML = '<p class="text-warning fw-bold">Time\'s up! The answer was: <strong>' + flag.country_name + '</strong></p>';
        
        // Save incorrect result (time's up counts as wrong)
        saveResult(false);
        
        // Navigate to next question or show results
        setTimeout(function() {
            if (isLastQuestion) {
                showResults();
            } else {
                loadNextQuestion();
            }
        }, 3000);
    }
    
    // Handle correct answer
    function handleCorrectAnswer() {
        if (isAnswered) return;
        isAnswered = true;
        
        clearInterval(timerInterval);
        guessInput.disabled = true;
        submitButton.disabled = true;
        skipButton.disabled = true;
        
        resultMessage.innerHTML = '<p class="text-success fw-bold">Correct! Well done!</p>';
        
        // Save correct result
        saveResult(true);
        
        // Navigate to next question or show results
        setTimeout(function() {
            if (isLastQuestion) {
                showResults();
            } else {
                loadNextQuestion();
            }
        }, 1500);
    }
    
    // Handle incorrect answer
    function handleIncorrectAnswer() {
        if (isAnswered) return;
        // Don't set isAnswered here - allow multiple attempts
        resultMessage.innerHTML = '<p class="text-danger fw-bold">Incorrect. Try again!</p>';
    }
    
    // Handle skip button click
    function handleSkip() {
        if (isAnswered) return;
        isAnswered = true;
        
        clearInterval(timerInterval);
        guessInput.disabled = true;
        submitButton.disabled = true;
        skipButton.disabled = true;
        
        resultMessage.innerHTML = '<p class="text-warning fw-bold">Skipped! The answer was: <strong>' + flag.country_name + '</strong></p>';
        
        // Save incorrect result (skipping counts as wrong)
        saveResult(false);
        
        // Navigate to next question or show results
        setTimeout(function() {
            if (isLastQuestion) {
                showResults();
            } else {
                loadNextQuestion();
            }
        }, 2000);
    }
    
    // Handle submit guess
    function handleSubmitGuess() {
        if (isAnswered) return;
        
        const userGuess = guessInput.value.trim().toLowerCase();
        
        // Check if guess matches country name or any alias (case-insensitive)
        if (aliases.includes(userGuess)) {
            handleCorrectAnswer();
        } else {
            handleIncorrectAnswer();
        }
    }
    
    // Show error message
    function showErrorMessage(message) {
        resultMessage.innerHTML = '<p class="text-danger">' + message + '</p>';
    }
});
