import csv
from pathlib import Path
import json

# --- HTML Template ---
# This is the full HTML structure of your flashcard website.
# The __FLASHCARD_DATA__ placeholder will be replaced with your actual flashcard data.
html_template = """
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Static Flashcards</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }
        /* Custom Scrollbar Styling */
        #sidebar::-webkit-scrollbar, #card-container::-webkit-scrollbar { 
            width: 8px; 
        }
        #sidebar::-webkit-scrollbar-track, #card-container::-webkit-scrollbar-track { 
            background: #1f2937; /* bg-gray-800 */
        }
        #sidebar::-webkit-scrollbar-thumb, #card-container::-webkit-scrollbar-thumb { 
            background: #4b5563; /* bg-gray-600 */
            border-radius: 4px; 
        }
        #sidebar::-webkit-scrollbar-thumb:hover, #card-container::-webkit-scrollbar-thumb:hover { 
            background: #6b7280; /* bg-gray-500 */
        }
        .progress-segment { transition: background-color 0.3s ease-in-out; }
    </style>
</head>
<body class="bg-gray-900 text-gray-200 flex h-full">

    <!-- Sidebar Overlay for Mobile -->
    <div id="sidebar-overlay" class="fixed inset-0 z-20 bg-black bg-opacity-50 hidden lg:hidden"></div>

    <!-- Sidebar -->
    <aside id="sidebar" class="fixed inset-y-0 left-0 z-30 w-64 bg-gray-800 p-4 overflow-y-auto h-full flex flex-col flex-shrink-0 -translate-x-full transition-transform duration-300 ease-in-out lg:translate-x-0">
        <h1 class="text-xl font-bold mb-4 text-white">Decks</h1>
        <div id="sidebar-content" class="flex-grow">
            <!-- Deck/Tag filters will be populated here -->
        </div>
        <div class="space-y-2 pt-2 border-t border-gray-700">
            <button id="start-quiz-btn" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-4 rounded-lg transition-colors">
                Quiz Mode
            </button>
        </div>
    </aside>

    <!-- Main Content -->
    <main class="w-full flex-grow flex flex-col items-center justify-center p-4 sm:p-6 lg:ml-64">
        <!-- Hamburger Menu Button -->
        <button id="hamburger-btn" class="lg:hidden fixed top-4 left-4 z-10 p-2 rounded-md bg-gray-700 text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </button>

        <div class="w-full max-w-3xl">
            <!-- Header: Progress and Tag -->
            <div class="flex justify-between items-center mb-4 px-2">
                <div id="tag-display" class="bg-gray-700 text-blue-300 text-sm font-semibold px-3 py-1 rounded-full truncate"></div>
                <div class="flex items-center space-x-4">
                    <button id="toggle-answer-view-btn" class="hidden text-sm bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded-md transition-colors">Hide Answers</button>
                    <div id="progress-display" class="text-gray-400 font-medium"></div>
                </div>
            </div>

            <!-- Flashcard Area -->
            <div id="card-container" class="hidden bg-gray-800 rounded-xl shadow-2xl p-6 sm:p-8 flex flex-col justify-center items-start text-left w-full h-[65vh] max-h-[500px] overflow-y-auto">
                <div id="question-text-area" class="text-lg sm:text-xl md:text-2xl leading-relaxed w-full"></div>
                <p id="answer-area" class="hidden text-xl sm:text-2xl md:text-3xl font-bold text-green-400 mt-4"></p>
                <div id="quiz-options-area" class="hidden w-full mt-6 space-y-3"></div>
            </div>
            
            <!-- Controls -->
            <div id="normal-controls" class="hidden mt-6 justify-center items-center space-x-4">
                <button id="prev-btn" class="bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-colors">Previous</button>
                <button id="show-answer-btn" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">Show</button>
                <button id="next-btn" class="bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-colors">Next</button>
            </div>

            <div id="quiz-controls" class="hidden mt-6 flex justify-center items-center">
                 <button id="quiz-next-btn" class="invisible bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-colors">Next Question</button>
            </div>
        </div>
    </main>
    
    <!-- Modal -->
    <div id="modal" class="hidden fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-40">
        <div class="bg-gray-800 rounded-lg p-6 sm:p-8 max-w-lg w-full">
            <h2 id="modal-title" class="text-2xl font-bold mb-2 text-white">Quiz Settings</h2>

            <div class="my-4">
                <label class="text-sm font-medium text-gray-400">Card Order</label>
                <div id="order-selector" class="mt-2 flex rounded-md bg-gray-700 p-1">
                    <button data-order="random" class="order-selector-btn flex-1 p-2 text-sm rounded-md transition-colors bg-indigo-600">Random</button>
                    <button data-order="sequence" class="order-selector-btn flex-1 p-2 text-sm rounded-md transition-colors bg-transparent">Sequence</button>
                </div>
            </div>
            
            <div class="flex justify-between items-center mb-2">
                 <label class="text-sm font-medium text-gray-400">Select Weeks</label>
                 <button id="select-all" class="text-sm text-indigo-400 hover:text-indigo-300">Select All</button>
            </div>
            <div id="week-selection" class="grid grid-cols-4 sm:grid-cols-6 gap-2 mb-6">
                <!-- Grid items for weeks will be populated here -->
            </div>
            <div class="flex justify-end space-x-4">
                <button id="cancel-btn" class="bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg">Cancel</button>
                <button id="begin-btn" class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-4 rounded-lg">Begin Quiz</button>
            </div>
        </div>
    </div>

    <script>
        const flashcardData = __FLASHCARD_DATA__;
        
        let groupedByTag = {};
        
        // --- State ---
        let currentMode = 'deck'; // deck, quiz
        let sessionQueue = [];
        let currentDeck = [];
        let currentDeckIndex = 0;
        let isAnswersHidden = false;

        // --- DOM Elements ---
        const sidebar = document.getElementById('sidebar');
        const sidebarContent = document.getElementById('sidebar-content');
        const sidebarOverlay = document.getElementById('sidebar-overlay');
        const hamburgerBtn = document.getElementById('hamburger-btn');
        const questionTextArea = document.getElementById('question-text-area');
        const answerArea = document.getElementById('answer-area');
        const quizOptionsArea = document.getElementById('quiz-options-area');
        const tagDisplay = document.getElementById('tag-display');
        const progressDisplay = document.getElementById('progress-display');
        const cardContainer = document.getElementById('card-container');
        
        const normalControls = document.getElementById('normal-controls');
        const showAnswerBtn = document.getElementById('show-answer-btn');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const toggleAnswerBtn = document.getElementById('toggle-answer-view-btn');

        const quizControls = document.getElementById('quiz-controls');
        const quizNextBtn = document.getElementById('quiz-next-btn');
        
        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modal-title');
        const startQuizBtn = document.getElementById('start-quiz-btn');
        const cancelBtn = document.getElementById('cancel-btn');
        const beginBtn = document.getElementById('begin-btn');
        const weekSelection = document.getElementById('week-selection');
        const selectAllBtn = document.getElementById('select-all');
        const orderSelector = document.getElementById('order-selector');

        // --- Initialization ---
        function initialize() {
            groupCardsByTag();
            renderSidebar();
            renderModalOptions();
            startDeckView('All');
            setupEventListeners();
        }
        
        function toggleSidebar() {
            sidebar.classList.toggle('-translate-x-full');
            sidebarOverlay.classList.toggle('hidden');
        }

        function groupCardsByTag() {
            flashcardData.forEach((card, index) => {
                if (!groupedByTag[card.t]) groupedByTag[card.t] = [];
                const newCard = { ...card, originalIndex: index };
                
                // Pre-parse options for quiz mode
                const parts = card.q.split('<br><br>');
                if (parts.length > 1) {
                    newCard.questionText = parts[0];
                    newCard.options = parts[1].split('<br>').map(opt => opt.replace(/^[a-d]\)\\s*/, '').trim());
                } else {
                    newCard.questionText = card.q;
                    newCard.options = [];
                }
                groupedByTag[card.t].push(newCard);
            });
            flashcardData.forEach(card => {
                 const parts = card.q.split('<br><br>');
                if (parts.length > 1) {
                    card.questionText = parts[0];
                    card.options = parts[1].split('<br>').map(opt => opt.replace(/^[a-d]\)\\s*/, '').trim());
                } else {
                    card.questionText = card.q;
                    card.options = [];
                }
            });
        }

        function renderSidebar() {
            sidebarContent.innerHTML = '';
            const tags = ['All', ...Object.keys(groupedByTag).sort()];
            tags.forEach(tag => {
                const button = document.createElement('button');
                button.className = 'text-left text-lg p-2 rounded-md text-gray-400 hover:bg-gray-700 hover:text-white w-full transition-colors';
                button.textContent = tag.replace(/_/g, ' ');
                button.dataset.tag = tag;
                button.addEventListener('click', () => {
                    exitSession();
                    startDeckView(tag);
                    if (window.innerWidth < 1024) { toggleSidebar(); }
                });
                sidebarContent.appendChild(button);
            });
        }
        
        function renderModalOptions() {
             weekSelection.innerHTML = '';
             Object.keys(groupedByTag).sort().forEach(tag => {
                const button = document.createElement('button');
                button.dataset.tag = tag;
                button.className = 'week-selector-btn p-3 rounded-lg bg-gray-700 text-white font-semibold transition-colors data-[selected=true]:bg-indigo-600';
                button.textContent = tag.replace('week', '');
                button.dataset.selected = 'false';
                button.addEventListener('click', () => {
                    button.dataset.selected = button.dataset.selected === 'true' ? 'false' : 'true';
                });
                weekSelection.appendChild(button);
             });
        }

        function setupEventListeners() {
            hamburgerBtn.addEventListener('click', toggleSidebar);
            sidebarOverlay.addEventListener('click', toggleSidebar);

            showAnswerBtn.addEventListener('click', showAnswer);
            prevBtn.addEventListener('click', showPrevDeckCard);
            nextBtn.addEventListener('click', showNextDeckCard);
            toggleAnswerBtn.addEventListener('click', toggleHideAnswers);

            startQuizBtn.addEventListener('click', openQuizModal);
            cancelBtn.addEventListener('click', () => modal.classList.add('hidden'));
            
            selectAllBtn.addEventListener('click', () => {
                const buttons = weekSelection.querySelectorAll('.week-selector-btn');
                const shouldSelectAll = Array.from(buttons).some(b => b.dataset.selected === 'false');
                buttons.forEach(b => b.dataset.selected = shouldSelectAll);
            });

            orderSelector.addEventListener('click', (e) => {
                const targetButton = e.target.closest('.order-selector-btn');
                if (targetButton) {
                    orderSelector.querySelectorAll('.order-selector-btn').forEach(btn => {
                        btn.classList.remove('bg-indigo-600');
                        btn.classList.add('bg-transparent');
                    });
                    targetButton.classList.add('bg-indigo-600');
                    targetButton.classList.remove('bg-transparent');
                }
            });

            beginBtn.addEventListener('click', startSession);
            quizNextBtn.addEventListener('click', showNextQuizCard);

            document.addEventListener('keydown', (e) => {
                if (currentMode !== 'deck') return;
                if (e.key === 'ArrowRight') showNextDeckCard();
                else if (e.key === 'ArrowLeft') showPrevDeckCard();
            });
        }

        function openQuizModal() {
            currentMode = 'quiz';
            modal.classList.remove('hidden');
        }

        function startDeckView(tag) {
            currentDeck = (tag === 'All') ? flashcardData : groupedByTag[tag];
            currentDeckIndex = 0;
            isAnswersHidden = false; // Default to showing answers
            
            cardContainer.classList.remove('hidden');
            cardContainer.classList.add('flex');
            normalControls.classList.remove('hidden');
            normalControls.classList.add('flex');
            quizOptionsArea.classList.add('hidden');
            toggleAnswerBtn.classList.remove('hidden');

            showDeckCard(currentDeckIndex);
        }
        
        function showDeckCard(index) {
            if (index < 0 || index >= currentDeck.length) return;
            
            const cardData = currentDeck[index];
            questionTextArea.innerHTML = cardData.q;
            questionTextArea.classList.remove('hidden');
            answerArea.innerHTML = cardData.a;
            
            if (isAnswersHidden) {
                // "Hide Answers" is ON: Hide the answer, show the "Show" button
                answerArea.classList.add('hidden');
                showAnswerBtn.classList.remove('hidden');
                toggleAnswerBtn.classList.add('bg-indigo-600'); // Indicate active state
            } else {
                // "Hide Answers" is OFF: Show the answer, hide the "Show" button
                answerArea.classList.remove('hidden');
                showAnswerBtn.classList.add('hidden');
                toggleAnswerBtn.classList.remove('bg-indigo-600'); // Indicate inactive state
            }
            
            tagDisplay.textContent = cardData.t;
            progressDisplay.textContent = `${index + 1} / ${currentDeck.length}`;
            cardContainer.scrollTop = 0; 
        }

        function toggleHideAnswers() {
            isAnswersHidden = !isAnswersHidden;
            showDeckCard(currentDeckIndex);
        }
        
        function showPrevDeckCard() {
            if (currentDeckIndex > 0) {
                currentDeckIndex--;
                showDeckCard(currentDeckIndex);
            }
        }

        function showNextDeckCard() {
            if (currentDeckIndex < currentDeck.length - 1) {
                currentDeckIndex++;
                showDeckCard(currentDeckIndex);
            }
        }

        function showAnswer() {
            answerArea.classList.remove('hidden');
        }
        
        // --- Session Logic (Quiz) ---
        function startSession() {
            const selectedTags = Array.from(weekSelection.querySelectorAll('.week-selector-btn[data-selected="true"]')).map(btn => btn.dataset.tag);
            if (selectedTags.length === 0) return;
            const selectedOrder = orderSelector.querySelector('.order-selector-btn.bg-indigo-600').dataset.order;

            let deck = flashcardData.filter(card => selectedTags.includes(card.t));
            if (selectedOrder === 'random') {
                deck.sort(() => Math.random() - 0.5);
            }
            
            sessionQueue = [...deck];
            
            modal.classList.add('hidden');
            normalControls.classList.add('hidden');
            toggleAnswerBtn.classList.add('hidden');
            cardContainer.classList.remove('hidden');
            cardContainer.classList.add('flex');
            quizControls.classList.remove('hidden');
            quizControls.classList.add('flex');
            showNextQuizCard();
        }
        
        function showNextQuizCard() {
            quizNextBtn.classList.add('invisible');
            if (sessionQueue.length === 0) {
                alert("Congratulations! Quiz complete.");
                exitSession();
                return;
            }
            const cardData = sessionQueue[0];
            questionTextArea.innerHTML = cardData.questionText;
            answerArea.classList.add('hidden');
            quizOptionsArea.classList.remove('hidden');
            quizOptionsArea.innerHTML = '';

            tagDisplay.textContent = cardData.t;
            progressDisplay.textContent = `Remaining: ${sessionQueue.length}`;
            cardContainer.scrollTop = 0;

            if (cardData.options.length > 0) {
                cardData.options.forEach(optionText => {
                    const button = document.createElement('button');
                    button.className = 'w-full text-left p-3 rounded-md bg-gray-700 hover:bg-gray-600 transition-colors';
                    button.textContent = optionText;
                    button.addEventListener('click', () => handleQuizAnswer(button, optionText, cardData), { once: true });
                    quizOptionsArea.appendChild(button);
                });
            } else {
                // Fallback for cards with no options
                const button = document.createElement('button');
                button.className = 'w-full p-3 rounded-md bg-blue-600 hover:bg-blue-500 transition-colors';
                button.textContent = 'Show Answer';
                button.addEventListener('click', () => {
                    answerArea.innerHTML = cardData.a;
                    answerArea.classList.remove('hidden');
                    sessionQueue.push(sessionQueue.shift()); // Re-queue to try again later
                    quizNextBtn.classList.remove('invisible');
                    quizOptionsArea.innerHTML = '';
                }, { once: true });
                 quizOptionsArea.appendChild(button);
            }
        }
        
        function handleQuizAnswer(button, selectedAnswer, cardData) {
            // Normalize both the official answer and the selected answer for comparison
            const normalize = (str) => str.trim().replace(/\\.$/, '').toLowerCase();

            const correctAnswer = normalize(cardData.a);
            const selected = normalize(selectedAnswer);
            const isCorrect = selected === correctAnswer;
            
            Array.from(quizOptionsArea.children).forEach(btn => {
                btn.disabled = true;
                const btnText = normalize(btn.textContent);
                if (btnText === correctAnswer) {
                    btn.classList.remove('bg-gray-700', 'hover:bg-gray-600');
                    btn.classList.add('bg-green-600', 'text-white');
                }
            });

            if (!isCorrect) {
                button.classList.remove('bg-gray-700', 'hover:bg-gray-600');
                button.classList.add('bg-red-600', 'text-white');
                sessionQueue.push(sessionQueue.shift()); // Wrong, move to back
            } else {
                sessionQueue.shift(); // Correct, remove from queue
            }
            
            quizNextBtn.classList.remove('invisible');
        }
        
        function exitSession() {
            if (currentMode === 'deck') return;
            currentMode = 'deck';
            quizControls.classList.add('hidden');
            progressDisplay.textContent = ''; 
            startDeckView('All');
        }

        initialize();
    </script>
</body>
</html>
"""

def generate_website():
    """Reads 'anki_all_weeks.csv' from the same directory and injects its data into the HTML template."""
    
    csv_path = Path("anki_all_weeks.csv")

    if not csv_path.is_file():
        print(f"Error: Required file 'anki_all_weeks.csv' not found in this directory.")
        print("Please make sure the CSV file is present before running this script.")
        return

    flashcards = []
    try:
        with csv_path.open('r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if len(row) == 3:
                    flashcards.append({"q": row[0], "a": row[1], "t": row[2]})
    except Exception as e:
        print(f"Error reading or parsing CSV file: {e}")
        return

    flashcard_json = json.dumps(flashcards, indent=4)
    final_html = html_template.replace('__FLASHCARD_DATA__', flashcard_json)

    output_filename = "index.html"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"\nSuccess! Your flashcard website has been created.")
        print(f"Just open the file '{output_filename}' in your web browser to start studying.")
    except Exception as e:
        print(f"Error writing HTML file: {e}")


if __name__ == "__main__":
    generate_website()

