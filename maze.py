import random
from typing import List

def generate_random_maze(rows: int, cols: int) -> List[List[int]]:
    # Nếu hàng hoặc cột là số chẵn thì tăng lên 1 để thành số lẻ
    if rows % 2 == 0:
        rows += 1
    if cols % 2 == 0:
        cols += 1

    # Khởi tạo mê cung toàn tường (1)
    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    def is_valid(x: int, y: int) -> bool:
        # chỉ carve bên trong, không chạm biên
        return 0 < x < rows - 1 and 0 < y < cols - 1

    def dfs(x: int, y: int):
        maze[x][y] = 0
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            wx, wy = x + dx // 2, y + dy // 2  # vị trí tường cần đục
            if is_valid(nx, ny) and maze[nx][ny] == 1:
                maze[wx][wy] = 0
                dfs(nx, ny)

    # Bắt đầu DFS từ một ô lẻ ngẫu nhiên (để không chạm biên ngay)
    start_x = random.randrange(1, rows - 1, 2)
    start_y = random.randrange(1, cols - 1, 2)
    dfs(start_x, start_y)

    # Đảm bảo start và goal không bị tường
    maze[1][1] = 0
    maze[rows - 2][cols - 2] = 0

    return maze

def generate_symmetric_maze(rows: int, cols: int) -> List[List[int]]:
    # Ensure odd dimensions
    if rows % 2 == 0: rows += 1
    if cols % 2 == 0: cols += 1
    
    # Initialize with all walls
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    
    # Calculate center goal position
    goal_x = rows // 2
    goal_y = cols // 2
    
    def is_valid(x: int, y: int) -> bool:
        return 0 < x < rows - 1 and 0 < y < cols//2
    
    def dfs(x: int, y: int, target_x: int, target_y: int, branch_chance: float = 0.8):
        maze[x][y] = 0
        maze[x][cols-1-y] = 0  # Symmetric path
        
        # Calculate direction weights based on distance to target
        dx_to_target = target_x - x
        dy_to_target = target_y - y
        
        # Prioritize directions that lead to target
        directions = []
        
        # Add vertical directions based on target
        if dx_to_target > 0:
            directions.extend([(2, 0)] * 2)  # Bias downward
        elif dx_to_target < 0:
            directions.extend([(-2, 0)] * 2)  # Bias upward
            
        # Add horizontal directions based on target
        if dy_to_target > 0:
            directions.extend([(0, 2)] * 2)  # Bias right
        elif dy_to_target < 0:
            directions.extend([(0, -2)] * 2)  # Bias left
            
        # Add standard directions for variety
        directions.extend([(2, 0), (-2, 0), (0, 2), (0, -2)])
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            wx, wy = x + dx//2, y + dy//2
            
            if is_valid(nx, ny) and maze[nx][ny] == 1:
                if random.random() < branch_chance:
                    maze[wx][wy] = 0
                    maze[wx][cols-1-wy] = 0
                    dfs(nx, ny, target_x, target_y, branch_chance * 0.95)
    
    # Create paths from multiple start points to goal
    num_starts = rows // 4
    start_points = random.sample(range(1, rows-1, 2), min(num_starts, rows//2))
    
    for start_x in start_points:
        dfs(start_x, 1, goal_x, goal_y)
    
    # Ensure start points and goal are clear
    maze[1][1] = 0  # Start point 1
    maze[1][cols-2] = 0  # Start point 2
    maze[goal_x][goal_y] = 0  # Center goal
    
    # Create clear area around goal
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if 0 < goal_x + dx < rows-1 and 0 < goal_y + dy < cols-1:
                maze[goal_x + dx][goal_y + dy] = 0
    
    # Ensure connectivity
    def flood_fill(x: int, y: int, visited: set):
        if not (0 <= x < rows and 0 <= y < cols) or maze[x][y] == 1 or (x,y) in visited:
            return
        visited.add((x,y))
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            flood_fill(x + dx, y + dy, visited)
    
    visited = set()
    flood_fill(1, 1, visited)
    
    # If goal is not reachable, create path
    if (goal_x, goal_y) not in visited:
        current_x, current_y = 1, 1
        while current_x < goal_x:
            maze[current_x][current_y] = 0
            maze[current_x][cols-1-current_y] = 0
            current_x += 1
        while current_y < goal_y:
            maze[current_x][current_y] = 0
            maze[current_x][cols-1-current_y] = 0
            current_y += 1
    
    return maze