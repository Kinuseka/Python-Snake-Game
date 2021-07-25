import curses
import random
import time 
import sys
import os
import logging
import traceback
import re 
import json


def Introduction():
  print("Welcome snake v1.0")
  print("This fun so enjoy i guess")
  time.sleep(1)
 
def continue_render(sh,sw):
  global window_continue
  csh,csw = scr.getmaxyx()
  if curses.has_colors():
    curses.use_default_colors()
    curses.init_pair(90, curses.COLOR_WHITE,curses.COLOR_WHITE)
  w2 = curses.newwin(csh,csw)
  while not csh >= sh and not csw >= sw:
    csh,csw = scr.getmaxyx()
    w2.addstr(0,0,"THE SIZE OF YOUR WINDOW IS SMALLER")
    w2.addstr(1,0,"THAN THE GIVEN WINDOW! PLEASE RESIZE!")
    w2.addstr(2,0,"Windows/Linux: Drag the outer box")
    w2.addstr(3,0,"Android(Termux): Pinch your terminal outwards")
    w2.refresh()
  else:
    w2.touchwin()
    w2.refresh()
    del w2
  window_continue = curses.newwin(sh,sw,0,0)
  timed = 5 / len(prev_snake)
  for i,snake in enumerate(prev_snake):
    window_continue.addstr(0,0,f"Get ready in:  5 seconds")
    window_continue.addch(snake[0],snake[1],"@",curses.color_pair(90))
    time.sleep(timed)
    window_continue.refresh()
    
 
def MainMenu(): 
  sh,sw = scr.getmaxyx()
  if curses.has_colors():
    curses.use_default_colors()
    curses.init_pair(1,curses.COLOR_RED,curses.COLOR_YELLOW)
    curses.init_pair(2,curses.COLOR_YELLOW,curses.COLOR_RED)
    curses.init_pair(3,curses.COLOR_WHITE,curses.COLOR_GREEN)
  sh = sh
  sw = sw
  w = curses.newwin(sh,sw,0,0)
  w.keypad(1)
  w.timeout(100)
  w.bkgd(" ",curses.color_pair(3))
  w.border('|', '|', '-', '-', '+', '+', '+', '+')
  KEY_UP = ord("w")
  KEY_DOWN = ord("s")
  key = 0
  start_button = [sh//4,sw//5]
  exit_button = [sh-sh//2,sw//5]
  initial_select = [start_button[0],start_button[1]-2]
  selected = "Start"
  while True:
    key = w.getch()
    w.addstr(sh//8,sw//4,"SNEK GAME BY KINU",curses.color_pair(1) | curses.A_BOLD)
    w.addch(initial_select[0],initial_select[1],">",curses.color_pair(2) | curses.A_BLINK)
    w.addstr(start_button[0],start_button[1],"Start",curses.color_pair(1) | curses.A_BOLD)
    w.addstr(exit_button[0],exit_button[1],"Exit",curses.color_pair(1) | curses.A_BOLD)
    #w.addstr(sh//2,sw//2,"Exit",curses.color_pair(1))
    if key == KEY_UP:
      initial_select = [start_button[0],start_button[1]-2]
      selected = "Start"
      w.addch(exit_button[0],exit_button[1]-2," ",curses.color_pair(3))
    elif key == KEY_DOWN:
      initial_select = [exit_button[0],exit_button[1]-2]
      selected = "Exit"
      w.addch(start_button[0],start_button[1]-2," ",curses.color_pair(3))
    if key == 10:
      if selected == "Start":
        if status:
          w2 = curses.newwin(sh,sw,0,0)
          w2.keypad(1)
          w2.timeout(100)
          w2.bkgd(" ",curses.color_pair(3))
          w2.border('|', '|', '-', '-', '+', '+', '+', '+')
          while True:
            key2 = w2.getch()
            w2.addstr(sh//8,sw//4,"Game Data existing\n,do you want to continue?",curses.color_pair(1) | curses.A_BOLD)
            w2.addch(initial_select[0],initial_select[1],">",curses.color_pair(2) | curses.A_BLINK)
            w2.addstr(start_button[0],start_button[1],"Yes",curses.color_pair(1) | curses.A_BOLD)
            w2.addstr(exit_button[0],exit_button[1],"No",curses.color_pair(1) | curses.A_BOLD)
            if key2 == KEY_UP:
              initial_select = [start_button[0],start_button[1]-2]
              selected = "Start"
              w2.addch(exit_button[0],exit_button[1]-2," ",curses.color_pair(3))
            elif key2 == KEY_DOWN:
              initial_select = [exit_button[0],exit_button[1]-2]
              selected = "Exit"
              w2.addch(start_button[0],start_button[1]-2," ",curses.color_pair(3))
            if key2 == 10:
              if selected == "Start":
                return True
              elif selected == "Exit":
                curses.endwin()
                break
        return False
      elif selected == "Exit":
        sys.exit()
    #time.sleep(1)
    
def GameStart(permission):
  #Change this if u want to change keybind
  KEY_UP = ord("w")
  KEY_LEFT = ord("a")
  KEY_DOWN = ord("s")
  KEY_RIGHT = ord("d")
  #Define Scores
  score = {"Snake":0}
  #Initialize curses
  if curses.has_colors():
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED,curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_WHITE,curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE,curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_BLACK,curses.COLOR_WHITE)
    curses.init_pair(5,curses.COLOR_WHITE,curses.COLOR_GREEN)
    curses.init_pair(6,curses.COLOR_WHITE,-1)
  #Get initial snake position
  if not permission:
    sh,sw = scr.getmaxyx()
    snake_x = sw//4
    snake_y = sh//2
    snake_bod = [
      [snake_y,snake_x],
      [snake_y,snake_x-1],
      [snake_y,snake_x-2],
      [snake_y,snake_x-3]
      ]
    #Food
    food = [sh//2,sw//2]
    w = curses.newwin(sh,sw,0,0)
  elif permission:
    def Check_last_move(Data):
      Coordinates = Data[2]
      Operator = Data[1]
      Mushed = str(Operator)+str(Coordinates)
      if Mushed == "+0":
        return(KEY_DOWN)
      elif Mushed == "-0":
        return(KEY_UP)
      elif Mushed == "+1":
        return(KEY_RIGHT)
      elif Mushed == "-1":
        return(KEY_LEFT)
    
    snake_bod = prev_snake
    food = prev_food
    sh = prev_sh
    sw = prev_sw
    score["Snake"] = prev_score
    continued_prev_data = Check_last_move(prev_lastmov)
    w = window_continue
  logger.debug(f"Window_size: {sh},{sw}")
  w.keypad(1)
  w.timeout(100)
  w.border('|', '|', '-', '-', '+', '+', '+', '+')
  w.addch(food[0],food[1],"@",curses.color_pair(1))
  key = KEY_RIGHT if not permission else continued_prev_data #default snake run
  #Movement snake
  error = False
  last_movement = []
  last_key = -1
  while True:
    try:
      while True:
        logger.debug(f"last_movement:{last_movement}")
        get_key = w.getch()
        key = key if get_key == -1 else get_key
        #Quit if gameover
        if snake_bod[0][0] in [0,sh-1] or snake_bod[0][1] in [0,sw-1] or error:
          curses.endwin()
          print("SNAKE WENT OUT LMAO NOOB")
          print("Score:",score["Snake"])
          sys.exit()
        if snake_bod[0] in snake_bod[1:]:
          curses.endwin()
          print("U ATE UR SELF WTF WEIRDO")
          print("Score:",score["Snake"])
          sys.exit()
        new_head = [snake_bod[0][0],snake_bod[0][1]]
        class Movement():
          def LAST_MOVEMENT(self):
            if last_movement:
              coordinates = last_movement[0]
              position = coordinates[0]
              operator = coordinates[1]
              index = coordinates[2]
              logger.debug(f"Movement_1: {coordinates}")
              if operator == "+":
                position += 1
              elif operator == "-":
                position -= 1
              new_head[int(index)] = position
              last_movement.append([new_head[index],operator,index])
              if len(last_movement) == 2:
                del last_movement[0]
            else:
              print("EMPTY LIST FUNCTION TRY AGAIN")
              time.sleep(10)
          def MOVE_UP(self):
            new_head[0] -= 1
            last_movement.append([new_head[0],"-",0])
            if len(last_movement) == 2:
              del last_movement[0]
       
          def MOVE_LEFT(self):
            new_head[1] -= 1
            last_movement.append([new_head[1],"-",1])
            if len(last_movement) == 2:
              del last_movement[0]
              
          def MOVE_DOWN(self):
            new_head[0] += 1
            last_movement.append([new_head[0],"+",0])
            if len(last_movement) == 2:
              del last_movement[0]
              
          def MOVE_RIGHT(self):
            new_head[1] += 1
            last_movement.append([new_head[1],"+",1])
            if len(last_movement) == 2:
              del last_movement[0]
            
        #keybind
        move = Movement()
        if key == KEY_UP and not last_key == KEY_DOWN:
          move.MOVE_UP()
          last_key = key
        elif key == KEY_LEFT and not last_key == KEY_RIGHT:
          move.MOVE_LEFT()
          last_key = key
        elif key == KEY_DOWN and not last_key == KEY_UP:
          move.MOVE_DOWN()
          last_key = key
        elif key == KEY_RIGHT and not last_key == KEY_LEFT:
          move.MOVE_RIGHT()
          last_key = key 
        elif key == ord("p"):
          key = last_key
          raise KeyboardInterrupt
        else:
          move.LAST_MOVEMENT()
        snake_bod.insert(0,new_head)
        if snake_bod[0] == food:
          food = None
          score["Snake"] += 1
          while food is None:
            nf = [
              random.randint(1,sh-2),
              random.randint(1,sw-2)
              ]
            food = nf if nf not in snake_bod else None
          w.addch(food[0],food[1], "@", curses.color_pair(1))
        else:
          tail = snake_bod.pop()
          w.addch(tail[0],tail[1], ' ')
        logger.debug(f"User_input: {get_key}")
        logger.debug(f"snake_bod: {snake_bod}")
        logger.debug(f"Food: {food}")
        logger.debug(f"Tail: {tail}")
        try:
          w.addch(snake_bod[0][0],snake_bod[0][1],"@",curses.color_pair(2))
          w.addstr(sh-1,0,f'Score:{score["Snake"]}',curses.color_pair(3))
        except curses.error as e:
          error_border = True
        #Set snake speed
        time.sleep(0.05)
    except KeyboardInterrupt:
      message = 'Game Paused press "p" to continue'
      while True:
        francis = w.getch()
        w.addch(snake_bod[0][0],snake_bod[0][1],"@",curses.color_pair(2))
        w.addstr(sh-1,0,f'Score:{score["Snake"]}',curses.color_pair(3))
        w.addstr(sh-1,9,message,curses.color_pair(3))
        if francis == ord("p"):
          for num,text in enumerate(message):
            text = "-"
            w.addstr(sh-1,9+num,text,curses.color_pair(6))
          break
      
def Continue():
  global status
  print("Load previous game data")
  def Check_snake_validity(data):
    status = True
    if data[0][0] in [0,sh-1] or data[0][1] in [0,sw-1]:
      print("Death1")
      status = False
    if data[0] in data[1:]:
      print("Death2")
      status = False
    return(status)
  with open("Snake.log") as f:
    for marc in f:
      stripped = marc.strip()
      if "Window_size" in stripped:
        y = ""
        data = stripped.replace("Window_size: ","")
        sh = int(re.search("(\d+),",data)[1])
        sw = int(re.search(",(\d+)",data)[1])
      if "snake_bod" in stripped:
        data = stripped.replace("snake_bod: ","")
        snake_data = json.loads(data)
      if "Food" in stripped:
        data = stripped.replace("Food: ","")
        food_data = json.loads(data)
      if "last_movement" in stripped:
        data = stripped.replace("last_movement:","")
        new = ""
        for line in data:
          new += line.replace("'",'"')
        last_data = json.loads(new)
  try:      
    status = Check_snake_validity(snake_data)
  except UnboundLocalError:
    print("Error on file")
    time.sleep(2)
    status = False
  if status:
    global prev_snake
    global prev_food
    global prev_score
    global prev_lastmov
    global prev_sh,prev_sw
    prev_sh = sh
    prev_sw = sw
    prev_food = food_data
    prev_score = len(snake_data)-4
    prev_snake = snake_data
    prev_lastmov = last_data[0]
  elif not status:
    if os.path.isfile(os.path.join(os.getcwd(),"Snake.log")): os.remove("Snake.log")
try:
  Introduction()
  try:
    Continue()
  except FileNotFoundError:
    status = False
    print("Error on file Snake.log")
    time.sleep
  scr = curses.initscr()
  curses.noecho()
  curses.start_color()
  curses.curs_set(0) 
  returned = MainMenu()
  if not returned:
    if os.path.isfile(os.path.join(os.getcwd(),"Snake.log")): os.remove("Snake.log")
  elif returned:
    continue_render(prev_sh,prev_sw)
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.DEBUG)
  handler = logging.FileHandler("Snake.log")
  handler.setLevel(logging.DEBUG)
  logger.addHandler(handler)
  GameStart(returned)
finally:
  curses.endwin()
  
      
