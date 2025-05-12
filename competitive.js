const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const CELL_SIZE = 20;
let maze = [];
let isEditing = false;
let isPlacingCoins = false;
let isSettingStart1 = false;
let isSettingStart2 = false;
let isSettingGoal = false;
let isPlacingWalls = false;

let start1 = null;
let start2 = null;
let goal = null;
let coins = new Set();

// Animation states
let agent1Path = [];
let agent2Path = [];
let agent1Visited = [];
let agent2Visited = [];
let currentStep = 0;
let animationId = null;
let isCompeting = false;
let animationSpeed = 100; // milliseconds between steps
let startTime = 0; // Add at the top with other state variables

// Initialize canvas
function initCanvas() {
    const width = window.innerWidth - 300;
    const height = window.innerHeight - 40;
    canvas.width = Math.floor(width / CELL_SIZE) * CELL_SIZE;
    canvas.height = Math.floor(height / CELL_SIZE) * CELL_SIZE;
}

// Initialize empty grid
function initEmptyGrid() {
    const rows = Math.floor(canvas.height / CELL_SIZE);
    const cols = Math.floor(canvas.width / CELL_SIZE);
    maze = Array(rows).fill().map(() => Array(cols).fill(0));
    
    // Add border walls
    for(let i = 0; i < rows; i++) {
        maze[i][0] = 1;
        maze[i][cols-1] = 1;
    }
    for(let j = 0; j < cols; j++) {
        maze[0][j] = 1;
        maze[rows-1][j] = 1;
    }
}

// Generate symmetric maze
async function generateMaze() {
    const rows = Math.floor(canvas.height / CELL_SIZE);
    const cols = Math.floor(canvas.width / CELL_SIZE);
    
    const response = await fetch('/generate_symmetric_maze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({rows, cols})
    });
    
    maze = await response.json();
    resetCompetition();
    drawMaze();
}

// Draw functions
function drawMaze() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid first
    drawGrid();
    
    // Draw walls
    for(let i = 0; i < maze.length; i++) {
        for(let j = 0; j < maze[0].length; j++) {
            if(maze[i][j] === 1) {
                ctx.fillStyle = '#333';
                ctx.fillRect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE);
            }
        }
    }
    
    // Draw coins with glow effect
    coins.forEach(coin => {
        ctx.fillStyle = '#FFD700';
        ctx.shadowColor = '#FFD700';
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.arc(
            coin[1] * CELL_SIZE + CELL_SIZE/2,
            coin[0] * CELL_SIZE + CELL_SIZE/2,
            CELL_SIZE/3,
            0,
            Math.PI * 2
        );
        ctx.fill();
        ctx.shadowBlur = 0; // Reset shadow
    });
    
    // Draw start and goal with highlight
    if(start1) {
        ctx.fillStyle = '#4CAF50';
        ctx.globalAlpha = 0.7;
        ctx.fillRect(start1[1] * CELL_SIZE, start1[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE);
        ctx.globalAlpha = 1;
    }
    if(start2) {
        ctx.fillStyle = '#2196F3';
        ctx.globalAlpha = 0.7;
        ctx.fillRect(start2[1] * CELL_SIZE, start2[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE);
        ctx.globalAlpha = 1;
    }
    if(goal) {
        ctx.fillStyle = '#E53935';
        ctx.globalAlpha = 0.7;
        ctx.fillRect(goal[1] * CELL_SIZE, goal[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE);
        ctx.globalAlpha = 1;
    }
}

function drawGrid() {
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 0.5;

    // Draw vertical lines
    for(let x = 0; x <= canvas.width; x += CELL_SIZE) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }

    // Draw horizontal lines
    for(let y = 0; y <= canvas.height; y += CELL_SIZE) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
}

function drawAgentPaths() {
    // Draw visited cells
    agent1Visited.forEach(cell => {
        ctx.fillStyle = 'rgba(76, 175, 80, 0.2)';
        ctx.fillRect(cell[1] * CELL_SIZE, cell[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE);
    });
    
    agent2Visited.forEach(cell => {
        ctx.fillStyle = 'rgba(33, 150, 243, 0.2)';
        ctx.fillRect(cell[1] * CELL_SIZE, cell[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE);
    });
    
    // Draw paths
    if(agent1Path.length > 0) {
        drawPath(agent1Path.slice(0, currentStep), '#4CAF50');
    }
    if(agent2Path.length > 0) {
        drawPath(agent2Path.slice(0, currentStep), '#2196F3');
    }
}

// Competition handling
async function startCompetition() {
    if(!start1 || !start2 || !goal) {
        document.getElementById('status').textContent = 'Please set both start points and goal first!';
        return;
    }
    
    if(isCompeting) {
        document.getElementById('status').textContent = 'Competition already running!';
        return;
    }
    
    const algo1 = document.getElementById('algo1').value;
    const algo2 = document.getElementById('algo2').value;
    
    try {
        document.getElementById('status').textContent = 'Competition started...';
        isCompeting = true;
        startTime = performance.now(); // Start timing
        document.getElementById('startCompetition').textContent = 'Running...';
        
        const response = await fetch('/competitive', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                grid: maze,
                starts: [start1, start2],
                goal: goal,
                coins: Array.from(coins),
                algo1: algo1,
                algo2: algo2
            })
        });
        
        if (!response.ok) {
            throw new Error('Server error');
        }
        
        const result = await response.json();
        animateCompetition(result);
    } catch (error) {
        document.getElementById('status').textContent = 'Error: ' + error.message;
    } finally {
        document.getElementById('startCompetition').textContent = 'Start Competition';
    }
}

// Update the animateCompetition function
function animateCompetition(result) {
    if (!result.states || result.states.length === 0) {
        document.getElementById('status').textContent = 'No valid paths found!';
        return;
    }

    // Store final paths
    let finalPath1 = [];
    let finalPath2 = [];
    let agent1ReachedGoal = false;
    let agent2ReachedGoal = false;
    
    currentStep = 0;
    
    function animate() {
        if (currentStep < result.states.length) {
            const currentState = result.states[currentStep];
            
            // Update paths if they exist in current state
            if (currentState.agent1?.path?.length > 0) {
                finalPath1 = currentState.agent1.path;
                if (!agent1ReachedGoal) {
                    const lastPoint = finalPath1[finalPath1.length - 1];
                    if (lastPoint[0] === goal[0] && lastPoint[1] === goal[1]) {
                        agent1ReachedGoal = true;
                    }
                }
            }
            if (currentState.agent2?.path?.length > 0) {
                finalPath2 = currentState.agent2.path;
                if (!agent2ReachedGoal) {
                    const lastPoint = finalPath2[finalPath2.length - 1];
                    if (lastPoint[0] === goal[0] && lastPoint[1] === goal[1]) {
                        agent2ReachedGoal = true;
                    }
                }
            }
            
            // Draw everything
            drawMaze();
            
            // Draw paths as colored squares
            if (finalPath1.length > 0) {
                finalPath1.forEach(cell => {
                    ctx.fillStyle = '#4CAF50';
                    ctx.globalAlpha = 0.5;
                    ctx.fillRect(cell[1] * CELL_SIZE, cell[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE);
                });
            }
            
            if (finalPath2.length > 0) {
                finalPath2.forEach(cell => {
                    ctx.fillStyle = '#2196F3';
                    ctx.globalAlpha = 0.5;
                    ctx.fillRect(cell[1] * CELL_SIZE, cell[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE);
                });
            }
            
            ctx.globalAlpha = 1;
            
            // Update status with who has reached goal
            let statusText = [];
            if (agent1ReachedGoal) statusText.push("Agent 1: Reached goal!");
            if (agent2ReachedGoal) statusText.push("Agent 2: Reached goal!");
            if (statusText.length === 0) statusText.push("Racing to goal...");
            
            // Add elapsed time to status
            const elapsedTime = ((performance.now() - startTime) / 1000).toFixed(2);
            document.getElementById('status').textContent = 
                `Time: ${elapsedTime}s | ${statusText.join(" | ")}`;
            
            // If either agent reaches goal, determine winner
            if (agent1ReachedGoal || agent2ReachedGoal) {
                const finalTime = performance.now() - startTime;
                isCompeting = false;
                if (agent1ReachedGoal && !agent2ReachedGoal) {
                    showWinner({ winner: 'agent1', time: finalTime });
                    return;
                } else if (agent2ReachedGoal && !agent1ReachedGoal) {
                    showWinner({ winner: 'agent2', time: finalTime });
                    return;
                }
            }
                
            currentStep++;
            animationId = setTimeout(() => requestAnimationFrame(animate), animationSpeed);
        }
    }
    
    if (animationId) {
        clearTimeout(animationId);
        cancelAnimationFrame(animationId);
    }
    
    animate();
}

// Update showWinner function
function showWinner(result) {
    const display = document.getElementById('winner-display');
    const text = document.getElementById('winner-text');
    display.classList.remove('winner-hidden');
    
    const timeInSeconds = (result.time / 1000).toFixed(2);
    const winnerText = `${result.winner === 'agent1' ? 'Agent 1' : 'Agent 2'} wins! (${timeInSeconds}s)`;
    
    text.textContent = winnerText;
    document.getElementById('status').textContent = `Competition finished in ${timeInSeconds}s`;
}

// Event handlers
canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;    // Add scaling factor
    const scaleY = canvas.height / rect.height;  // Add scaling factor
    
    // Calculate position with scale factor
    const x = Math.floor(((e.clientX - rect.left) * scaleX) / CELL_SIZE);
    const y = Math.floor(((e.clientY - rect.top) * scaleY) / CELL_SIZE);
    
    // Boundary check
    if (y < 0 || y >= maze.length || x < 0 || x >= maze[0].length) return;
    
    // Don't allow editing border walls
    if (y === 0 || y === maze.length-1 || x === 0 || x === maze[0].length-1) return;

    if (isPlacingWalls) {
        maze[y][x] = maze[y][x] === 1 ? 0 : 1;
    } else if (isPlacingCoins && maze[y][x] !== 1) {
        const point = [y, x];
        const pointStr = JSON.stringify(point); // Convert to string for Set comparison
        if (Array.from(coins).some(coin => JSON.stringify(coin) === pointStr)) {
            coins.delete(Array.from(coins).find(coin => JSON.stringify(coin) === pointStr));
        } else {
            coins.add(point);
        }
    } else if (isSettingStart1 && maze[y][x] !== 1) {
        start1 = [y, x];
        isSettingStart1 = false;
        document.getElementById('status').textContent = 'Start point 1 set';
    } else if (isSettingStart2 && maze[y][x] !== 1) {
        start2 = [y, x];
        isSettingStart2 = false;
        document.getElementById('status').textContent = 'Start point 2 set';
    } else if (isSettingGoal && maze[y][x] !== 1) {
        goal = [y, x];
        isSettingGoal = false;
        document.getElementById('status').textContent = 'Goal point set';
    }
    
    drawMaze();
});

// Button handlers
document.getElementById('gen').onclick = generateMaze;
document.getElementById('clear').onclick = () => {
    initEmptyGrid(); // Reset to empty grid with borders
    resetCompetition();
    drawMaze();
};
document.getElementById('edit').onclick = () => {
    // Reset all other modes
    isPlacingCoins = false;
    isSettingStart1 = false;
    isSettingStart2 = false;
    isSettingGoal = false;
    isPlacingWalls = !isPlacingWalls;
    document.getElementById('status').textContent = isPlacingWalls ? 'Click to add/remove walls' : 'Ready';
};
document.getElementById('placeCoins').onclick = () => {
    // Reset all other modes
    isPlacingWalls = false;
    isSettingStart1 = false;
    isSettingStart2 = false;
    isSettingGoal = false;
    isPlacingCoins = !isPlacingCoins;
    document.getElementById('status').textContent = isPlacingCoins ? 'Click to place/remove coins' : 'Ready';
};
document.getElementById('setStartPoints1').onclick = () => {
    // Reset all other modes
    isPlacingWalls = false;
    isPlacingCoins = false;
    isSettingStart2 = false;
    isSettingGoal = false;
    isSettingStart1 = true;
    document.getElementById('status').textContent = 'Click to set Agent 1 start point';
};
document.getElementById('setStartPoints2').onclick = () => {
    // Reset all other modes
    isPlacingWalls = false;
    isPlacingCoins = false;
    isSettingStart1 = false;
    isSettingGoal = false;
    isSettingStart2 = true;
    document.getElementById('status').textContent = 'Click to set Agent 2 start point';
};
document.getElementById('setGoal').onclick = () => {
    // Reset all other modes
    isPlacingWalls = false;
    isPlacingCoins = false;
    isSettingStart1 = false;
    isSettingStart2 = false;
    isSettingGoal = true;
    document.getElementById('status').textContent = 'Click to set goal point';
};
document.getElementById('startCompetition').onclick = startCompetition;

function resetCompetition() {
    start1 = null;
    start2 = null;
    goal = null;
    coins.clear();
    agent1Path = [];
    agent2Path = [];
    agent1Visited = [];
    agent2Visited = [];
    currentStep = 0;
    if(animationId) cancelAnimationFrame(animationId);
    isCompeting = false;
    document.getElementById('startCompetition').textContent = 'Start Competition';
    document.getElementById('status').textContent = 'Ready';
    document.getElementById('winner-display').classList.add('winner-hidden');
}

// Initialize
window.onload = () => {
    initCanvas();
    initEmptyGrid(); // Initialize empty grid first
    drawMaze();     // Draw the initial state
    generateMaze();
};