// Game State
let currentQuestionIndex = 0;
let team1Score = 0;
let team2Score = 0;
let currentPot = 0;
let strikes = 0;

// DOM Elements
const questionText = document.getElementById('question-text');
const answersBoard = document.getElementById('answers-board');
const scoreTeam1Display = document.getElementById('score-team1');
const scoreTeam2Display = document.getElementById('score-team2');
const currentPotDisplay = document.getElementById('current-pot');
const strikesOverlay = document.getElementById('strikes-overlay');

// Audio (Optional - placeholders)
// const correctSound = new Audio('correct.mp3');
// const wrongSound = new Audio('wrong.mp3');

function initGame() {
    currentQuestionIndex = 0;
    team1Score = 0;
    team2Score = 0;
    updateScores();
    loadQuestion(currentQuestionIndex);
}

function loadQuestion(index) {
    if (index >= gameData.length) {
        questionText.textContent = "¡JUEGO TERMINADO!";
        answersBoard.innerHTML = '';
        return;
    }

    const data = gameData[index];
    questionText.textContent = data.question.toUpperCase();

    // Clear board
    answersBoard.innerHTML = '';
    currentPot = 0;
    updateScores();

    // Create cards
    // We always want 8 cards for the visual look, even if fewer answers
    const totalSlots = 8;

    for (let i = 0; i < totalSlots; i++) {
        const answer = data.answers[i];
        const card = document.createElement('div');
        card.className = 'answer-card';

        if (answer) {
            card.innerHTML = `
                <div class="card-inner">
                    <div class="card-front">
                        <span class="number">${i + 1}</span>
                    </div>
                    <div class="card-back">
                        <span class="answer-text">${answer.text}</span>
                        <span class="answer-points">${answer.points}</span>
                    </div>
                </div>
            `;

            // Click event to reveal
            card.addEventListener('click', () => {
                if (!card.classList.contains('revealed')) {
                    card.classList.add('revealed');
                    addToPot(answer.points);
                    // if (correctSound) correctSound.play();
                }
            });
        } else {
            // Empty card (placeholder)
            card.innerHTML = `
                <div class="card-inner" style="cursor: default;">
                    <div class="card-front" style="background: #002b55; border-color: #004080;">
                        <span class="number" style="opacity: 0.1;">${i + 1}</span>
                    </div>
                    <div class="card-back"></div>
                </div>
            `;
        }

        answersBoard.appendChild(card);
    }
}

function addToPot(points) {
    currentPot += points;
    updateScores();
}

function updateScores() {
    scoreTeam1Display.textContent = team1Score;
    scoreTeam2Display.textContent = team2Score;
    currentPotDisplay.textContent = currentPot;
}

function showStrike() {
    strikesOverlay.classList.add('active');
    // if (wrongSound) wrongSound.play();
    setTimeout(() => {
        strikesOverlay.classList.remove('active');
    }, 1000);
}

// Event Listeners
document.getElementById('btn-wrong').addEventListener('click', showStrike);

document.getElementById('btn-next').addEventListener('click', () => {
    currentQuestionIndex++;
    loadQuestion(currentQuestionIndex);
});

document.getElementById('btn-team1-add').addEventListener('click', () => {
    team1Score += currentPot;
    currentPot = 0;
    updateScores();
});

document.getElementById('btn-team2-add').addEventListener('click', () => {
    team2Score += currentPot;
    currentPot = 0;
    updateScores();
});

// Start Game
initGame();
