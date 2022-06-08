import pyautogui
import time
import os

SECS_BETWEEN_KEYPRESSES = 0.07
SECS_BETWEEN_COMMANDS = 1.0

# file path that the asciinema script is located
asciinema_script = "cli.txt"

os.system("open /Applications/iTerm.app")
time.sleep(3)  # time to open terminal window

# clear screen
pyautogui.write("clear")
pyautogui.press("enter")

# start recording the terminal window
# pyautogui.write("asciinema rec", interval=SECS_BETWEEN_KEYPRESSES)
# pyautogui.press("enter")
# time.sleep(SECS_BETWEEN_COMMANDS)

# read and type the file line by line and strip trailing whitespace
with open(asciinema_script, "r") as f:
    lines = f.readlines()
    for line in lines:
        if line.strip() == "":
            pyautogui.press("enter")
        else: 
            pyautogui.write(line.strip(), interval=SECS_BETWEEN_KEYPRESSES)
            pyautogui.press("enter")
        if "nmap" in line: # nmap command takes a long time to run
            time.sleep(45)
        elif "pip install" in line: # pip install command takes a long time to run
            time.sleep(3)
        elif "censys search" in line: # censys search command takes a long time to run
            time.sleep(5)
        else: 
            time.sleep(SECS_BETWEEN_COMMANDS)

# stop recording
pyautogui.write("exit", interval=SECS_BETWEEN_KEYPRESSES)
pyautogui.press("enter")
time.sleep(SECS_BETWEEN_COMMANDS)
