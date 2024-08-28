import os
import sys
from watchdog.events import FileSystemEventHandler
from .colors import printc

class RestartHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback

    def on_any_event(self, event):
        # Clear terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        self.restart_callback()

class Verbose:
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def debug(self, msg, color='blue'):
        if self.verbose:
            printc(f'[DEBUG] {msg}', color)