let canvas, ctx;
let ROWS = 30, COLS = 50;
let grid = [];
let CELL = 20;
let start = null, goal = null;
let isEditing = false;
let isSettingPoints = false;
let isPlacingCoins = false;
let coins = new Set();

window.addEventListener('load', () => {
    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');
    generateMaze();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('gen').onclick = generateMaze;
    document.getElementById('clear').onclick = clearMaze;
    document.getElementById('edit').onclick = toggleEdit;
    document.getElementById('setpoints').onclick = toggleSetPoints;
    document.getElementById('placeCoins').onclick = toggleCoinPlacement;
    document.getElementById('runAst').onclick = () => runAlgo('/astar', '#2196F3', 'A*');
    document.getElementById('runBfs').onclick = () => runAlgo('/bfs', '#FF9800', 'BFS');
    document.getElementById('runLrta').onclick = () => runAlgo('/lrta', '#9C27B0', 'LRTA*');
    document.getElementById('runDfs').onclick = () => runAlgo('/onlinedfs', '#4CAF50', 'Online DFS');
    document.getElementById('runDijkstra').onclick = () => runAlgo('/dijkstra', '#00CED1', 'Dijkstra');
    document.getElementById('runBinary').onclick = () => runAlgo('/binary', '#008080', 'Binary Backtracking');
    document.getElementById('runBidirectional').onclick = () => runAlgo('/bidirectional', '#E53935', 'Bidirectional Search');
    
    canvas.onclick = handleCanvasClick;
}

async function generateMaze() {
    setStatus('Generating...');
    try {
        const res = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}) // Empty object since we're using server-side dimensions
        });
        
        if (!res.ok) throw new Error('Network response was not ok');
        const data = await res.json();
        
        // Update dimensions from server response
        ROWS = data.rows;
        COLS = data.cols;
        grid = data.grid;

        start = null
        goal = null
        coins.clear()

        resizeCanvas();
        drawGrid();
        setStatus('Maze generated');
    } catch (err) {
        console.error(err);
        setStatus('Error generating maze');
    }
}

function resizeCanvas() {
    canvas.width = COLS * CELL;
    canvas.height = ROWS * CELL;
}

function drawGrid() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid lines first
    ctx.strokeStyle = '#ddd';
    for (let r = 0; r <= ROWS; r++) {
        ctx.beginPath();
        ctx.moveTo(0, r * CELL);
        ctx.lineTo(canvas.width, r * CELL);
        ctx.stroke();
    }
    for (let c = 0; c <= COLS; c++) {
        ctx.beginPath();
        ctx.moveTo(c * CELL, 0);
        ctx.lineTo(c * CELL, canvas.height);
        ctx.stroke();
    }
    
    // Then draw walls
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            if (grid[r][c] === 1) {
                ctx.fillStyle = '#333';
                ctx.fillRect(c * CELL, r * CELL, CELL, CELL);
            }
        }
    }
    
    // Draw coins on top of walls
    ctx.fillStyle = '#FFD700';
    coins.forEach(pos => {
        const [r, c] = pos.split(',').map(Number);
        if (grid[r][c] !== 1) { // Only draw coins on non-wall cells
            ctx.beginPath();
            const centerX = (c + 0.5) * CELL;
            const centerY = (r + 0.5) * CELL;
            ctx.arc(centerX, centerY, CELL/3, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#FFA500';
            ctx.lineWidth = 2;
            ctx.stroke();
        }
    });
    
    // Finally draw start and goal on the very top
    if (start) {
        ctx.fillStyle = '#4CAF50';
        ctx.fillRect(start[1] * CELL, start[0] * CELL, CELL, CELL);
    }
    if (goal) {
        ctx.fillStyle = '#f44336';
        ctx.fillRect(goal[1] * CELL, goal[0] * CELL, CELL, CELL);
    }
}

function handleCanvasClick(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const r = Math.floor(y / CELL);
    const c = Math.floor(x / CELL);
    
    if (r < 0 || r >= ROWS || c < 0 || c >= COLS) return;
    
    if (isEditing) {
        grid[r][c] = grid[r][c] === 1 ? 0 : 1;
        drawGrid();
    } else if (isSettingPoints) {
        if (!start && grid[r][c] !== 1) {
            start = [r, c];
            setStatus('Click to set goal point');
        } else if (!goal && grid[r][c] !== 1 && !(r === start[0] && c === start[1])) {
            goal = [r, c];
            isSettingPoints = false;
            setStatus('Ready');
        }
        drawGrid();
    } else if (isPlacingCoins) {
        drawGrid();
        // Don't allow coins on walls, start, or goal
        if (grid[r][c] === 1) {
            return;
        }
        if (start && r === start[0] && c === start[1]) {
            return;
        }
        if (goal && r === goal[0] && c === goal[1]) {
            return;
        }

        const key = `${r},${c}`;
        if (coins.has(key)) {
            coins.delete(key);
        } else {
            coins.add(key);
        }
        drawGrid();
    }
}

function clearMaze() {
    grid = Array(ROWS).fill().map(() => Array(COLS).fill(0));
    start = null;
    goal = null;
    coins.clear();
    drawGrid();
    setStatus('Maze cleared');
}

function toggleEdit() {
    isEditing = !isEditing;
    isSettingPoints = false;
    isPlacingCoins = false; // Reset coin placement mode
    setStatus(isEditing ? 'Edit mode: Click to toggle walls' : 'Ready');
}

function toggleSetPoints() {
    isSettingPoints = !isSettingPoints;
    isEditing = false;
    isPlacingCoins = false;
    
    if (isSettingPoints) {
        // Only reset points if explicitly requested
        if (!start && !goal) {
            setStatus('Click to set start point');
        } else if (start && !goal) {
            setStatus('Click to set goal point');
        }
        drawGrid();
    } else {
        setStatus('Ready');
    }
}

function toggleCoinPlacement() {
    isPlacingCoins = !isPlacingCoins;
    isEditing = false; // Reset edit mode
    isSettingPoints = false; // Reset points mode
    setStatus(isPlacingCoins ? 'Click to place/remove coins' : 'Ready');
}

async function runAlgo(ep, color, label) {
    if (!start || !goal) {
        setStatus('Please set start and goal points first');
        return;
    }

    drawGrid(); // Clear previous path
    setStatus(`Running ${label}...`);
    const t0 = performance.now();

    try {
        const res = await fetch(ep, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                grid: grid,
                start: start,
                goal: goal,
                coins: Array.from(coins).map(pos => pos.split(',').map(Number))
            })
        });

        if (!res.ok) throw new Error('Network response was not ok');
        const data = await res.json();

        if (!data.path) {
            setStatus(`${label}: No path found`);
            return;
        }

        // Draw visited cells
        ctx.fillStyle = 'rgba(255, 165, 0, 0.2)';
        for (const [r, c, score] of data.visited) {
            if ((r !== start[0] || c !== start[1]) && (r !== goal[0] || c !== goal[1])) {
                ctx.fillRect(c * CELL + 2, r * CELL + 2, CELL - 4, CELL - 4);
            }
        }

        // Draw path with animation
        ctx.fillStyle = color;
        for (const [r, c] of data.path) {
            if ((r !== start[0] || c !== start[1]) && (r !== goal[0] || c !== goal[1])) {
                await new Promise(resolve => setTimeout(resolve, 5));
                ctx.fillRect(c * CELL + 4, r * CELL + 4, CELL - 8, CELL - 8);
            }
        }

        const t1 = performance.now();
        const timeElapsed = ((t1 - t0) / 1000).toFixed(2);
        setStatus(
            `${label} - Path length: ${data.length}, ` +
            `Coins collected: ${data.coins_collected}, ` +
            `Total score: ${data.cost}, ` +
            `Time: ${timeElapsed}s`
        );
    } catch (err) {
        console.error(err);
        setStatus(`Error running ${label}`);
    }
}

function setStatus(message) {
    document.getElementById('status').textContent = message;
}