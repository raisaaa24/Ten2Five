import tkinter as tk
import time
import math
import random

LYRICS = [
    (0,   "Hanya Untuk-Mu -Ten2Five"),
    (22,  "Inikah rasanya"),
    (25,  "Bila 'ku sedang jatuh cinta"),
    (33,  "Setiap hela nafasku bahagia"),
    (44,  "Mengenal hatimu"),
    (47,  "Hadirkan indahnya dunia"),
    (55,  "Kau bawa irama cinta di jiwa"),
    (67,  "Semua yang kumau"),
    (69,  "Hanyalah dirimu satu"),
    (78,  "Kaulah jawaban semua doa"),
    (89,  "Semua yang kurasa"),
    (92,  "Rindu dalam asa, di dekap cinta"),
    (101,  "Hatiku untukmu"),
]

BOX_W, BOX_H = 300, 250
FONT = ("Helvetica", 22, "bold")
BG_COLOR = "#FF9898"
FG_COLOR = "#2A8A37"
RISE_SPEED = 25
BOTTOM_SPAWN_OFFSET = 150

LOVE_CHARS = ["♡", "❤"]
LOVE_CHARS_SIZES = [22, 26]
LOVE_CHARS_COLORS = ["#2A8A37", "#FF6262"]
LOVE_MIN_SPAWN_GAP = 0.4
LOVE_MAX_SPAWN_GAP = 0.9
LOVE_SPEED_RANGE = (15, 25)
LOVE_WOBBLE_AMP_RANGE = (8, 20)
LOVE_WOBBLE_FREQ_RANGE = (0.7, 1.5)
LOVE_SPAWN_TAIL_BUFFER = 8

class LyricCard:
    def __init__(self, parent, text, x, y):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BG_COLOR)  # RED CARD
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}")
        self.win.resizable(False, False)

        self.full_text = text

        self.label = tk.Label(
            self.win, text="", font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            wraplength=BOX_W - 25, justify="center"
        )
        self.label.pack(expand=True, fill="both", padx=15, pady=15)

        self.typewriter_index = 0
        self.typewriter()

        self.x = x
        self.y = float(y)

    def rise(self, dy):
        self.y -= dy
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}")

    def is_offscreen(self):
        return self.y + BOX_H < -50

    def typewriter(self):
        if self.typewriter_index <= len(self.full_text):
            self.label.config(text=self.full_text[:self.typewriter_index])
            self.typewriter_index += 1
            self.win.after(100, self.typewriter)

class MusicNote:
    def __init__(self, parent, screen_w, screen_h):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)

        try:
            self.win.attributes("-transparentcolor", "#000000")
        except tk.TclError:
            pass
        try:
            self.win.attributes("-alpha", 0.88)
        except tk.TclError:
            pass

        # LOVE STYLE
        char = random.choice(LOVE_CHARS)
        size = random.choice(LOVE_CHARS_SIZES)
        color = random.choice(LOVE_CHARS_COLORS)

        self.win.configure(bg="#000000")

        label = tk.Label(
            self.win, text=char, font=("Helvetica", size, "bold"),
            bg="#000000", fg=color
        )
        label.pack(padx=3, pady=3)

        self.screen_h = screen_h
        self.base_x = random.uniform(10, max(10, screen_w - 60))
        self.y = float(screen_h + random.uniform(0, 120))

        self.spawn_time = time.time()
        self.wobble_phase = random.uniform(0, math.tau)
        self.wobble_freq = random.uniform(*LOVE_WOBBLE_FREQ_RANGE)
        self.wobble_amp = random.uniform(*LOVE_WOBBLE_AMP_RANGE)
        self.speed = random.uniform(*LOVE_SPEED_RANGE)


        self._update_pos()

    def _update_pos(self):
        t = time.time() - self.spawn_time
        x = self.base_x + math.sin(t * self.wobble_freq + self.wobble_phase) * self.wobble_amp
        self.win.geometry(f"+{int(x)}+{int(self.y)}")

    def rise(self, dt):
            self.y -= self.speed * dt
            self._update_pos()

    def is_offscreen(self):
        return self.y < -60

    def destroy(self):
        try:
            self.win.destroy()
        except tk.TclError:
            pass

class LyricFloatApp:
    def __init__(self, root):
        self.root = root
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()

        self.next_lyric_idx = 0
        self.boxes = []
        self.last_frame_time = None
        self.current_side = "left"

        self.love = []
        self.next_love_spawn_time = 0.0
        self.last_lyric_time = LYRICS[-1][0] if LYRICS else 0
        self.start()

    def random_safe_x(self):
        center_x = self.screen_w // 2
        spacing = BOX_W + 60
        left_x = center_x - spacing
        right_x = center_x + 60

        if self.current_side == "left":
            self.current_side = "right"
            return left_x
        else:
            self.current_side = "left"
            return right_x

    def start(self):
        self.root.iconify()
        self.start_time = time.time()
        self.last_frame_time = self.start_time
        self.next_love_spawn_time = self.start_time + random.uniform(LOVE_MIN_SPAWN_GAP, LOVE_MAX_SPAWN_GAP)
        
        self.tick()

    def _maybe_spawn_love(self,now, elapsed):
        if self.next_lyric_idx < len(LYRICS):
            pass
        elif self.boxes:
            pass
        else:
            return
        
        if now >= self.next_love_spawn_time:
            heart = MusicNote(self.root, self.screen_w, self.screen_h)
            self.love.append(heart)
            self.next_love_spawn_time = now + random.uniform (
                LOVE_MIN_SPAWN_GAP,
                LOVE_MAX_SPAWN_GAP
                )
            

    def tick(self):
        now = time.time()
        elapsed = now - self.start_time
        dt = now - self.last_frame_time
        self.last_frame_time = now
        self._maybe_spawn_love(now, elapsed)

        while (self.next_lyric_idx < len(LYRICS)
               and LYRICS[self.next_lyric_idx][0] <= elapsed):
            t, text = LYRICS[self.next_lyric_idx]

            if self.next_lyric_idx == 0:
                x = (self.screen_w - BOX_W) // 2
                
            else:
                x = self.random_safe_x()
                
            y = self.screen_h - BOX_H - BOTTOM_SPAWN_OFFSET

            box = LyricCard(self.root, text, x, y)
            self.boxes.append(box)
            self.next_lyric_idx += 1 

        dy = RISE_SPEED * dt
        for box in self.boxes:
            box.rise(dy)

        still_visible = []
        for box in self.boxes:
            if box.is_offscreen():
                try:
                    box.win.destroy()
                except tk.TclError:
                    pass
            else:
                still_visible.append(box)
        self.boxes = still_visible

        for love in self.love:
            love.rise(dt)

        still_floating_notes = []

        for heart in self.love:
            if heart.is_offscreen():
                heart.destroy()
            else:
                still_floating_notes.append(heart)
        self.love = still_floating_notes

        if self.next_lyric_idx < len(LYRICS) or self.boxes or self.love:
            self.root.after(16, self.tick)

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()