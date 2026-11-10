import tkinter as tk
import os

#Import musik
try:
    import winsound
except ImportError:
    winsound = None

# Kelas dasar untuk semua benda di game (bola, paddle, brick)
class GameObject(object):
    def init(self, canvas, item):
        self.canvas = canvas
        self.item = item

    # Mengambil posisi benda [x1, y1, x2, y2]
    def get_position(self):
        return self.canvas.coords(self.item)

    # Menggeser benda sejauh x dan y
    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    # Menghapus benda dari canvas
    def delete(self):
        self.canvas.delete(self.item)

