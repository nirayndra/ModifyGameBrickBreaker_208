import tkinter as tk
import os

#Import musik
try:
    import winsound
except ImportError:
    winsound = None