import json 
import os 
import sys
import threading
import time
import random
import curses
import Algofind

CURSES_ON = False
def blockPrint():
  sys.stdout = open(os.devnull, 'w')
def enablePrint():
  sys.stdout = sys.__stdout__

def menu():
  print("Snake cheat for Kinu v1.0")
  print("1.) Simulation cheat")
  print("2.) Visualize AI")
  arise = None
  while arise not in ("1","2"): 
    arise = input("Select:")
  if arise == "1":
    makefile()
    return 1
  elif arise == "2":
    CURSES_ON = True
    blockPrint()
    makefile(True)
    return 2
def makefile(*args):
  ignore = False
  if True in args:
    ignore = True
  print("> Creating file")
  open("Snake.log","a").close()
  if os.path.getsize("Snake.log") != 0:
    if not ignore:
      print("> Detected current file in directory, please check it.")
      print(f'Size: {os.path.getsize("Snake.log")}')
      if input("Remove?").lower() == "y":
        os.remove("Snake.log")
      else:
        sys.exit()
  
def Guiscores():
  while not died:
    sys.stdout.write(f"--Working | Scores: {len(snake_body)-4}--\r")
    sys.stdout.flush()
  else:
    print()
    sys.exit()
    
def simulation(vis=True):
  global snake_body
  global died
  algo = Algofind
  died = False
  last_move= None
  sw,sh = os.get_terminal_size()
  print("Starting simulation")
  print(f"Window size: Y{sh} x X{sw}")
  print("Simulating...")
  #ThreadF = threading.Thread(target=Guiscores)
  #ThreadF.daemon = True
  #ThreadF.start()
  snake_x = sw//4
  snake_y = sh//2
  snake_body = [
    [snake_y,snake_x],
    [snake_y,snake_x-1],
    [snake_y,snake_x-2],
    [snake_y,snake_x-3]
  ]
  food = [sh//2,sw//2]
  #Default move command
  with open("Snake.log","a") as file:
    file.write(f"Window_size: {sh},{sw}\n")
    iterations = 0
    while True:
      start = time.time()
      iterations += 1
      score = len(snake_body)-4
      print(f"Iterations: {iterations} Score: {score}")
      def is_border(coordinates,*strict):
          if strict:
            if coordinates[0] >= sh-1 or coordinates[1] >= sw-1:
              return True
          if coordinates[0] in [0,sh-1] or coordinates[1] in [0,sw-1]:
            return True
          return False
      def is_body(coordinates):
          if coordinates in snake_body[1:]:
            return True
          return False
      def mapmap(X,Y, inverse=False):
        ":param inverse - Turn all 1 in matrix to 0 and 0 to 1"
        maze = []
        pathing = (1,0) if not inverse else (0,1)
        for coord_y in range(Y+1):
          y_maze = []
          for coord_x in range(X+1):
            coordinates = [coord_y,coord_x]
            if is_border(coordinates):
              y_maze.append(pathing[0])
            elif is_body(coordinates):
              y_maze.append(pathing[0])
            else:
              y_maze.append(pathing[1])
          maze.append(y_maze)
        return(maze)      
      def move_one_verify(initial):
        terrain = mapmap(sw, sh, inverse=True)
        coord = list(initial)
        weights = {}
        weights = algo.path_plan(terrain, initial)
        most_weight = max(weights, key=weights.get)
        if most_weight == "Down":
          change = coord[0] + 1
          coord[0] = change
        elif most_weight == "Up":
          change = coord[0] - 1
          coord[0] = change
        elif most_weight == "Right":
          change = coord[1] + 1
          coord[1] = change
        elif most_weight == "Left":
          change = coord[1] - 1
          coord[1] = change
        if is_border(coord) or is_body(coord):
            return None
        return coord
      terrain = mapmap(sw,sh, inverse=True)
      #MOVE CHECKER AND CORRECTOR
      if len(snake_body) <= 100:
          path = algo.main(terrain,(snake_body[0][0],snake_body[0][1]),(food[0],food[1]))
          m_iter = len(path)
      elif len(snake_body) <= 150:
          path = algo.main(terrain,(snake_body[0][0],snake_body[0][1]),(food[0],food[1]))[:100]
          m_iter = 100
      elif len(snake_body) <= 500:
          path = algo.main(terrain,(snake_body[0][0],snake_body[0][1]),(food[0],food[1]))[:50]
          m_iter = 50
      elif len(snake_body) <= 1000:
          path = algo.main(terrain,(snake_body[0][0],snake_body[0][1]),(food[0],food[1]))[:10]
          m_iter = 10
      else:
          path = algo.main(terrain,(snake_body[0][0],snake_body[0][1]),(food[0],food[1]))[:5]
          m_iter = 5
      if path[0] == None:
        print("A* returned an Empty path")
        valid_temporary = move_one_verify((snake_body[0][0],snake_body[0][1]))
        if valid_temporary:
          path = algo.main(terrain, valid_temporary, valid_temporary)
        else:
          print("Cannot find a fix for this")
          sys.exit()
      prev_cord = None
      for cord in path:
        new_head = cord
        if not cord:
          print("Path is None type, will ignore")
          continue
        if is_body(new_head) or is_border(new_head):
          print("AI experienced miscalculation and hit an invalid but somehow accepted move. this is a bug")
          sys.exit()
        snake_body.insert(0,new_head)
        if vis:
          try:
            w.addch(snake_body[0][0],snake_body[0][1],"@",curses.color_pair(5))
            w.addch(snake_body[1][0],snake_body[1][1],"@",curses.color_pair(2))
            w.addstr(sh-1,0,f'Score:{score}-',curses.color_pair(3))
            w.addstr(sh-1,11,f'Iter:{iterations}-',curses.color_pair(5))
            w.addstr(sh-1,25,f'Moves/iter:{m_iter}-',curses.color_pair(6))
            w.refresh()
          except curses.error as e:
            curses.endwin()
            print("Error occured, Replay Over!")
            sys.exit()
        if snake_body[0] == food:
          food = None
          while food is None:
            nf = [
                random.randint(1,sh-2),
                random.randint(1,sw-2)
                ]
            food = nf if nf not in snake_body else None 
          if vis:
            w.addch(food[0],food[1], "@", curses.color_pair(1))
        else:
          tail = snake_body.pop()
          if vis:
            w.addch(tail[0],tail[1], ' ')
        if prev_cord and prev_cord == cord:
          print("Skipped, duplicate coordinates")
          continue
        prev_cord = cord
        file.write(f"snake_bod: {snake_body}\n")
        file.write(f"Food: {food}\n")
      time_taken = (time.time() - start) * 1000
      print("Time taken:", round(time_taken, 2), "ms")
      #print("New event soon")
          #print(f"Registered: {new_head}")
      #print(f"SNAKE_POS: {snake_body[0]}")
      #time.sleep(0.01)

if __name__ == "__main__":
  try:
    rel = menu()
    if rel == 1:
      simulation(vis=False)
    elif rel == 2:
      scr = curses.initscr()
      curses.noecho()
      curses.cbreak()
      csw,csh = os.get_terminal_size()
      w = curses.newwin(csh,csw,0,0)
      w.border('|', '|', '-', '-', '+', '+', '+', '+')
      curses.start_color()
      if curses.has_colors():
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED,curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_WHITE,curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_WHITE,curses.COLOR_RED)
        curses.init_pair(4, curses.COLOR_BLACK,curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_BLACK,curses.COLOR_BLUE)
        curses.init_pair(6, curses.COLOR_BLACK,curses.COLOR_GREEN)
      curses.curs_set(0) 
      curses.noecho()
      simulation()
      # curses.reset_shell_mode()
  finally:
    enablePrint()
    if CURSES_ON:
      curses.endwin()
 