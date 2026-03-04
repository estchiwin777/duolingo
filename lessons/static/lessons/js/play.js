document.addEventListener('DOMContentLoaded', function() {
    const questionsElement = document.getElementById('questions-data');
    if (!questionsElement) return; 
    
    const questions = JSON.parse(questionsElement.textContent);
    let currentIndex = 0;
    let score = 0;

    const jpText = document.getElementById('jp-text');
    const jpReading = document.getElementById('jp-reading');
    const hintBox = document.getElementById('hint-box');   
    const hintText = document.getElementById('hint-text'); 
    
    // UI Elements
    const wordInputContainer = document.getElementById('word-input-container');
    const answerInput = document.getElementById('answer-input');
    const sentenceUiContainer = document.getElementById('sentence-ui-container');
    const selectedWordsZone = document.getElementById('selected-words-zone');
    const wordBankZone = document.getElementById('word-bank-zone');
    
    const btnSpeak = document.getElementById('btn-speak');
    const btnCheck = document.getElementById('btn-check');
    const btnNext = document.getElementById('btn-next');
    const btnOverride = document.getElementById('btn-override'); 
    const feedbackArea = document.getElementById('feedback-area');
    const progressText = document.getElementById('progress-text');
    const quizCard = document.getElementById('quiz-card');
    const resultScreen = document.getElementById('result-screen');
    const finalScore = document.getElementById('final-score');
    
    // 🌟 ส่วนที่เพิ่มมาใหม่: UI สรุปผล
    const resultMessage = document.getElementById('result-message');
    const btnNextLevel = document.getElementById('btn-next-level');
    const btnRetry = document.getElementById('btn-retry');

    function loadQuestion() {
        quizCard.classList.remove('slide-animation'); 
        void quizCard.offsetWidth;                    
        quizCard.classList.add('slide-animation');    

        const currentQ = questions[currentIndex];
        jpText.textContent = currentQ.jp_text;
        
        if (currentQ.type === 'sentence') {
            const romajiMatch = currentQ.jp_reading.match(/\((.*?)\)/);
            if (romajiMatch) {
                jpReading.textContent = `(${romajiMatch[1]})`;
            } else {
                jpReading.textContent = currentQ.jp_reading;
            }
        } else {
            const hiraganaReading = currentQ.jp_reading;
            const romajiReading = wanakana.toRomaji(hiraganaReading);
            jpReading.textContent = `(${romajiReading})`;
        }

        if (currentQ.type === 'sentence') {
            wordInputContainer.classList.add('d-none');
            sentenceUiContainer.classList.remove('d-none');
            setupSentenceUI(currentQ.choices);
        } else {
            sentenceUiContainer.classList.add('d-none');
            wordInputContainer.classList.remove('d-none');
            answerInput.value = '';
            answerInput.disabled = false;
            answerInput.focus(); 
        }
        
        feedbackArea.classList.add('d-none');
        btnCheck.classList.remove('d-none');
        btnNext.classList.add('d-none');
        if (btnOverride) btnOverride.classList.add('d-none'); 
        progressText.textContent = `${currentIndex + 1}/${questions.length}`;
        document.getElementById('progress-bar').style.width = `${((currentIndex) / questions.length) * 100}%`;
    }

    function setupSentenceUI(choices) {
        selectedWordsZone.innerHTML = ''; 
        wordBankZone.innerHTML = '';
        choices.forEach(word => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-outline-secondary btn-lg rounded-pill shadow-sm m-1';
            btn.textContent = word;
            btn.onclick = function() {
                if (btn.parentElement === selectedWordsZone) {
                    wordBankZone.appendChild(btn);
                } else {
                    selectedWordsZone.appendChild(btn);
                }
            };
            wordBankZone.appendChild(btn);
        });
    }

    function playAudio() {
        const currentQ = questions[currentIndex];
        let textToSpeak = currentQ.jp_text; 
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = 'ja-JP'; 
        window.speechSynthesis.speak(utterance);
    }

    function showCorrectFeedback() {
        feedbackArea.classList.remove('alert-danger');
        feedbackArea.classList.add('alert-success');
        feedbackArea.innerHTML = '<strong><i class="fas fa-check-circle"></i> ถูกต้อง!</strong>';
        if (btnOverride) btnOverride.classList.add('d-none');
        score++;
    }

    function getSimilarity(str1, str2) {
        if (str1 === str2) return 1.0;
        const len1 = str1.length, len2 = str2.length;
        const maxLen = Math.max(len1, len2);
        if (maxLen === 0) return 1.0;
        let matrix = [];
        for (let i = 0; i <= len1; i++) matrix[i] = [i];
        for (let j = 0; j <= len2; j++) matrix[0][j] = j;
        for (let i = 1; i <= len1; i++) {
            for (let j = 1; j <= len2; j++) {
                const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
                matrix[i][j] = Math.min(matrix[i - 1][j] + 1, matrix[i][j - 1] + 1, matrix[i - 1][j - 1] + cost);
            }
        }
        return (maxLen - matrix[len1][len2]) / maxLen;
    }

    function checkAnswer() {
        const currentQ = questions[currentIndex];
        const cleanString = (str) => str.toLowerCase().replace(/[\s\.。!?,;\(\)（）]/g, '');
        let userAnswer = '';
        
        if (currentQ.type === 'sentence') {
            const selectedButtons = Array.from(selectedWordsZone.children);
            userAnswer = cleanString(selectedButtons.map(b => b.textContent).join(''));
        } else {
            userAnswer = cleanString(answerInput.value);
            answerInput.disabled = true; 
        }

        const validThAnswers = currentQ.th_meaning.split(',').map(p => cleanString(p));
        const allValidAnswers = [...validThAnswers];

        btnCheck.classList.add('d-none'); 
        btnNext.classList.remove('d-none'); 
        feedbackArea.classList.remove('d-none');

        let isCorrect = allValidAnswers.some(valid => {
            if (valid === userAnswer) return true;
            let similarityScore = getSimilarity(valid, userAnswer);
            if (currentQ.type === 'sentence' && similarityScore >= 0.65) return true;
            if (currentQ.type === 'word' && (valid.includes(userAnswer) && userAnswer.length >= 2 || similarityScore >= 0.80)) return true;
            return false;
        });

        if (isCorrect) {
            showCorrectFeedback();
        } else {
            feedbackArea.classList.add('alert-danger');
            feedbackArea.innerHTML = `<strong><i class="fas fa-times-circle"></i> ผิด!</strong><br>เฉลย: ${currentQ.th_meaning.split(',')[0]}`;
            if (btnOverride) btnOverride.classList.remove('d-none'); 
        }
    }

    function nextQuestion() {
        currentIndex++;
        if (currentIndex < questions.length) {
            loadQuestion(); 
        } else {
            finishGame();
        }
    }

    // 🌟 2. ฟังก์ชันจบเกมตาม User Story
    function finishGame() {
        quizCard.classList.add('d-none');
        document.getElementById('action-buttons-container').classList.add('d-none');
        resultScreen.classList.remove('d-none');
        finalScore.textContent = `${score} / ${questions.length}`;

        const passScore = questions.length / 2;
        if (score >= passScore) {
            resultMessage.textContent = "เก่งมากขุนแผน! ผ่านเกณฑ์แล้ว 🎉";
            resultMessage.className = "text-success h4";
            btnNextLevel.classList.remove('d-none');
            btnRetry.classList.add('d-none');
        } else {
            resultMessage.textContent = "คะแนนไม่ถึงครึ่ง ขุนแผนต้องเล่นใหม่นะ 😅";
            resultMessage.className = "text-danger h4";
            btnRetry.classList.remove('d-none');
            btnNextLevel.classList.add('d-none');
        }
    }

    btnSpeak.addEventListener('click', playAudio);
    btnCheck.addEventListener('click', checkAnswer);
    btnNext.addEventListener('click', nextQuestion);
    if (btnRetry) btnRetry.addEventListener('click', () => location.reload());
    if (btnOverride) btnOverride.addEventListener('click', showCorrectFeedback);

    answerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            if (!btnCheck.classList.contains('d-none')) checkAnswer();
            else if (!btnNext.classList.contains('d-none')) nextQuestion();
        }
    });

    if (questions.length > 0) {
        loadQuestion();
        setTimeout(playAudio, 500);
    }
});