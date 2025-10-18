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
        #sidebar::-webkit-scrollbar { width: 8px; }
        #sidebar::-webkit-scrollbar-track { background: #1f2937; }
        #sidebar::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 4px; }
        #sidebar::-webkit-scrollbar-thumb:hover { background: #6b7280; }
        .progress-segment { transition: background-color 0.3s ease-in-out; }
    </style>
</head>
<body class="bg-gray-900 text-gray-200 flex h-full">

    <!-- Sidebar -->
    <aside id="sidebar" class="w-64 bg-gray-800 p-4 overflow-y-auto h-full flex flex-col flex-shrink-0">
        <h1 class="text-xl font-bold mb-4 text-white">Decks</h1>
        <div id="sidebar-content" class="flex-grow">
            <!-- Deck/Tag filters will be populated here -->
        </div>
        <button id="start-cram-btn" class="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 px-4 rounded-lg transition-colors">
            Cram Mode
        </button>
    </aside>

    <!-- Main Content -->
    <main class="flex-grow flex flex-col items-center justify-center p-6">
        <div class="w-full max-w-3xl">
            <!-- Cram Progress Bar -->
            <div id="cram-progress-bar" class="hidden w-full h-2.5 rounded-full bg-gray-700 mb-4 flex overflow-hidden">
                <!-- Segments will be added here -->
            </div>

            <!-- Header: Progress and Tag -->
            <div class="flex justify-between items-center mb-4 px-2">
                <div id="tag-display" class="bg-gray-700 text-blue-300 text-sm font-semibold px-3 py-1 rounded-full"></div>
                <div id="progress-display" class="text-gray-400 font-medium"></div>
            </div>

            <!-- Flashcard Area -->
            <div id="card-container" class="hidden bg-gray-800 rounded-xl shadow-2xl p-8 flex flex-col justify-center items-start text-left w-full h-96 min-h-[24rem]">
                <p id="question-area" class="text-xl md:text-2xl leading-relaxed"></p>
                <p id="answer-area" class="hidden text-2xl md:text-3xl font-bold text-green-400 mt-4"></p>
            </div>
            
            <!-- Controls -->
            <div id="normal-controls" class="hidden mt-6 justify-center items-center space-x-4">
                <button id="prev-btn" class="bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-colors">Previous</button>
                <button id="show-answer-btn" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">Show Answer</button>
                <button id="next-btn" class="bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-colors">Next</button>
            </div>
            
            <div id="cram-controls" class="hidden mt-6 flex-col items-center">
                <div class="flex justify-center items-center space-x-4">
                     <button id="cram-show-answer-btn" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">Show Answer</button>
                </div>
                 <div id="cram-feedback" class="hidden mt-4 flex justify-center items-center space-x-2 md:space-x-4">
                    <button data-difficulty="hard" class="cram-feedback-btn bg-red-600 hover:bg-red-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">Hard</button>
                    <button data-difficulty="mid" class="cram-feedback-btn bg-yellow-500 hover:bg-yellow-400 text-white font-bold py-3 px-6 rounded-lg transition-colors">Mid</button>
                    <button data-difficulty="easy" class="cram-feedback-btn bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">Easy</button>
                 </div>
            </div>
        </div>
    </main>

    <!-- Cram Mode Modal -->
    <div id="cram-modal" class="hidden fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4">
        <div class="bg-gray-800 rounded-lg p-8 max-w-lg w-full">
            <div class="flex justify-between items-start">
                <h2 class="text-2xl font-bold mb-2 text-white">Cram Settings</h2>
            </div>

            <div class="my-4">
                <label class="text-sm font-medium text-gray-400">Card Order</label>
                <div id="order-selector" class="mt-2 flex rounded-md bg-gray-700 p-1">
                    <button data-order="random" class="order-selector-btn flex-1 p-2 text-sm rounded-md transition-colors bg-indigo-600">Random</button>
                    <button data-order="sequence" class="order-selector-btn flex-1 p-2 text-sm rounded-md transition-colors bg-transparent">Sequence</button>
                </div>
            </div>
            
            <div class="flex justify-between items-center mb-2">
                 <label class="text-sm font-medium text-gray-400">Select Weeks</label>
                 <button id="cram-select-all" class="text-sm text-indigo-400 hover:text-indigo-300">Select All</button>
            </div>
            <div id="cram-week-selection" class="grid grid-cols-4 sm:grid-cols-6 gap-2 mb-6">
                <!-- Grid items for weeks will be populated here -->
            </div>
            <div class="flex justify-end space-x-4">
                <button id="cancel-cram-btn" class="bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg">Cancel</button>
                <button id="begin-cram-btn" class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-4 rounded-lg">Begin Session</button>
            </div>
        </div>
    </div>

    <script>
        const flashcardData = __FLASHCARD_DATA__;
        
        let groupedByTag = {};
        
        // --- State ---
        let isCramming = false;
        let cramDeck = [];
        let learningQueue = [];
        let currentDeck = [];
        let currentDeckIndex = 0;

        // --- DOM Elements ---
        const sidebarContent = document.getElementById('sidebar-content');
        const questionArea = document.getElementById('question-area');
        const answerArea = document.getElementById('answer-area');
        const tagDisplay = document.getElementById('tag-display');
        const progressDisplay = document.getElementById('progress-display');
        const cardContainer = document.getElementById('card-container');
        
        const normalControls = document.getElementById('normal-controls');
        const showAnswerBtn = document.getElementById('show-answer-btn');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');

        const cramControls = document.getElementById('cram-controls');
        const cramShowAnswerBtn = document.getElementById('cram-show-answer-btn');
        const cramFeedback = document.getElementById('cram-feedback');
        const cramProgressBar = document.getElementById('cram-progress-bar');
        
        const cramModal = document.getElementById('cram-modal');
        const startCramBtn = document.getElementById('start-cram-btn');
        const cancelCramBtn = document.getElementById('cancel-cram-btn');
        const beginCramBtn = document.getElementById('begin-cram-btn');
        const cramWeekSelection = document.getElementById('cram-week-selection');
        const cramSelectAllBtn = document.getElementById('cram-select-all');
        const orderSelector = document.getElementById('order-selector');

        // --- Initialization ---
        function initialize() {
            groupCardsByTag();
            renderSidebar();
            renderCramModalOptions();
            startDeckView('All'); // Start with the "All" deck view
            setupEventListeners();
        }

        function groupCardsByTag() {
            flashcardData.forEach((card, index) => {
                if (!groupedByTag[card.t]) groupedByTag[card.t] = [];
                groupedByTag[card.t].push({ ...card, originalIndex: index });
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
                    exitCramMode();
                    startDeckView(tag);
                });
                sidebarContent.appendChild(button);
            });
        }
        
        function renderCramModalOptions() {
             cramWeekSelection.innerHTML = '';
             Object.keys(groupedByTag).sort().forEach(tag => {
                const button = document.createElement('button');
                button.dataset.tag = tag;
                button.className = 'week-selector-btn p-3 rounded-lg bg-gray-700 text-white font-semibold transition-colors data-[selected=true]:bg-indigo-600';
                button.textContent = tag.replace('week', '');
                button.dataset.selected = 'false';
                button.addEventListener('click', () => {
                    const isSelected = button.dataset.selected === 'true';
                    button.dataset.selected = isSelected ? 'false' : 'true';
                });
                cramWeekSelection.appendChild(button);
             });
        }

        function setupEventListeners() {
            showAnswerBtn.addEventListener('click', showAnswer);
            prevBtn.addEventListener('click', showPrevDeckCard);
            nextBtn.addEventListener('click', showNextDeckCard);

            startCramBtn.addEventListener('click', () => cramModal.classList.remove('hidden'));
            cancelCramBtn.addEventListener('click', () => cramModal.classList.add('hidden'));
            
            cramSelectAllBtn.addEventListener('click', () => {
                const buttons = cramWeekSelection.querySelectorAll('.week-selector-btn');
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

            beginCramBtn.addEventListener('click', startCramSession);
            
            cramShowAnswerBtn.addEventListener('click', showAnswer);
            document.querySelectorAll('.cram-feedback-btn').forEach(btn => {
                btn.addEventListener('click', () => handleCramFeedback(btn.dataset.difficulty));
            });
        }

        function startDeckView(tag) {
            currentDeck = (tag === 'All') ? flashcardData : groupedByTag[tag];
            currentDeckIndex = 0;
            
            cardContainer.classList.remove('hidden');
            cardContainer.classList.add('flex');
            normalControls.classList.remove('hidden');
            normalControls.classList.add('flex');

            showDeckCard(currentDeckIndex);
        }
        
        function showDeckCard(index) {
            if (index < 0 || index >= currentDeck.length) return;
            
            const cardData = currentDeck[index];
            questionArea.innerHTML = cardData.q;
            answerArea.innerHTML = cardData.a;
            answerArea.classList.add('hidden');
            tagDisplay.textContent = cardData.t;
            progressDisplay.textContent = `${index + 1} / ${currentDeck.length}`;
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
            if (isCramming) {
                cramShowAnswerBtn.classList.add('hidden');
                cramFeedback.classList.remove('hidden');
            }
        }
        
        // --- Cram Mode Logic ---
        function startCramSession() {
            const selectedTags = Array.from(cramWeekSelection.querySelectorAll('.week-selector-btn[data-selected="true"]'))
                                      .map(btn => btn.dataset.tag);
            
            if (selectedTags.length === 0) return;
            
            const selectedOrder = orderSelector.querySelector('.order-selector-btn.bg-indigo-600').dataset.order;

            isCramming = true;
            let deck = flashcardData.filter(card => selectedTags.includes(card.t));
            
            if (selectedOrder === 'random') {
                deck.sort(() => Math.random() - 0.5);
            }
            
            cramDeck = deck.map((card, index) => ({ ...card, cramId: index, status: 'unseen' }));
            learningQueue = [...cramDeck];
            
            cramModal.classList.add('hidden');
            normalControls.classList.add('hidden');
            cardContainer.classList.remove('hidden');
            cardContainer.classList.add('flex');
            cramControls.classList.remove('hidden');
            cramControls.classList.add('flex');
            cramProgressBar.classList.remove('hidden');

            renderCramProgressBar();
            showNextCramCard();
        }

        function renderCramProgressBar() {
            cramProgressBar.innerHTML = '';
            cramDeck.forEach(card => {
                const segment = document.createElement('div');
                segment.className = 'progress-segment flex-1 h-full bg-gray-600';
                cramProgressBar.appendChild(segment);
                card.progressSegment = segment;
            });
        }

        function showNextCramCard() {
            if (learningQueue.length === 0) {
                alert("Congratulations! Cram session complete.");
                exitCramMode();
                return;
            }
            const cardData = learningQueue[0];
            questionArea.innerHTML = cardData.q;
            answerArea.innerHTML = cardData.a;
            answerArea.classList.add('hidden');
            tagDisplay.textContent = cardData.t;
            progressDisplay.textContent = `Remaining: ${learningQueue.length}`;
            
            cramShowAnswerBtn.classList.remove('hidden');
            cramFeedback.classList.add('hidden');
        }
        
        function handleCramFeedback(difficulty) {
            const currentCard = learningQueue.shift(); // Take card from the front
            let reinsertIndex;

            switch(difficulty) {
                case 'hard':
                    reinsertIndex = Math.ceil(learningQueue.length * 0.25);
                    learningQueue.splice(reinsertIndex, 0, currentCard);
                    currentCard.status = 'hard';
                    break;
                case 'mid':
                    reinsertIndex = Math.ceil(learningQueue.length * 0.50);
                    learningQueue.splice(reinsertIndex, 0, currentCard);
                    currentCard.status = 'mid';
                    break;
                case 'easy':
                    currentCard.status = 'easy';
                    // Card is not re-inserted, effectively removing it
                    break;
            }
            updateProgressBar(currentCard);
            showNextCramCard();
        }

        function updateProgressBar(card) {
            const colorMap = {
                hard: 'bg-red-500',
                mid: 'bg-yellow-500',
                easy: 'bg-green-500'
            };
            card.progressSegment.className = 'progress-segment flex-1 h-full ' + colorMap[card.status];
        }
        
        function exitCramMode() {
            if (!isCramming) return;
            isCramming = false;
            cramControls.classList.add('hidden');
            cramProgressBar.classList.add('hidden');
            progressDisplay.textContent = ''; // Clear cram progress text
            startDeckView('All'); // Go back to the default "All" deck view
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

