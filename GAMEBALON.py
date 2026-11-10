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


class Ball(GameObject):
    def init(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 2  # kecepatan bola (makin kecil = makin lambat)
        # Warna bola diganti jadi pink
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='#ff69b4')
        super(Ball, self).__init__(canvas, item)

    # Menggerakkan bola dan memantulkannya kalau kena dinding
    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    # Mengatur pantulan bola saat menabrak paddle/brick
    # Fngsi ini mengembalikan poin yang didapat
    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        points = 0  # poin yang didapat di tabrakan ini
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()
                points += 10  # setiap brick yang kena = 10 poin
        return points

class Paddle(GameObject):
    def init(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='yellow')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    # Menggeser paddle (dan bola kalau belum dilepas), tidak boleh keluar layar
    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)