import os
import sys
import time
import datetime


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
        print("\033c", end="")
    else:
        os.system("clear")
        print("\033c", end="")


def draw_file(ascii_file):
    """prints a text file to screen"""
    with open(ascii_file, 'r', newline='\n') as draw_file:
        temp = [line.rstrip('\n') for line in draw_file]
        for strip in temp:
            strip.rstrip('\n')
            print(strip)


def my_exit():
    """clears screen and display ascii image before exiting"""
    clear_screen()
    draw_file("getbacktowork.txt")
    sys.exit()

