// UPSC AI Platform - Main JavaScript File
// Handles all interactive components across the platform

// Global State Management
let currentTest = {
    questions: [],
    currentQuestionIndex: 0,
    answers: {},
    timeRemaining: 0,
    isActive: false,
    selectedSubjects: []
};

let userProgress = {
    testsTaken: 24,
    averageScore: 73,
    hoursStudied: 156,
    currentStreak: 15,
    subjectAccuracy: {
        history: 85,
        geography: 78,
        polity: 72,
        economy: 65,
        environment: 70,
        science: 82,
        'current-affairs': 75
    }
};

// Mock Question Database
const questionBank = {
    history: [
        {
            question: "Which of the following statements about the Indian National Movement is correct?",
            options: [
                "The Quit India Movement was launched in 1940",
                "The Non-Cooperation Movement was suspended after the Chauri Chaura incident",
                "The Simon Commission was welcomed by all Indian leaders",
                "The Rowlatt Act was passed during the tenure of Lord Mountbatten"
            ],
            correct: 1,
            explanation: "The Non-Cooperation Movement was indeed suspended after the Chauri Chaura incident in 1922."
        },
        {
            question: "The Swadeshi Movement was primarily related to:",
            options: [
                "Opposition to British education policy",
                "Boycott of foreign goods",
                "Demand for political rights",
                "Opposition to partition of Bengal"
            ],
            correct: 3,
            explanation: "The Swadeshi Movement was launched in response to the partition of Bengal in 1905."
        }
    ],
    geography: [
        {
            question: "Which of the following is the correct sequence of rivers from north to south?",
            options: [
                "Satluj, Yamuna, Narmada, Godavari",
                "Yamuna, Satluj, Godavari, Narmada",
                "Satluj, Yamuna, Godavari, Narmada",
                "Yamuna, Narmada, Satluj, Godavari"
            ],
            correct: 0,
            explanation: "The correct north to south sequence is Satluj, Yamuna, Narmada, Godavari."
        }
    ],
    polity: [
        {
            question: "Which Article of the Indian Constitution deals with the appointment of the Prime Minister?",
            options: ["Article 74", "Article 75", "Article 76", "Article 77"],
            correct: 1,
            explanation: "Article 75 deals with the appointment of the Prime Minister by the President."
        }
    ],
    economy: [
        {
            question: "The term 'GDP deflator' refers to:",
            options: [
                "The ratio of nominal GDP to real GDP",
                "The difference between nominal and real GDP",
                "The percentage change in GDP",
                "The inflation rate calculated using GDP"
            ],
            correct: 0,
            explanation: "GDP deflator is the ratio of nominal GDP to real GDP, measuring price level changes."
        }
    ],
    environment: [
        {
            question: "The Montreal Protocol is related to:",
            options: [
                "Climate change",
                "Ozone depletion",
                "Biodiversity conservation",
                "Desertification"
            ],
            correct: 1,
            explanation: "The Montreal Protocol (1987) is an international treaty to protect the ozone layer."
        }
    ],
    science: [
        {
            question: "Which of the following is used as a moderator in nuclear reactors?",
            options: ["Uranium", "Graphite", "Plutonium", "Radium"],
            correct: 1,
            explanation: "Graphite is commonly used as a moderator in nuclear reactors to slow down neutrons."
        }
    ],
    'current-affairs': [
        {
            question: "The G20 Summit 2024 was held in:",
            options: ["India", "Brazil", "South Africa", "Indonesia"],
            correct: 1,
            explanation: "The G20 Summit 2024 was held in Brazil."
        }
    ],
    csat: [
        {
            question: "If all roses are flowers and some flowers are red, which conclusion follows?",
            options: [
                "All roses are red",
                "Some roses are red",
                "Some red things are roses",
                "None of the above"
            ],
            correct: 3,
            explanation: "The given statements do not provide enough information to draw any of the specific conclusions."
        }
    ]
};

// Mains Questions Database
const mainsQuestions = {
    gs1: [
        {
            year: "2024",
            question: "Discuss the role of women in the Indian National Movement. (250 words)",
            modelAnswer: "The role of women in the Indian National Movement was significant and multifaceted..."
        },
        {
            year: "2023",
            question: "Examine the impact of globalization on Indian society. (250 words)",
            modelAnswer: "Globalization has profoundly impacted Indian society across multiple dimensions..."
        }
    ],
    gs2: [
        {
            year: "2024",
            question: "Analyze the role of the Supreme Court as the guardian of the Constitution. (250 words)",
            modelAnswer: "The Supreme Court of India serves as the ultimate judicial authority..."
        }
    ],
    gs3: [
        {
            year: "2024",
            question: "Discuss the challenges and opportunities in India's digital economy. (250 words)",
            modelAnswer: "India's digital economy presents both significant challenges and opportunities..."
        }
    ],
    gs4: [
        {
            year: "2024",
            question: "What are the ethical implications of artificial intelligence in governance? (250 words)",
            modelAnswer: "Artificial intelligence in governance raises several ethical considerations..."
        }
    ],
    essay: [
        {
            year: "2024",
            question: "India's Role in the 21st Century World Order",
            modelAnswer: "India's emergence as a global power in the 21st century..."
        }
    ]
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize based on current page
    const currentPage = window.location.pathname.split('/').pop();
    
    switch(currentPage) {
        case 'index.html':
        case '':
            initializePrelimsTest();
            break;
        case 'mains-evaluation.html':
            initializeMainsEvaluation();
            break;
        case 'analytics.html':
            initializeAnalytics();
            break;
    }
    
    // Initialize animations
    initializeAnimations();
}

// Prelims Test Functions
function initializePrelimsTest() {
    setupSubjectSelection();
    setupQuestionSlider();
    setupQuestionOptions();
}

function setupSubjectSelection() {
    const subjectCards = document.querySelectorAll('.subject-card');
    subjectCards.forEach(card => {
        card.addEventListener('click', function() {
            this.classList.toggle('selected');
            const subject = this.dataset.subject;
            if (currentTest.selectedSubjects.includes(subject)) {
                currentTest.selectedSubjects = currentTest.selectedSubjects.filter(s => s !== subject);
            } else {
                currentTest.selectedSubjects.push(subject);
            }
        });
    });
}

function setupQuestionSlider() {
    const slider = document.getElementById('question-count');
    const display = document.getElementById('question-count-display');
    
    if (slider && display) {
        slider.addEventListener('input', function() {
            display.textContent = this.value;
        });
    }
}

function setupQuestionOptions() {
    const options = document.querySelectorAll('.question-option');
    options.forEach(option => {
        option.addEventListener('click', function() {
            // Remove previous selections
            options.forEach(opt => opt.classList.remove('selected'));
            // Add selection to clicked option
            this.classList.add('selected');
            
            const questionIndex = currentTest.currentQuestionIndex;
            currentTest.answers[questionIndex] = this.dataset.option;
        });
    });
}

function scrollToTestGenerator() {
    const element = document.getElementById('test-generator');
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

function generateTest() {
    if (currentTest.selectedSubjects.length === 0) {
        alert('Please select at least one subject');
        return;
    }
    
    const questionCount = parseInt(document.getElementById('question-count').value);
    const difficulty = document.getElementById('difficulty').value;
    const timeLimit = parseInt(document.getElementById('time-limit').value);
    
    // Generate test questions
    currentTest.questions = [];
    const questionsPerSubject = Math.ceil(questionCount / currentTest.selectedSubjects.length);
    
    currentTest.selectedSubjects.forEach(subject => {
        const subjectQuestions = questionBank[subject] || [];
        const selectedQuestions = subjectQuestions.slice(0, questionsPerSubject);
        currentTest.questions.push(...selectedQuestions);
    });
    
    // Shuffle questions
    currentTest.questions = shuffleArray(currentTest.questions).slice(0, questionCount);
    
    // Initialize test state
    currentTest.currentQuestionIndex = 0;
    currentTest.answers = {};
    currentTest.timeRemaining = timeLimit * 60; // Convert to seconds
    currentTest.isActive = true;
    
    // Show test interface
    document.getElementById('test-config').classList.add('hidden');
    document.getElementById('test-interface').classList.remove('hidden');
    
    // Update test interface
    updateTestInterface();
    startTimer();
}

function updateTestInterface() {
    const question = currentTest.questions[currentTest.currentQuestionIndex];
    if (!question) return;
    
    // Update question counter
    document.getElementById('current-question').textContent = currentTest.currentQuestionIndex + 1;
    document.getElementById('total-questions').textContent = currentTest.questions.length;
    
    // Update question text
    document.getElementById('question-text').textContent = question.question;
    
    // Update options
    const options = document.querySelectorAll('.question-option');
    options.forEach((option, index) => {
        const optionLetter = String.fromCharCode(65 + index); // A, B, C, D
        option.querySelector('span').textContent = optionLetter + '.';
        option.innerHTML = `<span class="font-semibold mr-3">${optionLetter}.</span>${question.options[index]}`;
        option.dataset.option = index;
        
        // Restore previous answer selection
        if (currentTest.answers[currentTest.currentQuestionIndex] === String(index)) {
            option.classList.add('selected');
        } else {
            option.classList.remove('selected');
        }
    });
    
    // Update progress bar
    const progress = ((currentTest.currentQuestionIndex + 1) / currentTest.questions.length) * 100;
    document.getElementById('test-progress').style.width = progress + '%';
    
    // Update navigation buttons
    document.getElementById('prev-btn').disabled = currentTest.currentQuestionIndex === 0;
    document.getElementById('next-btn').textContent = 
        currentTest.currentQuestionIndex === currentTest.questions.length - 1 ? 'Submit' : 'Next';
}

function startTimer() {
    const timerDisplay = document.getElementById('timer-display');
    const timerCircle = document.getElementById('timer-circle');
    const totalTime = currentTest.timeRemaining;
    
    const timer = setInterval(() => {
        if (!currentTest.isActive) {
            clearInterval(timer);
            return;
        }
        
        const minutes = Math.floor(currentTest.timeRemaining / 60);
        const seconds = currentTest.timeRemaining % 60;
        timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Update progress circle
        const progress = (totalTime - currentTest.timeRemaining) / totalTime;
        const circumference = 2 * Math.PI * 28;
        timerCircle.style.strokeDashoffset = circumference * (1 - progress);
        
        if (currentTest.timeRemaining <= 0) {
            clearInterval(timer);
            submitTest();
        }
        
        currentTest.timeRemaining--;
    }, 1000);
}

function nextQuestion() {
    if (currentTest.currentQuestionIndex < currentTest.questions.length - 1) {
        currentTest.currentQuestionIndex++;
        updateTestInterface();
    } else {
        submitTest();
    }
}

function previousQuestion() {
    if (currentTest.currentQuestionIndex > 0) {
        currentTest.currentQuestionIndex--;
        updateTestInterface();
    }
}

function pauseTest() {
    currentTest.isActive = !currentTest.isActive;
    const button = event.target;
    button.textContent = currentTest.isActive ? 'Pause' : 'Resume';
}

function submitTest() {
    currentTest.isActive = false;
    
    // Calculate results
    let correct = 0;
    let incorrect = 0;
    
    currentTest.questions.forEach((question, index) => {
        const userAnswer = parseInt(currentTest.answers[index]);
        if (userAnswer === question.correct) {
            correct++;
        } else {
            incorrect++;
        }
    });
    
    const score = Math.round((correct / currentTest.questions.length) * 100);
    
    // Update results display
    document.getElementById('correct-answers').textContent = correct;
    document.getElementById('incorrect-answers').textContent = incorrect;
    document.getElementById('final-score').textContent = score + '%';
    
    // Show results
    document.getElementById('test-interface').classList.add('hidden');
    document.getElementById('test-results').classList.remove('hidden');
    
    // Update user progress
    userProgress.testsTaken++;
    userProgress.averageScore = Math.round((userProgress.averageScore + score) / 2);
}

function retakeTest() {
    // Reset test state
    currentTest = {
        questions: [],
        currentQuestionIndex: 0,
        answers: {},
        timeRemaining: 0,
        isActive: false,
        selectedSubjects: []
    };
    
    // Show configuration
    document.getElementById('test-results').classList.add('hidden');
    document.getElementById('test-config').classList.remove('hidden');
    
    // Reset selections
    document.querySelectorAll('.subject-card').forEach(card => {
        card.classList.remove('selected');
    });
}

// Mains Evaluation Functions
function initializeMainsEvaluation() {
    setupMainsQuestionSelection();
    setupTextEditor();
}

function setupMainsQuestionSelection() {
    const subjectSelect = document.getElementById('subject-select');
    const yearSelect = document.getElementById('year-select');
    
    if (subjectSelect && yearSelect) {
        subjectSelect.addEventListener('change', populateMainsQuestions);
        yearSelect.addEventListener('change', populateMainsQuestions);
        
        // Initial population
        populateMainsQuestions();
    }
}

function populateMainsQuestions() {
    const subject = document.getElementById('subject-select').value;
    const year = document.getElementById('year-select').value;
    const questionList = document.getElementById('question-list');
    
    if (!questionList) return;
    
    questionList.innerHTML = '';
    
    if (subject && year) {
        const questions = mainsQuestions[subject] || [];
        const filteredQuestions = questions.filter(q => q.year === year);
        
        filteredQuestions.forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'bg-gray-50 p-4 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors';
            questionDiv.innerHTML = `
                <div class="font-semibold mb-2">Question ${index + 1}</div>
                <div class="text-gray-700">${question.question}</div>
            `;
            questionDiv.addEventListener('click', () => selectMainsQuestion(question));
            questionList.appendChild(questionDiv);
        });
    }
}

function selectMainsQuestion(question) {
    // Show writing interface
    document.getElementById('question-selection').classList.add('hidden');
    document.getElementById('writing-interface').classList.remove('hidden');
    
    // Update question text
    document.getElementById('selected-question').textContent = question.question;
    
    // Store selected question for evaluation
    window.selectedMainsQuestion = question;
}

function setupTextEditor() {
    const editor = document.getElementById('answer-editor');
    if (editor) {
        editor.addEventListener('input', updateWordCount);
        editor.addEventListener('keydown', handleEditorShortcuts);
    }
}

function updateWordCount() {
    const editor = document.getElementById('answer-editor');
    const wordCountDisplay = document.getElementById('word-count');
    
    if (editor && wordCountDisplay) {
        const text = editor.textContent || editor.innerText;
        const words = text.trim().split(/\s+/).filter(word => word.length > 0);
        wordCountDisplay.textContent = `${words.length} words`;
    }
}

function handleEditorShortcuts(event) {
    // Handle keyboard shortcuts for formatting
    if (event.ctrlKey || event.metaKey) {
        switch(event.key) {
            case 'b':
                event.preventDefault();
                formatText('bold');
                break;
            case 'i':
                event.preventDefault();
                formatText('italic');
                break;
            case 'u':
                event.preventDefault();
                formatText('underline');
                break;
        }
    }
}

function formatText(command) {
    document.execCommand(command, false, null);
    document.getElementById('answer-editor').focus();
}

function saveDraft() {
    const editor = document.getElementById('answer-editor');
    const content = editor.innerHTML;
    localStorage.setItem('mains-answer-draft', content);
    
    // Show success message
    showNotification('Draft saved successfully!', 'success');
}

function submitForEvaluation() {
    const editor = document.getElementById('answer-editor');
    const answer = editor.textContent || editor.innerText;
    
    if (answer.trim().length < 50) {
        alert('Please write a more detailed answer (minimum 50 words)');
        return;
    }
    
    // Simulate AI evaluation
    const evaluation = simulateAIEvaluation(answer);
    displayEvaluationResults(evaluation);
}

function simulateAIEvaluation(answer) {
    // Simulate AI evaluation with realistic scores
    const wordCount = answer.trim().split(/\s+/).length;
    const structureScore = Math.min(90, 70 + Math.random() * 20 + (wordCount > 200 ? 10 : 0));
    const contentScore = Math.min(90, 65 + Math.random() * 25);
    const languageScore = Math.min(90, 68 + Math.random() * 22);
    
    const overallScore = Math.round((structureScore + contentScore + languageScore) / 3);
    
    return {
        overall: overallScore,
        structure: Math.round(structureScore),
        content: Math.round(contentScore),
        language: Math.round(languageScore),
        feedback: generateFeedback(overallScore)
    };
}

function generateFeedback(score) {
    if (score >= 80) {
        return {
            strengths: ["Excellent structure and organization", "Good use of examples", "Clear and concise writing"],
            improvements: ["Could include more contemporary examples", "Consider adding data and statistics"],
            recommendations: ["Continue practicing with time limits", "Study recent policy developments"]
        };
    } else if (score >= 70) {
        return {
            strengths: ["Good introduction and conclusion", "Relevant examples provided", "Logical flow maintained"],
            improvements: ["Strengthen content with more facts", "Improve time management", "Add more dimensions"],
            recommendations: ["Practice answer writing daily", "Focus on weak areas", "Read model answers"]
        };
    } else {
        return {
            strengths: ["Basic structure present", "Attempted all aspects"],
            improvements: ["Need more comprehensive content", "Improve writing style", "Add more examples"],
            recommendations: ["Study fundamental concepts", "Practice basic answer structure", "Read toppers' answers"]
        };
    }
}

function displayEvaluationResults(evaluation) {
    // Hide writing interface
    document.getElementById('writing-interface').classList.add('hidden');
    
    // Update scores
    document.getElementById('overall-score').textContent = evaluation.overall;
    document.getElementById('structure-score').textContent = evaluation.structure;
    document.getElementById('content-score').textContent = evaluation.content;
    document.getElementById('language-score').textContent = evaluation.language;
    
    // Update feedback
    updateFeedbackList(evaluation.feedback);
    
    // Show results
    document.getElementById('evaluation-results').classList.remove('hidden');
    
    // Animate score display
    animateScores();
}

function updateFeedbackList(feedback) {
    const feedbackList = document.getElementById('feedback-list');
    if (!feedbackList) return;
    
    feedbackList.innerHTML = `
        <div class="feedback-item p-4 rounded-lg">
            <div class="font-semibold text-green-600 mb-2">✅ Strengths</div>
            <ul class="text-sm text-gray-700 space-y-1">
                ${feedback.strengths.map(item => `<li>• ${item}</li>`).join('')}
            </ul>
        </div>
        <div class="feedback-item p-4 rounded-lg">
            <div class="font-semibold text-orange-600 mb-2">⚠️ Areas for Improvement</div>
            <ul class="text-sm text-gray-700 space-y-1">
                ${feedback.improvements.map(item => `<li>• ${item}</li>`).join('')}
            </ul>
        </div>
        <div class="feedback-item p-4 rounded-lg">
            <div class="font-semibold text-blue-600 mb-2">💡 Recommendations</div>
            <ul class="text-sm text-gray-700 space-y-1">
                ${feedback.recommendations.map(item => `<li>• ${item}</li>`).join('')}
            </ul>
        </div>
    `;
}

function tryAnotherQuestion() {
    // Reset interface
    document.getElementById('evaluation-results').classList.add('hidden');
    document.getElementById('question-selection').classList.remove('hidden');
    
    // Clear editor
    const editor = document.getElementById('answer-editor');
    if (editor) {
        editor.innerHTML = '';
    }
}

// Analytics Functions
function initializeAnalytics() {
    setupCharts();
    setupCalendar();
    animateProgressRings();
}

function setupCharts() {
    // Subject-wise Performance Radar Chart
    const subjectRadarChart = echarts.init(document.getElementById('subject-radar'));
    if (subjectRadarChart) {
        const radarOption = {
            radar: {
                indicator: [
                    { name: 'History', max: 100 },
                    { name: 'Geography', max: 100 },
                    { name: 'Polity', max: 100 },
                    { name: 'Economy', max: 100 },
                    { name: 'Environment', max: 100 },
                    { name: 'Science', max: 100 }
                ],
                radius: 80
            },
            series: [{
                type: 'radar',
                data: [{
                    value: [
                        userProgress.subjectAccuracy.history,
                        userProgress.subjectAccuracy.geography,
                        userProgress.subjectAccuracy.polity,
                        userProgress.subjectAccuracy.economy,
                        userProgress.subjectAccuracy.environment,
                        userProgress.subjectAccuracy.science
                    ],
                    areaStyle: {
                        color: 'rgba(74, 155, 142, 0.3)'
                    },
                    lineStyle: {
                        color: '#4a9b8e'
                    }
                }]
            }]
        };
        subjectRadarChart.setOption(radarOption);
    }
    
    // Monthly Progress Line Chart
    const progressLineChart = echarts.init(document.getElementById('progress-line'));
    if (progressLineChart) {
        const lineOption = {
            xAxis: {
                type: 'category',
                data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            },
            yAxis: {
                type: 'value',
                max: 100
            },
            series: [{
                data: [65, 68, 72, 75, 73, 78],
                type: 'line',
                smooth: true,
                lineStyle: {
                    color: '#d4af37'
                },
                areaStyle: {
                    color: 'rgba(212, 175, 55, 0.3)'
                }
            }]
        };
        progressLineChart.setOption(lineOption);
    }
}

function setupCalendar() {
    const calendarGrid = document.getElementById('calendar-grid');
    if (!calendarGrid) return;
    
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    // Get first day of month and number of days
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    calendarGrid.innerHTML = '';
    
    // Add empty cells for days before month starts
    for (let i = 0; i < firstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day';
        calendarGrid.appendChild(emptyDay);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        dayElement.textContent = day;
        
        // Mark today
        if (day === today.getDate()) {
            dayElement.classList.add('today');
        }
        
        // Add study sessions (mock data)
        if ([2, 5, 8, 12, 15, 18, 22, 25, 28].includes(day)) {
            dayElement.classList.add('has-session');
        }
        
        dayElement.addEventListener('click', () => selectCalendarDay(day));
        calendarGrid.appendChild(dayElement);
    }
}

function selectCalendarDay(day) {
    showNotification(`Study session for November ${day}`, 'info');
}

function animateProgressRings() {
    const rings = document.querySelectorAll('.progress-ring-circle');
    rings.forEach(ring => {
        const circumference = 2 * Math.PI * 40;
        const progress = Math.random() * 100; // Mock progress
        const offset = circumference - (progress / 100) * circumference;
        
        anime({
            targets: ring,
            strokeDashoffset: offset,
            duration: 1500,
            easing: 'easeOutCubic',
            delay: 500
        });
    });
}

function animateScores() {
    const scores = document.querySelectorAll('#overall-score, #structure-score, #content-score, #language-score');
    scores.forEach(score => {
        const finalValue = parseInt(score.textContent);
        anime({
            targets: score,
            innerHTML: [0, finalValue],
            duration: 2000,
            round: 1,
            easing: 'easeOutCubic'
        });
    });
}

// Utility Functions
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    anime({
        targets: notification,
        translateX: [300, 0],
        opacity: [0, 1],
        duration: 300,
        easing: 'easeOutCubic'
    });
    
    // Remove after 3 seconds
    setTimeout(() => {
        anime({
            targets: notification,
            translateX: [0, 300],
            opacity: [1, 0],
            duration: 300,
            easing: 'easeInCubic',
            complete: () => {
                document.body.removeChild(notification);
            }
        });
    }, 3000);
}

function initializeAnimations() {
    // Animate cards on scroll
    const cards = document.querySelectorAll('.card-hover');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                anime({
                    targets: entry.target,
                    translateY: [50, 0],
                    opacity: [0, 1],
                    duration: 600,
                    easing: 'easeOutCubic',
                    delay: Math.random() * 200
                });
            }
        });
    });
    
    cards.forEach(card => observer.observe(card));
}

// Calendar Navigation
function previousMonth() {
    showNotification('Previous month navigation', 'info');
}

function nextMonth() {
    showNotification('Next month navigation', 'info');
}

// Handle responsive behavior
window.addEventListener('resize', function() {
    // Reinitialize charts on resize
    if (window.location.pathname.includes('analytics.html')) {
        setTimeout(setupCharts, 100);
    }
});

// Export functions for global access
window.scrollToTestGenerator = scrollToTestGenerator;
window.generateTest = generateTest;
window.nextQuestion = nextQuestion;
window.previousQuestion = previousQuestion;
window.pauseTest = pauseTest;
window.retakeTest = retakeTest;
window.formatText = formatText;
window.saveDraft = saveDraft;
window.submitForEvaluation = submitForEvaluation;
window.tryAnotherQuestion = tryAnotherQuestion;
window.previousMonth = previousMonth;
window.nextMonth = nextMonth;