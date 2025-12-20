import tkinter as tk
from tkinter import ttk
import random

from Đồ_án_trí_tuệ_nhân_tạo import sa_generator

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


WIDTH = 600
HEIGHT = 600
CITY_RADIUS = 4


class SAApp:
    def __init__(self, root):
        print(">>> ĐANG CHẠY GIAO_DIEN  <<<")
        self.root = root
        root.title("Simulated Annealing - TSP")

        # ===== STATE =====
        self.cities = []
        self.gen = None
        self.running = False
        self.iteration = 0
        self.delay = 50

        self.dist_history = []

        # ===== LAYOUT =====
        main_frame = tk.Frame(root)
        main_frame.pack()

        left = tk.Frame(main_frame)
        left.pack(side=tk.LEFT)

        right = tk.Frame(main_frame)
        right.pack(side=tk.RIGHT, padx=10)

        # ===== CANVAS MAP =====
        self.canvas = tk.Canvas(left, width=WIDTH, height=HEIGHT, bg="white")
        self.canvas.pack()

        # ===== STATS =====
        self.info = tk.Label(
            left,
            text="Iteration: 0 | Current: - | Best: - | Status: Idle"
        )
        self.info.pack()

        # ===== CONTROL PANEL =====
        panel = tk.Frame(right)
        panel.pack(pady=5)

        tk.Label(panel, text="Số thành phố").grid(row=0, column=0)
        self.entry_n = tk.Entry(panel, width=5)
        self.entry_n.grid(row=0, column=1)

        ttk.Button(panel, text="Generate", command=self.generate).grid(row=1, column=0, columnspan=2, sticky="ew")
        ttk.Button(panel, text="Start", command=self.start).grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Button(panel, text="Pause / Resume", command=self.toggle).grid(row=3, column=0, columnspan=2, sticky="ew")
        ttk.Button(panel, text="Reset", command=self.reset).grid(row=4, column=0, columnspan=2, sticky="ew")

        tk.Label(panel, text="Speed").grid(row=5, column=0)
        self.speed = tk.Scale(
            panel, from_=1, to=200, orient=tk.HORIZONTAL,
            command=self.update_speed
        )
        self.speed.set(50)
        self.speed.grid(row=5, column=1)

        # ===== MATPLOTLIB CHART =====
        self.fig = Figure(figsize=(4, 3))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Best Distance")
        self.ax.set_xlabel("Iteration")
        self.ax.set_ylabel("Distance")

        #tỰ ĐỘNG CĂN CHỈNH
        self.fig.tight_layout()

        self.chart = FigureCanvasTkAgg(self.fig, master=right)
        self.chart.get_tk_widget().pack()

    # ================= CORE =================
    def update_speed(self, val):
        self.delay = int(val)

    def reset(self):
        self.running = False
        self.gen = None
        self.iteration = 0
        self.cities.clear()
        self.dist_history.clear()

        self.canvas.delete("all")
        self.ax.clear()
        self.chart.draw()

        self.info.config(text="Iteration: 0 | Current: - | Best: - | Status: Reset")

    def generate(self):
        self.canvas.delete("all")
        self.cities.clear()

        try:
            n = int(self.entry_n.get())
        except:
            n = 10

        for _ in range(n):
            x = random.randint(40, WIDTH - 40)
            y = random.randint(40, HEIGHT - 40)
            self.cities.append((x, y))

        self.iteration = 0
        self.dist_history.clear()
        self.draw_cities()

        self.info.config(text=f"Generated {n} cities")

    def start(self):
        if len(self.cities) < 3:
            return

        self.gen = sa_generator(self.cities)
        self.running = True
        self.animate()

    def toggle(self):
        self.running = not self.running
        if self.running:
            self.info.config(text="Status: Running...")
            self.animate()
        else:
            self.info.config(text="Status: Paused")

    def animate(self):
        if not self.running:
            return

        try:
            current, best, curr_e, best_e = next(self.gen)
            self.iteration += 1

            self.draw_tour(current, "gray", "current")
            self.draw_tour(best, "red", "best")

            self.dist_history.append(best_e)
            self.update_chart()

            self.info.config(
                text=f"Iteration: {self.iteration} | "
                     f"Current: {curr_e:.2f} | "
                     f"Best: {best_e:.2f} | Running"
            )

            self.root.after(self.delay, self.animate)

        except StopIteration:
            self.running = False
            self.info.config(text="Status: Done")

    # ================= DRAW =================
    def draw_cities(self):
        for x, y in self.cities:
            self.canvas.create_oval(
                x - CITY_RADIUS, y - CITY_RADIUS,
                x + CITY_RADIUS, y + CITY_RADIUS,
                fill="black"
            )

    def draw_tour(self, tour, color, tag):
        self.canvas.delete(tag)
        for i in range(len(tour)):
            x1, y1 = self.cities[tour[i]]
            x2, y2 = self.cities[tour[(i + 1) % len(tour)]]
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                tags=tag,
                width=2
            )

    def update_chart(self):
        self.ax.clear()
        self.ax.plot(self.dist_history, color="red")
        self.ax.set_title("Best Distance")
        self.ax.set_xlabel("Iteration")
        self.ax.set_ylabel("Distance")

        self.fig.tight_layout()

        self.chart.draw()

