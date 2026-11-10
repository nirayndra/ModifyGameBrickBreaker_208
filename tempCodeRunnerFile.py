import tkinter as tk


# Kelas dasar untuk semua benda di game (bola, paddle, brick)
class GameObject(object):
    def __init__(self, canvas, item):
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
    def __init__(self, canvas, x, y):
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
    # Sekarang fungsi ini mengembalikan poin yang didapat
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
    def __init__(self, canvas, x, y):
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


class Brick(GameObject):
    # Warna brick: 2 hit = biru, 1 hit = putih
    # (brick biru kena sekali berubah jadi putih, kena lagi hancur)
    COLORS = {1: 'white', 2: '#3498db', 3: '#222222'}

    def __init__(self, canvas, x, y, hits):
        # Ukuran brick dibuat sama (30x30) supaya jadi bulat sempurna
        self.width = 30
        self.height = 30
        self.hits = hits
        color = Brick.COLORS[hits]
        # create_oval = bentuk bulat (sebelumnya create_rectangle = kotak)
        item = canvas.create_oval(x - self.width / 2,
                                  y - self.height / 2,
                                  x + self.width / 2,
                                  y + self.height / 2,
                                  fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    # Dipanggil tiap brick kena bola
    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0  # skor awal
        self.width = 610
        self.height = 400
        # Latar belakang diganti jadi hitam
        self.canvas = tk.Canvas(self, bg='black',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle
        # Baris atas 2 hit (biru), dua baris bawah 1 hit (putih)
        # Jarak antar-brick disesuaikan dengan ukuran brick bulat yang baru
        for x in range(5, self.width - 5, 38):
            self.add_brick(x + 19, 50, 2)
            self.add_brick(x + 19, 85, 1)
            self.add_brick(x + 19, 120, 1)

        self.hud = None        # teks nyawa
        self.score_hud = None  # teks skor
        self.update_score_text()
        self.setup_game()
        self.canvas.focus_set()
        # Gerakan paddle yang smooth: catat tombol yang sedang DITEKAN,
        # lalu paddle digerakkan terus selama tombol masih ditahan
        self.keys = set()
        self.canvas.bind('<KeyPress-Left>', lambda _: self.keys.add('Left'))
        self.canvas.bind('<KeyRelease-Left>', lambda _: self.keys.discard('Left'))
        self.canvas.bind('<KeyPress-Right>', lambda _: self.keys.add('Right'))
        self.canvas.bind('<KeyRelease-Right>', lambda _: self.keys.discard('Right'))
        self.paddle_loop()

    # Dijalankan terus-menerus (tiap 16 ms, sekitar 60x per detik)
    # supaya paddle langsung bergerak begitu tombol ditekan, tanpa jeda
    def paddle_loop(self):
        if 'Left' in self.keys:
            self.paddle.move(-4)  # kecepatan paddle (makin kecil = makin lambat)
        if 'Right' in self.keys:
            self.paddle.move(4)
        self.after(16, self.paddle_loop)

    # Menyiapkan bola baru dan menunggu pemain menekan Space
    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200,
                                   'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    # Menulis teks di canvas. Warna teks dibuat putih supaya terlihat di latar hitam
    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font, fill='white')

    def update_lives_text(self):
        text = 'Nyawa: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    # Menampilkan/memperbarui skor di pojok kanan atas
    def update_score_text(self):
        text = 'Total Score: %s' % self.score
        if self.score_hud is None:
            self.score_hud = self.draw_text(550, 20, text, 12)
        else:
            self.canvas.itemconfig(self.score_hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    # Perulangan utama game (jalan tiap 16 ms, sebelumnya 50 ms)
    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            # Semua brick habis = menang
            self.ball.speed = None
            self.draw_text(300, 200, 'You win!')
        elif self.ball.get_position()[3] >= self.height:
            # Bola jatuh = nyawa berkurang
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                # Tulisan saat kalah (nyawa habis)
                self.draw_text(300, 200, 'seporsi kekalahan.')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(16, self.game_loop)

    # Cek bola menabrak apa, lalu tambahkan skor dari brick yang kena
    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        points = self.ball.collide(objects)
        if points > 0:
            self.score += points
            self.update_score_text()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Hello, Jarvis!')
    game = Game(root)
    game.mainloop()