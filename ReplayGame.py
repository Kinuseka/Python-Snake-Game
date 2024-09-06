import curses
import json
import time
import sys
import os
import re
snake_movement = []
score = []
food_pos = []
class Collector:
  def GetWindowData(data):
    data = data.replace("Window_size: ","")
    matches = re.findall(r'\d+', data)
    sh = int(matches[0])
    sw = int(matches[1])
    return(sh,sw)
  def ListSnakeBody(data):
    data = data.replace("snake_bod: ","")
    data = json.loads(data)
    snake_movement.append(data)
  def FoodPosition(data):
    data = data.replace("Food: ","")
    data = json.loads(data)
    food_pos.append(data)
    
print("Collecting data please wait...")
with open("Snake.log","r") as file:
  Collect = Collector
  for i, line in enumerate(file):
    print(f"Collected: {i+1}", end="\r")
    stripped = line.strip()
    if "Window_size" in stripped:
      sh,sw = Collect.GetWindowData(stripped)
    if "snake_bod" in stripped:
      Collect.ListSnakeBody(stripped)
    if "Food" in stripped:
      Collect.FoodPosition(stripped)
score.append(len(snake_movement[len(snake_movement)-1])-4)
ctsw,ctsh = os.get_terminal_size()
print("DATA PARSED WITHOUT ERROR")
def Menu():
  global rate_limit_value
  print("Snake.log Terminal data:")
  print(f"Window size: {sw}, {sh}")
  print(f"Your terminal size: {ctsw}, {ctsh}")
  

  print("Snake.log replay data:")
  print(f"Total score: {score[0]}")
  print(f"Total actions: {len(snake_movement)}")
  print(f"Food data collected: {len(food_pos)}")
  a = input("START REPLAY?(Y/N)").strip().lower()
  if a == "y":
    print("""
    1.) Action/1s
    2.) Action/0.5s
    3.) Action/0.1s
    4.) Action/0.01s
    5.) Action/LOOP (aka No Limiter)
    """)
    while True:
      a = input("Set speed:")
      if a == "1":
        rate_limit_value = 1
        break
      elif a == "2":
        rate_limit_value = 0.5
        break
      elif a == "3":
        rate_limit_value = 0.1
        break
      elif a == "4":
        rate_limit_value = 0.01
        break
      elif a == "5":
        rate_limit_value = 0
        break
    return 0
  else:
    sys.exit()
Menu()
#Adjust screen
screen = curses.initscr()
#curses.curs_set(0) 
curses.noecho()
curses.cbreak()
csh,csw = screen.getmaxyx()
while not csh >= sh and not csw >= sw:
  csh,csw = screen.getmaxyx()
  screen.addstr(0,0,"THE SIZE OF YOUR WINDOW IS SMALLER")
  screen.addstr(1,0,"THAN THE GIVEN WINDOW! PLEASE RESIZE!")
  screen.addstr(2,0,"Windows/Linux: Drag the outer box")
  screen.addstr(3,0,"Android(Termux): Pinch your terminal outwards")
  screen.refresh()
  time.sleep(1)
curses.endwin()
scr = curses.initscr()
curses.noecho()
curses.cbreak()
w = curses.newwin(sh,sw,0,0)
w.keypad(1)
w.timeout(100)
w.border('|', '|', '-', '-', '+', '+', '+', '+')
curses.start_color()
if curses.has_colors():
  curses.use_default_colors()
  curses.init_pair(1, curses.COLOR_RED,curses.COLOR_RED)
  curses.init_pair(2, curses.COLOR_WHITE,curses.COLOR_WHITE)
  curses.init_pair(3, curses.COLOR_WHITE,curses.COLOR_RED)
  curses.init_pair(4, curses.COLOR_BLACK,curses.COLOR_WHITE)
  curses.init_pair(5, curses.COLOR_BLACK,curses.COLOR_BLUE)
curses.curs_set(0) 
curses.noecho()
score_em = {"Snake":0}
for num,snake_pos in enumerate(snake_movement):
  food = food_pos[num] 
  w.addch(food[0],food[1], "@", curses.color_pair(1))
  snake_bod = snake_pos 
  score_em = len(snake_movement[num])-4
  tail = snake_bod.pop()
  w.addch(tail[0],tail[1], ' ')
  try:
    w.addch(snake_bod[0][0],snake_bod[0][1],"@",curses.color_pair(5))
    w.addch(snake_bod[1][0],snake_bod[1][1],"@",curses.color_pair(2))
    w.addstr(sh-1,0,f'Score:{score_em}',curses.color_pair(3))
    w.addstr(sh-1,10,f'Actions:{num}/{len(snake_movement)}',curses.color_pair(5))
  except curses.error as e:
    curses.endwin()
    print("Error occured, Replay Over!")
    sys.exit()
  time.sleep(rate_limit_value)
  w.refresh()
  
curses.endwin()
print("GAME OVER")