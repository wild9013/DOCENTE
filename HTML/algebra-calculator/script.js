document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('expression-input');
    const evaluateBtn = document.getElementById('evaluate-btn');
    const historyContainer = document.getElementById('history');
    const variablesList = document.getElementById('variables-list');
    const clearVarsBtn = document.getElementById('clear-vars');
    const modeRadBtn = document.getElementById('mode-rad');
    const modeDegBtn = document.getElementById('mode-deg');

    // Initialize math.js parser
    let parser = math.parser();
    let angleMode = 'RAD'; // 'RAD' or 'DEG'

    // Focus input on load
    input.focus();

    // Initialize trigonometry functions
    updateParserFunctions();

    // Event Listeners
    evaluateBtn.addEventListener('click', handleEvaluation);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            handleEvaluation();
        }
    });
    clearVarsBtn.addEventListener('click', clearVariables);

    modeRadBtn.addEventListener('click', () => setAngleMode('RAD'));
    modeDegBtn.addEventListener('click', () => setAngleMode('DEG'));

    function setAngleMode(mode) {
        angleMode = mode;

        // Update UI
        if (mode === 'RAD') {
            modeRadBtn.classList.add('active');
            modeDegBtn.classList.remove('active');
        } else {
            modeDegBtn.classList.add('active');
            modeRadBtn.classList.remove('active');
        }

        // Update Parser Logic
        updateParserFunctions();

        // Re-evaluate if there is input (optional, but good UX)
        // handleEvaluation(); 
    }

    function updateParserFunctions() {
        // Standard trig functions
        const trigFunctions = ['sin', 'cos', 'tan', 'sec', 'cot', 'csc'];
        // Inverse trig functions
        const invTrigFunctions = ['asin', 'acos', 'atan', 'acot', 'acsc', 'asec']; // mathjs uses asin, acos etc.

        if (angleMode === 'DEG') {
            // Override for Degrees
            trigFunctions.forEach(fn => {
                parser.set(fn, (x) => {
                    // Convert degrees to radians before calculation
                    return math[fn](math.unit(x, 'deg').toNumber('rad'));
                });
            });

            invTrigFunctions.forEach(fn => {
                parser.set(fn, (x) => {
                    // Calculate in radians, then convert result to degrees
                    const result = math[fn](x);
                    return math.unit(result, 'rad').toNumber('deg');
                });
            });

            // Special case for atan2 if needed, but let's stick to basic ones first
        } else {
            // Restore for Radians (Native math.js behavior)
            // We can just set them back to the native math functions
            trigFunctions.forEach(fn => {
                parser.set(fn, math[fn]);
            });
            invTrigFunctions.forEach(fn => {
                parser.set(fn, math[fn]);
            });
        }
    }

    function handleEvaluation() {
        const expression = input.value.trim();
        if (!expression) return;

        try {
            const result = parser.evaluate(expression);

            // Check if it was an assignment or just an expression
            // We can infer this by checking if the scope has changed, 
            // but math.js parser keeps state internally.
            // A simple way is to re-render variables every time.

            addToHistory(expression, result);
            updateVariablesUI();

            input.value = '';
            scrollToBottom();
        } catch (error) {
            addToHistory(expression, error.message, true);
            scrollToBottom();
        }
    }

    function addToHistory(expression, result, isError = false) {
        // Remove welcome message if it exists
        const welcome = document.querySelector('.welcome-msg');
        if (welcome) welcome.remove();

        const item = document.createElement('div');
        item.className = 'history-item';

        const exprDiv = document.createElement('div');
        exprDiv.className = 'expression';
        exprDiv.textContent = expression;

        const resultDiv = document.createElement('div');
        resultDiv.className = `result ${isError ? 'error' : ''}`;

        if (isError) {
            resultDiv.textContent = `Error: ${result}`;
        } else {
            // Format result if it's a function or complex object
            resultDiv.textContent = formatResult(result);
        }

        item.appendChild(exprDiv);
        item.appendChild(resultDiv);
        historyContainer.appendChild(item);
    }

    function formatResult(result) {
        if (typeof result === 'function') {
            return 'Function defined';
        }
        if (typeof result === 'object' && result !== null) {
            return math.format(result);
        }
        return result;
    }

    function updateVariablesUI() {
        const variables = parser.getAll();
        variablesList.innerHTML = '';

        const keys = Object.keys(variables);

        if (keys.length === 0) {
            variablesList.innerHTML = '<div class="empty-state">No hay variables definidas</div>';
            return;
        }

        keys.forEach(key => {
            // Skip internal math.js variables if any (usually none with parser.getAll())
            const value = variables[key];

            const div = document.createElement('div');
            div.className = 'variable-item';

            const nameSpan = document.createElement('span');
            nameSpan.className = 'variable-name';
            nameSpan.textContent = key;

            const valueSpan = document.createElement('span');
            valueSpan.className = 'variable-value';
            valueSpan.textContent = formatResult(value);

            div.appendChild(nameSpan);
            div.appendChild(valueSpan);
            variablesList.appendChild(div);
        });
    }

    function clearVariables() {
        parser.clear();
        updateVariablesUI();

        // Add a system message to history
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = '<div class="result" style="text-align: center; color: var(--text-secondary); font-size: 0.9rem;">Variables limpiadas</div>';
        historyContainer.appendChild(item);
        scrollToBottom();
    }

    function scrollToBottom() {
        historyContainer.scrollTop = historyContainer.scrollHeight;
    }
});
