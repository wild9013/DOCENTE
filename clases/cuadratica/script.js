document.addEventListener('DOMContentLoaded', () => {
    const mathField = document.getElementById('math-input');
    const solveBtn = document.getElementById('solve-btn');
    const resultDisplay = document.getElementById('result-display');

    // Initialize Nerdamer
    // nerdamer.set('SOLUTIONS_AS_OBJECT', true); // Optional configuration

    solveBtn.addEventListener('click', () => {
        solveEquation();
    });

    // Optional: Solve on Enter key
    mathField.addEventListener('keydown', (evt) => {
        if (evt.key === 'Enter') {
            solveEquation();
        }
    });

    function solveEquation() {
        const latex = mathField.value;
        if (!latex) return;

        // Convert LaTeX to text for Nerdamer (Nerdamer has some LaTeX support but text is safer)
        // However, Nerdamer's convertFromLaTeX is experimental. 
        // MathLive provides a way to get the text value directly if configured, 
        // but by default .value is LaTeX.
        // We can use MathLive's getValue('ascii-math') or similar, but let's try to parse the LaTeX directly
        // or use nerdamer.convertFromLaTeX if available, or simple replacements.
        
        // Better approach: Use MathLive's compute engine or just simple text conversion if possible.
        // For this demo, we'll try to use nerdamer's solve.
        
        try {
            // Get the expression in a format Nerdamer understands better (e.g., text)
            // mathField.expressionMathField.getValue("ascii-math") might be useful but let's stick to standard
            // We will assume the user inputs standard equations.
            
            // Hack: MathLive's .value is LaTeX. 
            // Let's try to use nerdamer directly on the LaTeX string, it has basic support.
            // If that fails, we might need a converter.
            
            // Let's try to get the ASCII value from MathLive which is often easier for parsers
            const ascii = mathField.getValue('ascii-math');
            console.log("Input (ASCII):", ascii);

            // Nerdamer solve
            // Syntax: nerdamer.solve(equation, variable)
            // If no variable is specified, it tries to guess.
            
            let solution;
            try {
                // Try solving
                const result = nerdamer.solve(ascii, 'x'); // Defaulting to solving for x
                solution = result.toString();
            } catch (e) {
                // If it fails, maybe it's not an equation but an expression to simplify
                const result = nerdamer(ascii);
                solution = result.toString();
            }

            // Display result
            // Convert the result back to LaTeX for pretty printing
            const solutionLatex = nerdamer(solution).toTeX();
            
            resultDisplay.innerHTML = `$$${solutionLatex}$$`;
            resultDisplay.classList.add('has-result');
            
            // Re-render MathJax/MathLive if needed, but MathLive can render static latex too
            // Or we can just put it in a math-field read-only
            // Let's use MathLive's static rendering or just insert a math-field
            
            resultDisplay.innerHTML = '';
            const resultField = new MathfieldElement();
            resultField.value = solutionLatex;
            resultField.readOnly = true;
            resultField.style.border = 'none';
            resultField.style.background = 'transparent';
            resultField.style.fontSize = '1.5rem';
            resultDisplay.appendChild(resultField);

        } catch (error) {
            console.error(error);
            resultDisplay.innerHTML = `<span style="color: #ef4444">Error: No se pudo resolver. Intenta simplificar la entrada.</span>`;
        }
    }
});
