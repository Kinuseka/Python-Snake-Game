from pathfinding.core.grid import Grid
from pathfinding.core.grid import GridNode
from pathfinding.finder.a_star import AStarFinder

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
def path_plan(maze, start, direction) -> int:
    "Returns confidence level"
    grid = Grid(matrix=maze)
    curr_dir = list(start)
    weight = 0
    while grid.walkable(curr_dir[1], curr_dir[0]):
        if direction == "Left":
            curr_dir[1] -= 1
        elif direction == "Right":
            curr_dir[1] += 1
        elif direction == "Up":
            curr_dir[0] -= 1
        elif direction == "Down":
            curr_dir[0] += 1
        weight += 1
    else:
        return weight



if __name__ == '__main__':
    main()