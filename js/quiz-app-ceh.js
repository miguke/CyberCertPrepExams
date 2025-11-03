document.addEventListener('DOMContentLoaded', () => {
    // --- Global Variables ---
    let quizQuestions = [];
    let userAnswers = [];
    let currentQ = 0;
    let correctCount = 0;
    let selectedTopics = [];
    let examTimeRemaining = 0;
    let examTimerInterval = null;
    let courseConfig = null;
    let isRealExamMode = false;
    let isReviewMode = false;
    let originalQuestions = [];
    let originalAnswers = [];
    let originalCorrectCount = 0;

    // --- DOM Elements ---
    const startScreen = document.getElementById('startScreen');
    const quizScreen = document.getElementById('quizScreen');
    const resultScreen = document.getElementById('resultScreen');
    const loadingScreen = document.getElementById('loadingScreen');
    const topicList = document.getElementById('topicList');
    const qText = document.getElementById('qText');
    const optionsList = document.getElementById('optionsList');
    const explanationContainer = document.getElementById('explanation');
    const explText = document.getElementById('explText');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const menuBtn = document.getElementById('menuBtn');
    const restartBtn = document.getElementById('restartBtn');
    const backToMenuBtn = document.getElementById('backToMenuBtn');
    const reviewBtn = document.getElementById('reviewBtn');
    const currentQEl = document.getElementById('currentQ');
    const totalQEl = document.getElementById('totalQ');
    const correctCountEl = document.getElementById('correctCount');
    const accuracyEl = document.getElementById('accuracy');
    const progressFill = document.querySelector('.progress-fill');
    const timerDisplay = document.getElementById('timer-display');
    const realExamBtn = document.getElementById('realExamBtn');
    const startQuizBtn = document.getElementById('startBtn');
    const selectAllBtn = document.getElementById('selectAllBtn');

    // --- Helper Functions ---
    const showScreen = (screenId) => {
        [startScreen, quizScreen, resultScreen, loadingScreen].forEach(screen => {
            if (screen) screen.classList.remove('active');
        });
        const screenToShow = document.getElementById(screenId);
        if (screenToShow) screenToShow.classList.add('active');
    };

    const goToMenu = () => {
        stopExamTimer();
        showScreen('startScreen');
        selectedTopics = [];
        // Uncheck all checkboxes
        document.querySelectorAll('#topicList input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
            cb.closest('.topic-item')?.classList.remove('selected');
        });
        updateStartButtons();
    };

    const updateQuizProgress = () => {
        if (!quizQuestions.length) return;
        const total = quizQuestions.length;
        const current = currentQ + 1;
        const answeredCount = userAnswers.filter(a => a !== null).length;
        
        if (progressFill) progressFill.style.width = `${(current / total) * 100}%`;
        if (currentQEl) currentQEl.textContent = current;
        if (totalQEl) totalQEl.textContent = total;
        if (correctCountEl) correctCountEl.textContent = correctCount;
        if (accuracyEl) {
            const accuracy = answeredCount > 0 ? Math.round((correctCount / answeredCount) * 100) : 0;
            accuracyEl.textContent = `${accuracy}%`;
        }
    };

    const shuffle = (array) => {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const arraysEqual = (a, b) => {
        if (!a || !b || a.length !== b.length) return false;
        const sortedA = [...a].sort((x, y) => x - y);
        const sortedB = [...b].sort((x, y) => x - y);
        return sortedA.every((val, index) => val === sortedB[index]);
    };
    
    const toggleExplanation = (show) => {
        if (explanationContainer) {
            explanationContainer.style.display = show ? 'block' : 'none';
        }
        if (show && quizQuestions[currentQ]) {
            explText.innerHTML = quizQuestions[currentQ].explanation;
        }
    };

    const updateButtonStates = () => {
        const isAnswered = userAnswers[currentQ] !== null;
        if (submitBtn) submitBtn.style.display = isAnswered ? 'none' : 'inline-block';
        if (nextBtn) nextBtn.style.display = isAnswered ? 'inline-block' : 'none';
        if (prevBtn) prevBtn.style.display = isAnswered ? 'inline-block' : 'none';
        
        if (prevBtn) prevBtn.disabled = currentQ === 0;
        if (nextBtn) {
            if (currentQ >= quizQuestions.length - 1) {
                nextBtn.textContent = 'Show Results';
            } else {
                nextBtn.textContent = 'Next';
            }
        }
    };

    // --- Core Quiz Logic ---

    const loadCourseConfig = async () => {
        try {
            const cacheBuster = `?v=${Date.now()}`;
            const module = await import(`./course-ceh-config.js${cacheBuster}`);
            courseConfig = module.default;
            if (!courseConfig) {
                throw new Error('Course configuration not found in module');
            }
            const { updateTopicCounts } = module;
            if (typeof updateTopicCounts === 'function') {
                await updateTopicCounts();
            }
            renderTopics();
            return true;
        } catch (error) {
            console.error('Failed to load course configuration:', error);
            const errorContainer = document.createElement('div');
            errorContainer.className = 'error-container';
            errorContainer.innerHTML = `
                <h1>Error Loading Application</h1>
                <p>Failed to load course configuration. Please check the console for details.</p>
                <p><strong>Error:</strong> ${error.message}</p>
            `;
            document.body.innerHTML = '';
            document.body.prepend(errorContainer);
            return false;
        }
    };

    const loadQuestions = async (isExam) => {
        console.log('[loadQuestions] Called. isExam:', isExam, 'Initial selectedTopics (if not exam):', JSON.parse(JSON.stringify(selectedTopics)));
        showScreen('loadingScreen');
        quizQuestions = [];
        let questionLimits = {};
        const topicsToLoad = isExam ? Object.keys(courseConfig.topics) : selectedTopics;
        console.log('[loadQuestions] Effective topicsToLoad:', JSON.parse(JSON.stringify(topicsToLoad)));

        if (isExam) {
            console.log('[loadQuestions] Exam mode: Calculating weighted question limits.');
            const totalExamQuestions = courseConfig.examQuestionCount || 90;
            let totalWeight = 0;
            topicsToLoad.forEach(topic => {
                totalWeight += courseConfig.topics[topic]?.weight || 0;
            });
            console.log('[loadQuestions] Total weight for exam topics:', totalWeight);

            if (totalWeight > 0) {
                let assignedQuestions = 0;
                topicsToLoad.forEach(topic => {
                    const weight = courseConfig.topics[topic]?.weight || 0;
                    const num = Math.round((weight / totalWeight) * totalExamQuestions);
                    questionLimits[topic] = num;
                    assignedQuestions += num;
                });
                console.log('[loadQuestions] Initial question limits:', JSON.parse(JSON.stringify(questionLimits)), 'Assigned:', assignedQuestions, 'Target:', totalExamQuestions);
                
                let diff = totalExamQuestions - assignedQuestions;
                let topicIndex = 0;
                let iterations = 0;
                while (diff !== 0 && iterations < topicsToLoad.length * 5) {
                    const topic = topicsToLoad[topicIndex % topicsToLoad.length];
                    if (diff > 0) {
                        questionLimits[topic]++;
                        diff--;
                    } else {
                        if(questionLimits[topic] > 0) {
                           questionLimits[topic]--;
                           diff++;
                        }
                    }
                    topicIndex++;
                    iterations++;
                }
                console.log('[loadQuestions] Final question limits for exam:', JSON.parse(JSON.stringify(questionLimits)));
            }
        }

        console.log('[loadQuestions] Starting to fetch questions for topics:', JSON.parse(JSON.stringify(topicsToLoad)));
        for (const topic of topicsToLoad) {
            const topicConfig = courseConfig.topics[topic];
            if (!topicConfig || !topicConfig.file) {
                console.warn(`[loadQuestions] Missing config or file for topic: ${topic}. Skipping.`);
                continue;
            }

            try {
                console.log(`[loadQuestions] Fetching questions for topic: ${topic} from ${topicConfig.file}`);
                const response = await fetch(`${topicConfig.file}?v=${Date.now()}`);
                if (!response.ok) {
                    console.error(`[loadQuestions] HTTP error for ${topic}! status: ${response.status}, ${response.statusText}`);
                    throw new Error(`HTTP error! status: ${response.status} for ${topicConfig.file}`);
                }
                let topicQuestions = await response.json();
                console.log(`[loadQuestions] Fetched ${topicQuestions.length} questions for ${topic}`);
                
                topicQuestions = topicQuestions.map(q => ({ ...q, topic }));

                const limit = questionLimits[topic];
                if (isExam && limit !== undefined && topicQuestions.length > limit) { 
                    console.log(`[loadQuestions] Limiting ${topic} from ${topicQuestions.length} to ${limit} questions for exam mode.`);
                    topicQuestions = shuffle([...topicQuestions]).slice(0, limit);
                }
                quizQuestions.push(...topicQuestions);
                console.log(`[loadQuestions] Current total quizQuestions: ${quizQuestions.length} after adding from ${topic}`);
            } catch (error) {
                console.error(`[loadQuestions] Error processing topic ${topic}:`, error.message, error.stack ? error.stack : '');
            }
        }
        console.log(`[loadQuestions] Finished fetching. Total quizQuestions loaded: ${quizQuestions.length}`);

        if (quizQuestions.length === 0) {
            console.warn('[loadQuestions] No questions loaded. Selected topics might be empty, files failed to load, or all selected topics had errors.');
            alert('Failed to load questions for the selected topics. Please check the browser console (F12) for more details.');
            showScreen('startScreen');
            return false;
        }

        quizQuestions = shuffle(quizQuestions);
        userAnswers = new Array(quizQuestions.length).fill(null);
        console.log(`[loadQuestions] Successfully loaded and shuffled ${quizQuestions.length} questions.`);
        return true;
    };

    const startQuiz = async (isExam) => {
        console.log('[startQuiz] Called. isExam:', isExam, 'Selected Topics:', JSON.parse(JSON.stringify(selectedTopics)));
        if (!isExam && selectedTopics.length === 0) {
            alert('Please select at least one topic to begin.');
            console.log('[startQuiz] No topics selected for non-exam mode. Aborting.');
            return;
        }
        isRealExamMode = isExam;
        console.log('[startQuiz] Loading questions...');
        const success = await loadQuestions(isExam);
        console.log('[startQuiz] loadQuestions success:', success);
        if (!success) {
            console.log('[startQuiz] loadQuestions failed. Aborting quiz start.');
            return;
        }

        currentQ = 0;
        correctCount = 0;
        
        if (isExam) {
            console.log('[startQuiz] Starting exam timer.');
            startExamTimer();
        } else {
            console.log('[startQuiz] Stopping exam timer (if any).');
            stopExamTimer();
            if (timerDisplay) timerDisplay.textContent = '';
        }

        console.log('[startQuiz] Showing quiz screen and loading first question.');
        showScreen('quizScreen');
        loadQ();
    };

    const loadQ = () => {
        if (currentQ < 0 || currentQ >= quizQuestions.length) return;

        const q = quizQuestions[currentQ];
        if (!qText || !optionsList) {
            console.error("Quiz elements not found!");
            return;
        }
        qText.innerHTML = q.question;
        optionsList.innerHTML = '';

        q.options.forEach((option, index) => {
            const li = document.createElement('li');
            const inputType = q.correct.length > 1 ? 'checkbox' : 'radio';
            li.dataset.index = index;
            li.innerHTML = `<input type="${inputType}" name="option" value="${index}" id="opt${index}"> <label for="opt${index}">${option}</label>`;
            optionsList.appendChild(li);
        });
        
        const isAnswered = userAnswers[currentQ] !== null;
        if (isAnswered) {
            showFeedback();
        } else {
            toggleExplanation(false);
        }
        updateButtonStates();
        updateQuizProgress();
    };

    const showFeedback = () => {
        const q = quizQuestions[currentQ];
        const userAnswer = userAnswers[currentQ];
        const options = optionsList.querySelectorAll('li');

        // Debug current mapping and selections
        try {
            console.debug('[showFeedback]', { qId: q?.id, correct: q?.correct, userAnswer });
        } catch (e) { /* no-op */ }

        options.forEach((li) => {
            const input = li.querySelector('input');
            if (!input) return;
            input.disabled = true;

            // Always compute using the input's value to avoid any DOM index mismatch
            const valueIndex = parseInt(input.value, 10);

            // Reset any prior classes defensively
            li.classList.remove('correct', 'incorrect');

            const isCorrect = Array.isArray(q.correct) && q.correct.includes(valueIndex);
            const isSelected = Array.isArray(userAnswer) ? userAnswer.includes(valueIndex) : false;

            if (isCorrect) {
                li.classList.add('correct');
            } else if (isSelected) {
                li.classList.add('incorrect');
            }

            if (isSelected) {
                input.checked = true;
            }
        });

        toggleExplanation(true);
    };

    const submitA = () => {
        const selectedOptions = Array.from(optionsList.querySelectorAll('input:checked')).map(el => parseInt(el.value));
        if (selectedOptions.length === 0) {
            alert('Please select an answer.');
            return;
        }

        const wasAnswered = userAnswers[currentQ] !== null;
        userAnswers[currentQ] = selectedOptions;
        const q = quizQuestions[currentQ];
        const isCorrect = arraysEqual(selectedOptions, q.correct);

        if (!wasAnswered) {
            if (isCorrect) {
                correctCount++;
            }
        }
        
        showFeedback();
        updateButtonStates();
        updateQuizProgress();
    };
    
    const nextQ = () => {
        if (currentQ < quizQuestions.length - 1) {
            currentQ++;
            loadQ();
        } else {
            if (isReviewMode) {
                restoreOriginalQuiz();
                showResults(false);
            } else {
                showResults(true);
            }
        }
    };

    const prevQ = () => {
        if (currentQ > 0) {
            currentQ--;
            loadQ();
        }
    };

    const restoreOriginalQuiz = () => {
        if (isReviewMode) {
            quizQuestions = originalQuestions;
            userAnswers = originalAnswers;
            correctCount = originalCorrectCount;
            isReviewMode = false;
        }
    };

    const showResults = (recalculate = true) => {
        console.log('[showResults] Function called - displaying results screen');
        stopExamTimer();
        const answeredCount = userAnswers.filter(a => a !== null).length;
        const totalQuestions = quizQuestions.length;
        const accuracy = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;

        if (recalculate) {
            originalQuestions = [...quizQuestions];
            originalAnswers = [...userAnswers];
            originalCorrectCount = correctCount;
        }

        // Get the actual DOM elements that match the 1102 structure
        const scoreEl = document.getElementById('score');
        const correctAnswersEl = document.getElementById('correctAnswers');
        const totalQuestionsEl = document.getElementById('totalQuestions');
        const percentageEl = document.getElementById('percentage');
        const passFail = document.getElementById('passFail');
        const topicBreakdown = document.getElementById('topicBreakdown');
        const scoreProgress = document.getElementById('scoreProgress');
        
        if (!scoreEl || !correctAnswersEl || !totalQuestionsEl || !percentageEl || !passFail || !topicBreakdown) {
            console.error('Results screen elements not found!');
            console.log('Available elements:', {
                scoreEl: !!scoreEl,
                correctAnswersEl: !!correctAnswersEl,
                totalQuestionsEl: !!totalQuestionsEl,
                percentageEl: !!percentageEl,
                passFail: !!passFail,
                topicBreakdown: !!topicBreakdown
            });
            return;
        }

        const score = Math.round(100 + (accuracy * (courseConfig.maxScore - 100) / 100));
        const passed = score >= courseConfig.passingScore;

        // Update the score display elements to match 1102 structure
        scoreEl.textContent = score;
        correctAnswersEl.textContent = correctCount;
        totalQuestionsEl.textContent = totalQuestions;
        percentageEl.textContent = accuracy;

        // Update the progress circle using the same logic as 1102
        if (scoreProgress) {
            scoreProgress.style.setProperty('--progress', accuracy);
        }

        // Update pass/fail status with the same classes as 1102
        passFail.textContent = passed ? 'APROVADO' : 'REPROVADO';
        passFail.className = passed ? 'pass-status' : 'fail-status';
        
        // Calculate topic results
        const topicResults = {};
        quizQuestions.forEach((q, i) => {
            if (!topicResults[q.topic]) {
                topicResults[q.topic] = { correct: 0, total: 0 };
            }
            topicResults[q.topic].total++;
            if (arraysEqual(userAnswers[i], q.correct)) {
                topicResults[q.topic].correct++;
            }
        });

        // Build topic breakdown using the same structure as 1102
        topicBreakdown.innerHTML = '<h3>Desempenho por Tópico</h3>';
        const topicTable = document.createElement('table');
        topicTable.className = 'topic-table';
        topicTable.innerHTML = `
            <thead>
                <tr>
                    <th>Tópico</th>
                    <th>Corretas</th>
                    <th>Total</th>
                    <th>Percentual</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;
        
        const tbody = topicTable.querySelector('tbody');
        for (const [topic, results] of Object.entries(topicResults)) {
            const acc = results.total > 0 ? Math.round((results.correct / results.total) * 100) : 0;
            const row = document.createElement('tr');
            row.className = acc >= 70 ? 'topic-mastered' : 'topic-needs-review';
            row.innerHTML = `
                <td>${topic}</td>
                <td>${results.correct}</td>
                <td>${results.total}</td>
                <td>${acc}%</td>
            `;
            tbody.appendChild(row);
        }
        
        topicBreakdown.appendChild(topicTable);
        showScreen('resultScreen');
    };

    const reviewIncorrect = () => {
        if (!isReviewMode) {
            originalQuestions = [...quizQuestions];
            originalAnswers = [...userAnswers];
            originalCorrectCount = correctCount;
        }

        const incorrectQuestions = quizQuestions.filter((q, i) => !arraysEqual(userAnswers[i], q.correct));
        
        if (incorrectQuestions.length === 0) {
            alert("Congratulations, you have no incorrect answers to review!");
            return;
        }

        quizQuestions = incorrectQuestions;
        userAnswers = new Array(quizQuestions.length).fill(null);
        currentQ = 0;
        correctCount = 0;
        isReviewMode = true;

        showScreen('quizScreen');
        loadQ();
    };

    const renderTopics = () => {
        if (!topicList) return;
        topicList.innerHTML = '';
        for (const [topic, config] of Object.entries(courseConfig.topics)) {
            const topicEl = document.createElement('div');
            topicEl.className = 'topic-item';
            topicEl.innerHTML = `
                <input type="checkbox" id="${topic}" name="topic" value="${topic}">
                <label for="${topic}">
                    <span class="topic-title">${topic} <span class="question-count">(${config.count || 0})</span></span>
                    <span class="topic-description">${config.description}</span>
                </label>
            `;
            topicList.appendChild(topicEl);
        }
    };

    const updateStartButtons = () => {
        const anySelected = selectedTopics.length > 0;
        if (startQuizBtn) {
            startQuizBtn.disabled = !anySelected;
            startQuizBtn.title = anySelected ? 'Start the quiz with selected topics' : 'Please select at least one topic';
        }
    };

    const startExamTimer = () => {
        if (!timerDisplay) return;
        stopExamTimer();
        examTimeRemaining = courseConfig.examDuration || 5400;
        if(timerDisplay.parentElement) timerDisplay.parentElement.style.display = 'block';
        timerDisplay.textContent = formatTime(examTimeRemaining);

        examTimerInterval = setInterval(() => {
            examTimeRemaining--;
            timerDisplay.textContent = formatTime(examTimeRemaining);
            if (examTimeRemaining <= 0) {
                stopExamTimer();
                alert('Time is up!');
                showResults(true);
            }
        }, 1000);
    };

    const stopExamTimer = () => {
        clearInterval(examTimerInterval);
        examTimerInterval = null;
        if (timerDisplay && timerDisplay.parentElement) timerDisplay.parentElement.style.display = 'none';
    };

    // --- Event Listeners ---
    if (topicList) {
        topicList.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox') {
                selectedTopics = Array.from(document.querySelectorAll('#topicList input:checked')).map(cb => cb.value);
                document.querySelectorAll('#topicList .topic-item').forEach(item => {
                    const cb = item.querySelector('input');
                    if (cb.checked) {
                        item.classList.add('selected');
                    } else {
                        item.classList.remove('selected');
                    }
                });
                updateStartButtons();
            }
        });
    }

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            const checkboxes = document.querySelectorAll('#topicList input[type="checkbox"]');
            const allSelected = checkboxes.length > 0 && Array.from(checkboxes).every(cb => cb.checked);
            
            checkboxes.forEach(cb => {
                cb.checked = !allSelected;
                cb.dispatchEvent(new Event('change', { bubbles: true })); 
            });
        });
    }

    if (startQuizBtn) {
        startQuizBtn.addEventListener('click', () => startQuiz(false));
    }

    if (realExamBtn) {
        realExamBtn.addEventListener('click', () => startQuiz(true));
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', submitA);
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', nextQ);
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', prevQ);
    }

    if (menuBtn) {
        menuBtn.addEventListener('click', goToMenu);
    }

    if (backToMenuBtn) {
        backToMenuBtn.addEventListener('click', goToMenu);
    }

    if (restartBtn) {
        restartBtn.addEventListener('click', () => {
            if(isReviewMode) {
                restoreOriginalQuiz();
                startQuiz(isRealExamMode);
            } else {
                startQuiz(isRealExamMode);
            }
        });
    }

    if (reviewBtn) {
        reviewBtn.addEventListener('click', reviewIncorrect);
    }

    // --- Initial Load ---
    loadCourseConfig().then(success => {
        if (success) {
            showScreen('startScreen');
            updateStartButtons();
        }
    });
});
