document.addEventListener('DOMContentLoaded', () => {
    // IDs das perguntas que apareceram no exame real (65 questões confirmadas)
    // Excluídos: PBQs/Simulações (3, 84, 103, 140, 193, 526)
    const EXAM_QUESTION_IDS = [
        1, 55, 133, 142, 154, 163, 185, 187, 197, 200, 
        218, 221, 253, 270, 273, 278, 286, 313, 322, 347, 351, 353, 359, 374, 
        376, 385, 400, 418, 422, 432, 440, 447, 472, 493, 496, 499, 504, 517, 
        518, 520, 521, 532, 557, 562, 567, 570, 591, 608, 609, 610, 614, 
        621, 622, 627, 635, 638, 651, 652, 657, 663, 673, 674, 678, 681, 682
    ];

    // --- Global Variables ---
    let quizQuestions = [];
    let userAnswers = [];
    let currentQ = 0;
    let correctCount = 0;
    let examTimeRemaining = 0;
    let examTimerInterval = null;
    let courseConfig = null;
    let isReviewMode = false;
    let originalQuestions = [];
    let originalAnswers = [];
    let originalCorrectCount = 0;

    // --- DOM Elements ---
    const startScreen = document.getElementById('startScreen');
    const quizScreen = document.getElementById('quizScreen');
    const resultScreen = document.getElementById('resultScreen');
    const loadingScreen = document.getElementById('loadingScreen');
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
    const startExamBtn = document.getElementById('startExamBtn');

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
                nextBtn.textContent = 'Mostrar Resultados';
            } else {
                nextBtn.textContent = 'Próxima';
            }
        }
    };

    // --- Core Quiz Logic ---

    const loadCourseConfig = async () => {
        try {
            const cacheBuster = `?v=${Date.now()}`;
            const module = await import(`./course-sy0-701-config.js${cacheBuster}`);
            courseConfig = module.default;
            if (!courseConfig) {
                throw new Error('Course configuration not found in module');
            }
            return true;
        } catch (error) {
            console.error('Failed to load course configuration:', error);
            alert('Erro ao carregar configuração. Verifique o console para detalhes.');
            return false;
        }
    };

    const loadQuestions = async () => {
        console.log('[loadQuestions] Carregando questões do exame real...');
        showScreen('loadingScreen');
        quizQuestions = [];

        const topicsToLoad = Object.keys(courseConfig.topics);
        console.log('[loadQuestions] Tópicos a carregar:', topicsToLoad);

        // Carregar todas as questões de todos os ficheiros (incluindo ficheiro extra)
        const allFiles = [
            ...Object.entries(courseConfig.topics).map(([topic, config]) => ({ topic, file: config.file })),
            { topic: 'exam-real-missing', file: '../data/sy0-701/exam-real-missing-questions.json' }
        ];

        for (const { topic, file } of allFiles) {
            if (!file) {
                console.warn(`[loadQuestions] Ficheiro em falta para: ${topic}`);
                continue;
            }

            try {
                console.log(`[loadQuestions] A buscar questões de: ${topic} de ${file}`);
                const response = await fetch(`${file}?v=${Date.now()}`);
                if (!response.ok) {
                    throw new Error(`Erro HTTP! status: ${response.status} para ${file}`);
                }
                let topicQuestions = await response.json();
                console.log(`[loadQuestions] ${topicQuestions.length} questões carregadas de ${topic}`);
                
                // Adicionar o tópico a cada questão
                topicQuestions = topicQuestions.map(q => ({ ...q, topic }));
                
                // Filtrar apenas as questões com os IDs especificados
                const filteredQuestions = topicQuestions.filter(q => EXAM_QUESTION_IDS.includes(q.id));
                if (filteredQuestions.length > 0) {
                    console.log(`[loadQuestions] ${filteredQuestions.length} questões filtradas de ${topic}`);
                    quizQuestions.push(...filteredQuestions);
                }
            } catch (error) {
                console.error(`[loadQuestions] Erro ao processar ${topic}:`, error.message);
            }
        }

        console.log(`[loadQuestions] Total de questões carregadas: ${quizQuestions.length}`);
        console.log(`[loadQuestions] IDs das questões carregadas:`, quizQuestions.map(q => q.id).sort((a, b) => a - b));

        if (quizQuestions.length === 0) {
            alert('Falha ao carregar questões. Verifique o console (F12) para mais detalhes.');
            showScreen('startScreen');
            return false;
        }

        // Verificar se todas as questões esperadas foram encontradas
        const loadedIds = new Set(quizQuestions.map(q => q.id));
        const missingIds = EXAM_QUESTION_IDS.filter(id => !loadedIds.has(id));
        if (missingIds.length > 0) {
            console.warn(`[loadQuestions] IDs não encontrados:`, missingIds);
            console.warn(`[loadQuestions] ${missingIds.length} questões não foram encontradas nos ficheiros JSON`);
        }

        // Embaralhar as questões
        quizQuestions = shuffle(quizQuestions);
        userAnswers = new Array(quizQuestions.length).fill(null);
        console.log(`[loadQuestions] ${quizQuestions.length} questões carregadas e embaralhadas com sucesso.`);
        return true;
    };

    const startQuiz = async () => {
        console.log('[startQuiz] Iniciando simulação do exame real...');
        const success = await loadQuestions();
        if (!success) {
            console.log('[startQuiz] Falha ao carregar questões.');
            return;
        }

        currentQ = 0;
        correctCount = 0;
        
        console.log('[startQuiz] Iniciando timer do exame.');
        startExamTimer();

        console.log('[startQuiz] Mostrando tela do quiz.');
        showScreen('quizScreen');
        loadQ();
    };

    const loadQ = () => {
        if (currentQ < 0 || currentQ >= quizQuestions.length) return;

        const q = quizQuestions[currentQ];
        if (!qText || !optionsList) {
            console.error("Elementos do quiz não encontrados!");
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

        options.forEach((li) => {
            const input = li.querySelector('input');
            if (!input) return;
            input.disabled = true;

            const valueIndex = parseInt(input.value, 10);
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
            alert('Por favor, selecione uma resposta.');
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
        console.log('[showResults] Mostrando tela de resultados');
        stopExamTimer();
        const totalQuestions = quizQuestions.length;
        const accuracy = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;

        if (recalculate) {
            originalQuestions = [...quizQuestions];
            originalAnswers = [...userAnswers];
            originalCorrectCount = correctCount;
        }

        const scoreEl = document.getElementById('score');
        const correctAnswersEl = document.getElementById('correctAnswers');
        const totalQuestionsEl = document.getElementById('totalQuestions');
        const percentageEl = document.getElementById('percentage');
        const passFail = document.getElementById('passFail');
        const topicBreakdown = document.getElementById('topicBreakdown');
        const scoreProgress = document.getElementById('scoreProgress');
        
        if (!scoreEl || !correctAnswersEl || !totalQuestionsEl || !percentageEl || !passFail || !topicBreakdown) {
            console.error('Elementos da tela de resultados não encontrados!');
            return;
        }

        const score = Math.round(100 + (accuracy * (courseConfig.maxScore - 100) / 100));
        const passed = score >= courseConfig.passingScore;

        scoreEl.textContent = score;
        correctAnswersEl.textContent = correctCount;
        totalQuestionsEl.textContent = totalQuestions;
        percentageEl.textContent = accuracy;

        if (scoreProgress) {
            scoreProgress.style.setProperty('--progress', accuracy);
        }

        passFail.textContent = passed ? 'APROVADO' : 'REPROVADO';
        passFail.className = passed ? 'pass-status' : 'fail-status';
        
        // Calcular resultados por tópico
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

        // Construir tabela de desempenho por tópico
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
            alert("Parabéns! Não tem respostas incorretas para rever!");
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
                alert('Tempo esgotado!');
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
    if (startExamBtn) {
        startExamBtn.addEventListener('click', startQuiz);
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
                startQuiz();
            } else {
                startQuiz();
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
        }
    });
});
