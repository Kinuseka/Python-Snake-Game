from pathfinding.core.grid import Grid
from pathfinding.core.grid import GridNode
from pathfinding.finder.a_star import AStarFinder
from collections import deque

finder = AStarFinder()
def main(maze,start,end):
    grid = Grid(matrix=maze)
    g_start = grid.node(start[1],start[0])
    g_end = grid.node(end[1],end[0])
    path = finder.find_path(g_start, g_end, grid)
    found_path = path[0]
    if len(found_path) != 0:
      #convert GridNode object to list
      #eg as Each GridNodes
      pathed = [[eg.y, eg.x] for eg in found_path]
      return(pathed)
    return [None]

def reachable_area(grid, maze, start_row, start_col) -> int:
    rows, cols = len(maze), len(maze[0])
    if not (0 <= start_row < rows and 0 <= start_col < cols):
        return 0
    if not grid.walkable(start_col, start_row):
        return 0

    visited = set()
    q = deque()
    q.append((start_row, start_col))
    visited.add((start_row, start_col))

    # 4-connected neighbors
    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    area = 0

    while q:
        r, c = q.popleft()
        area += 1
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < rows and 0 <= nc < cols and
                (nr, nc) not in visited and
                grid.walkable(nc, nr)
            ):
                visited.add((nr, nc))
                q.append((nr, nc))

    return area

def path_plan(maze, start) -> int:
    "Returns confidence level"
    grid = Grid(matrix=maze)
    curr_dir = list(start)
    directions = {
        "Left":  (0, -1),
        "Right": (0,  1),
        "Up":    (-1, 0),
        "Down":  (1,  0),
    }

    paths = {}

    for name, (dr, dc) in directions.items():
        nr = curr_dir[0] + dr
        nc = curr_dir[1] + dc

        # how much space is available if we go here?
        area = reachable_area(grid, maze, nr, nc)

        paths[name] = area  # weight / confidence for this direction

    return paths


if __name__ == '__main__':
    main()