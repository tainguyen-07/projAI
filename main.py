from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from maze import *
from algo2 import *
from typing import List, Set, Dict, Any

ROWS = 31
COLS = 101

class CompetitiveMazeRequest(BaseModel):
    grid: List[List[int]]
    starts: List[List[int]]
    goal: List[int]
    coins: List[List[int]]
    algo1: str
    algo2: str

class MazeRequest(BaseModel):
    grid: List[List[int]]
    start: List[int]
    goal: List[int]
    coins: List[List[int]] = []

app = FastAPI()

def create_grid_and_nodes(req: MazeRequest):
    """Helper function to create grid and nodes from request"""
    grid = Grid(len(req.grid), len(req.grid[0]), req.grid)
    start_node = Node(req.start[0], req.start[1])
    goal_node = Node(req.goal[0], req.goal[1])
    coins = {Node(x, y) for x, y in req.coins}
    return grid, start_node, goal_node, coins

def process_search_result(generator, coins_set: Set[Node]) -> Dict[str, Any]:
    """Process search results after collecting all possible paths"""
    all_paths = []  # Store all paths and their info
    
    try:
        import sys
        original_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)
        
        # Collect all paths first
        for path, visited in generator:
            if path:
                coins_collected = sum(1 for node in path if node in coins_set)
                path_length = len(path)
                all_paths.append({
                    'path': path,
                    'visited': visited,
                    'coins': coins_collected,
                    'length': path_length
                })
        
        if not all_paths:
            return {
                "path": [],
                "visited": [],
                "cost": 0,
                "length": 0,
                "coins_collected": 0,
                "score": 0
            }
        
        # Sort paths by coins first, then by length
        sorted_paths = sorted(
            all_paths,
            key=lambda x: (x['coins'], -x['length']),  # Sort by coins descending, then length ascending
            reverse=True
        )
        
        # Select best path
        best_path = sorted_paths[0]
        
        # Calculate final metrics
        total_coins = best_path['coins']
        path_length = best_path['length']
        total_cost = path_length - (total_coins * 1000)
        score = (total_coins * 1000) - path_length
        
    except RecursionError:
        return {
            "path": [],
            "visited": [],
            "cost": 0,
            "length": 0,
            "coins_collected": 0,
            "score": 0,
            "error": "Path too deep - recursion limit reached"
        }
    finally:
        sys.setrecursionlimit(original_limit)
    
    return {
        "path": [(p.hang, p.cot) for p in best_path['path']],
        "visited": best_path['visited'],
        "cost": total_cost,
        "length": path_length,
        "coins_collected": total_coins,
        "score": score
    }

@app.post("/astar")
def run_astar(req: MazeRequest):
    grid, start, goal, coins = create_grid_and_nodes(req)
    generator = astar_search_with_animation(grid, start, goal, coins)
    return process_search_result(generator, coins)

@app.post("/bfs")
def run_bfs(req: MazeRequest):
    grid, start, goal, coins = create_grid_and_nodes(req)
    generator = bfs_search_withAnimation(grid, start, goal, coins)
    return process_search_result(generator, coins)

@app.post("/lrta")
def run_lrta(req: MazeRequest):
    grid, start, goal, coins = create_grid_and_nodes(req)
    generator = lrta_star_search_with_animation(grid, start, goal, coins)
    return process_search_result(generator, coins)

@app.post("/onlinedfs")
def run_online_dfs(req: MazeRequest):
    grid, start, goal, coins = create_grid_and_nodes(req)
    generator = online_dfs_search_with_animation(grid, start, goal, coins)
    return process_search_result(generator, coins)

@app.post("/dijkstra")
def run_dijkstra(req: MazeRequest):
    grid, start, goal, coins = create_grid_and_nodes(req)
    generator = dijkstra_search_with_animation(grid, start, goal, coins)
    return process_search_result(generator, coins)

@app.post("/binary")
def run_binary_backtracking(req: MazeRequest):
    grid, start, goal, coins = create_grid_and_nodes(req)
    generator = binary_backtracking_search_with_animation(grid, start, goal, coins)
    return process_search_result(generator, coins)

@app.post("/bidirectional")
def run_bidirectional_search(req: MazeRequest):
    grid, start, goal, coins = create_grid_and_nodes(req)
    generator = bidirectional_search_with_animation(grid, start, goal, coins)
    return process_search_result(generator, coins)

@app.post("/generate_symmetric_maze")
def generate_maze_endpoint(data: dict):
    rows = data.get("rows", 20)
    cols = data.get("cols", 30)
    maze = generate_symmetric_maze(rows, cols)
    return maze

# Add algorithm mapping at the top of the file
algo_map = {
    "astar": astar_search_with_animation,
    "bfs": bfs_search_withAnimation,
    "lrta": lrta_star_search_with_animation,
    "onlinedfs": online_dfs_search_with_animation,
    "dijkstra": dijkstra_search_with_animation,
    "binary": binary_backtracking_search_with_animation,
    "bidirectional": bidirectional_search_with_animation
}

@app.post("/competitive")
def run_competitive(req: CompetitiveMazeRequest):
    if not req.grid or not req.starts or len(req.starts) < 2 or not req.goal:
        raise HTTPException(
            status_code=400, 
            detail="Missing or invalid input data"
        )

    try:
        # Create grid and nodes
        grid = Grid(len(req.grid), len(req.grid[0]), req.grid)
        start1 = Node(req.starts[0][0], req.starts[0][1])
        start2 = Node(req.starts[1][0], req.starts[1][1])
        goal = Node(req.goal[0], req.goal[1])
        coins = {Node(x, y) for x, y in req.coins} if req.coins else set()

        # Get algorithm functions
        gen1 = algo_map.get(req.algo1)
        gen2 = algo_map.get(req.algo2)

        if not gen1 or not gen2:
            raise HTTPException(
                status_code=400,
                detail="Invalid algorithm selection"
            )

        # Initialize generators
        gen1 = gen1(grid, start1, goal, coins)
        gen2 = gen2(grid, start2, goal, coins)

        # Process results
        states = []
        current_state = {
            "agent1": {"path": [], "visited": [], "steps": 0},
            "agent2": {"path": [], "visited": [], "steps": 0}
        }
        states.append(current_state.copy())

        path1_complete = False
        path2_complete = False
        steps1 = 0
        steps2 = 0

        while not (path1_complete and path2_complete):
            current_state = {
                "agent1": {"path": [], "visited": [], "steps": steps1},
                "agent2": {"path": [], "visited": [], "steps": steps2}
            }

            # Update agent 1
            if not path1_complete:
                try:
                    path, visited = next(gen1)
                    current_state["agent1"]["visited"] = visited
                    if path:
                        path1_complete = True
                        current_state["agent1"]["path"] = [
                            [p.hang, p.cot] for p in path
                        ]
                    steps1 += 1
                except StopIteration:
                    path1_complete = True

            # Update agent 2
            if not path2_complete:
                try:
                    path, visited = next(gen2)
                    current_state["agent2"]["visited"] = visited
                    if path:
                        path2_complete = True
                        current_state["agent2"]["path"] = [
                            [p.hang, p.cot] for p in path
                        ]
                    steps2 += 1
                except StopIteration:
                    path2_complete = True

            states.append(current_state.copy())

        return {
            "states": states,
            "winner": "agent1" if steps1 <= steps2 else "agent2",
            "agent1_steps": steps1,
            "agent2_steps": steps2
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing competition: {str(e)}"
        )

# File serving routes
@app.get("/style.css")
def get_css():
    return FileResponse("style.css")

@app.get("/script.js")
def get_js():
    return FileResponse("script.js")

@app.get("/competitive.js")
def get_js():
    return FileResponse("competitive.js")

@app.get("/")
def serve_frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
    
@app.get("/competitive")
def serve_competitive():
    with open("competitive.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Maze generation route
@app.post("/generate")
def generate(req: dict):
    grid = generate_random_maze(ROWS, COLS)
    return {"rows": ROWS, "cols": COLS, "grid": grid}

#change nodejs version