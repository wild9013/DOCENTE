const canvas = document.getElementById('triangleCanvas');
const ctx = canvas.getContext('2d');

// State
let state = {
    mode: 'SAS', // SAS, SSS, ASA, AAS
    inputs: {
        a: 150,
        b: 180,
        c: 150,
        A: 60,
        B: 60,
        C: 60
    },
    results: {
        a: 0, b: 0, c: 0,
        A: 0, B: 0, C: 0,
        valid: true
    }
};

// DOM Elements
const ui = {
    rows: {
        a: document.getElementById('row-side-a'),
        b: document.getElementById('row-side-b'),
        c: document.getElementById('row-side-c'),
        A: document.getElementById('row-angle-a'),
        B: document.getElementById('row-angle-b'),
        C: document.getElementById('row-angle-c')
    },
    inputs: {
        a: document.getElementById('input-side-a'),
        b: document.getElementById('input-side-b'),
        c: document.getElementById('input-side-c'),
        A: document.getElementById('input-angle-a'),
        B: document.getElementById('input-angle-b'),
        C: document.getElementById('input-angle-c')
    },
    displays: {
        a: document.getElementById('val-side-a'),
        b: document.getElementById('val-side-b'),
        c: document.getElementById('val-side-c'),
        A: document.getElementById('val-angle-a'),
        B: document.getElementById('val-angle-b'),
        C: document.getElementById('val-angle-c')
    },
    steps: document.getElementById('steps-content')
};

// Configuration for modes: which inputs to show
const modes = {
    SAS: ['a', 'b', 'C'],
    SSS: ['a', 'b', 'c'],
    ASA: ['A', 'c', 'B'],
    AAS: ['A', 'B', 'a'] // Not in HTML buttons yet, but good to have logic
};

// Resize Canvas
function resize() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    draw();
}

window.addEventListener('resize', resize);

// Init
function init() {
    resize();
    addListeners();
    updateUIForMode();
    update();
}

function addListeners() {
    Object.keys(ui.inputs).forEach(key => {
        ui.inputs[key].addEventListener('input', (e) => {
            state.inputs[key] = parseFloat(e.target.value);
            update();
        });
    });

    document.querySelectorAll('.mode-selector button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelector('.mode-selector button.active').classList.remove('active');
            e.target.classList.add('active');
            state.mode = e.target.dataset.mode;
            updateUIForMode();
            update();
        });
    });
}

function updateUIForMode() {
    const activeInputs = modes[state.mode];

    Object.keys(ui.rows).forEach(key => {
        if (activeInputs.includes(key)) {
            ui.rows[key].style.display = 'flex';
        } else {
            ui.rows[key].style.display = 'none';
        }
    });
}

function toRad(deg) { return deg * Math.PI / 180; }
function toDeg(rad) { return rad * 180 / Math.PI; }

function solve() {
    const { a, b, c, A, B, C } = state.inputs;
    let res = { ...state.inputs, valid: true };
    let steps = [];

    try {
        if (state.mode === 'SAS') {
            // Given a, b, C
            // Law of Cosines for c
            // c^2 = a^2 + b^2 - 2ab cos(C)
            const radC = toRad(C);
            const c2 = a * a + b * b - 2 * a * b * Math.cos(radC);
            res.c = Math.sqrt(c2);

            steps.push(`<strong>Paso 1:</strong> Calcular lado c con Ley de Cosenos.<br>c² = ${a}² + ${b}² - 2(${a})(${b})cos(${C}°)<br>c = <strong>${res.c.toFixed(2)}</strong>`);

            // Law of Sines for A
            // sin(A)/a = sin(C)/c
            const sinA = (a * Math.sin(radC)) / res.c;
            res.A = toDeg(Math.asin(sinA));

            steps.push(`<strong>Paso 2:</strong> Calcular ángulo A con Ley de Senos.<br>sin(A)/${a} = sin(${C}°)/${res.c.toFixed(2)}<br>A = <strong>${res.A.toFixed(2)}°</strong>`);

            // Angle Sum for B
            res.B = 180 - C - res.A;
            steps.push(`<strong>Paso 3:</strong> Calcular ángulo B (suma 180°).<br>B = 180° - ${C}° - ${res.A.toFixed(2)}° = <strong>${res.B.toFixed(2)}°</strong>`);

        } else if (state.mode === 'SSS') {
            // Given a, b, c
            // Check validity
            if (a + b <= c || a + c <= b || b + c <= a) {
                throw new Error("No es un triángulo válido (Desigualdad Triangular).");
            }

            // Law of Cosines for A
            // a^2 = b^2 + c^2 - 2bc cos(A)
            // cos(A) = (b^2 + c^2 - a^2) / 2bc
            const cosA = (b * b + c * c - a * a) / (2 * b * c);
            res.A = toDeg(Math.acos(cosA));
            steps.push(`<strong>Paso 1:</strong> Calcular ángulo A con Ley de Cosenos.<br>cos(A) = (${b}² + ${c}² - ${a}²) / (2*${b}*${c})<br>A = <strong>${res.A.toFixed(2)}°</strong>`);

            // Law of Cosines for B (safer than sines for obtuse angles)
            const cosB = (a * a + c * c - b * b) / (2 * a * c);
            res.B = toDeg(Math.acos(cosB));
            steps.push(`<strong>Paso 2:</strong> Calcular ángulo B con Ley de Cosenos.<br>cos(B) = (${a}² + ${c}² - ${b}²) / (2*${a}*${c})<br>B = <strong>${res.B.toFixed(2)}°</strong>`);

            res.C = 180 - res.A - res.B;
            steps.push(`<strong>Paso 3:</strong> Calcular ángulo C.<br>C = 180° - ${res.A.toFixed(2)}° - ${res.B.toFixed(2)}° = <strong>${res.C.toFixed(2)}°</strong>`);

        } else if (state.mode === 'ASA') {
            // Given A, c, B
            res.C = 180 - A - B;
            if (res.C <= 0) throw new Error("La suma de ángulos debe ser < 180°.");

            steps.push(`<strong>Paso 1:</strong> Calcular ángulo C.<br>C = 180° - ${A}° - ${B}° = <strong>${res.C.toFixed(2)}°</strong>`);

            // Law of Sines for a and b
            // a/sin(A) = c/sin(C)
            const radA = toRad(A);
            const radB = toRad(B);
            const radC = toRad(res.C);

            res.a = c * Math.sin(radA) / Math.sin(radC);
            steps.push(`<strong>Paso 2:</strong> Calcular lado a con Ley de Senos.<br>a = ${c} * sin(${A}°) / sin(${res.C.toFixed(2)}°)<br>a = <strong>${res.a.toFixed(2)}</strong>`);

            res.b = c * Math.sin(radB) / Math.sin(radC);
            steps.push(`<strong>Paso 3:</strong> Calcular lado b con Ley de Senos.<br>b = ${c} * sin(${B}°) / sin(${res.C.toFixed(2)}°)<br>b = <strong>${res.b.toFixed(2)}</strong>`);
        }
    } catch (e) {
        res.valid = false;
        steps = [`<span style="color: #ef4444;">Error: ${e.message}</span>`];
    }

    state.results = res;
    ui.steps.innerHTML = steps.map(s => `<p>${s}</p>`).join('');
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!state.results.valid) return;

    const { a, b, c, A, B, C } = state.results;

    // Coordinates
    // C at (0,0)
    // B at (a, 0)
    // A at (b cos(C), b sin(C))

    // Note: We need to map the calculated logic (where C is origin) to the visual
    // In our logic:
    // SAS: C is the angle between a and b.
    // SSS: We calculated A, B, C. We can place C at origin, B at (a,0), A at ...
    // ASA: We have c, A, B. Let's place A at origin, B at (c, 0), C at ...

    // To be consistent, let's always place the "first point" at origin.
    // Let's use the calculated side lengths a, b, c and angles A, B, C to draw.
    // Let's place Vertex C at origin (0,0).
    // Vertex B at (a, 0).
    // Vertex A at (b * Math.cos(C), b * Math.sin(C)).
    // This works for all if we have all values.

    const radC = toRad(C);

    const pC = { x: 0, y: 0 };
    const pB = { x: a, y: 0 };
    const pA = { x: b * Math.cos(radC), y: b * Math.sin(radC) }; // y grows down in canvas, but let's handle scale first

    // Scale and Center
    const minX = Math.min(pC.x, pB.x, pA.x);
    const maxX = Math.max(pC.x, pB.x, pA.x);
    const minY = Math.min(pC.y, pB.y, pA.y);
    const maxY = Math.max(pC.y, pB.y, pA.y);

    const w = maxX - minX;
    const h = maxY - minY;

    const padding = 60;
    const scaleX = (canvas.width - padding * 2) / w;
    const scaleY = (canvas.height - padding * 2) / h;
    const scale = Math.min(scaleX, scaleY);

    const offsetX = (canvas.width - w * scale) / 2 - minX * scale;
    const offsetY = (canvas.height - h * scale) / 2 - minY * scale;

    // Helper to transform
    const tr = (p) => ({
        x: p.x * scale + offsetX,
        y: canvas.height - (p.y * scale + offsetY) // Flip Y for Cartesian
    });

    const tC = tr(pC);
    const tB = tr(pB);
    const tA = tr(pA);

    // Draw Fill
    ctx.beginPath();
    ctx.moveTo(tC.x, tC.y);
    ctx.lineTo(tB.x, tB.y);
    ctx.lineTo(tA.x, tA.y);
    ctx.closePath();
    ctx.fillStyle = 'rgba(139, 92, 246, 0.1)';
    ctx.fill();

    // Draw Stroke
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#8b5cf6';
    ctx.stroke();

    // Draw Points and Labels
    drawPoint(tA, 'A', A);
    drawPoint(tB, 'B', B);
    drawPoint(tC, 'C', C);

    // Draw Side Labels
    drawLabel(tB, tC, `a = ${a.toFixed(0)}`);
    drawLabel(tC, tA, `b = ${b.toFixed(0)}`);
    drawLabel(tA, tB, `c = ${c.toFixed(0)}`);
}

function drawPoint(p, label, angleVal) {
    ctx.beginPath();
    ctx.arc(p.x, p.y, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#ec4899';
    ctx.fill();

    ctx.fillStyle = 'white';
    ctx.font = 'bold 16px Outfit';
    ctx.fillText(`${label} (${angleVal.toFixed(0)}°)`, p.x + 15, p.y - 15);
}

function drawLabel(p1, p2, text) {
    const midX = (p1.x + p2.x) / 2;
    const midY = (p1.y + p2.y) / 2;

    ctx.fillStyle = '#94a3b8';
    ctx.font = '14px Outfit';
    ctx.fillText(text, midX + 10, midY + 10);
}

function update() {
    // Update display values
    Object.keys(ui.displays).forEach(key => {
        if (state.inputs[key]) {
            ui.displays[key].textContent = key === key.toUpperCase() ? state.inputs[key] + '°' : state.inputs[key];
        }
    });

    solve();
    draw();
}

init();
