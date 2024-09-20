import curses
import traceback
if __name__ == "__main__":
  try:
    from ReplayGame import *
  finally:
    print(">>Launcher stop")
    try:
      curses.endwin()
    except curses.error:
      print("Endwin skipped")