import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import time

from utils.tracker import track_pendulum
from utils.plotting import save_and_plot
from utils.config import CAMERA_INDEX, DEFAULT_DURATION

class PenduloApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MOFT - Pêndulo Físico")

        self.duration = DEFAULT_DURATION
        self.running = False
        self.start_time = None

        self.app_running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # GUI Elements
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)

        self.label = tk.Label(input_frame, text="Tempo (s):")
        self.label.pack(side=tk.LEFT)

        self.entry = tk.Entry(input_frame, width=5)
        self.entry.insert(0, str(DEFAULT_DURATION))
        self.entry.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(input_frame, text="Iniciar", command=self.start_tracking)
        self.start_button.pack(side=tk.LEFT)

        self.timer_label = tk.Label(root, text="")
        self.timer_label.pack()

        self.video_label = tk.Label(root)
        self.video_label.pack()

        # Dados do experimento
        self.positions = []
        self.timestamps = []
        self.periods = []
        self.center_x_reference = None
        self.last_side = None
        self.crossed_center_time = None
        self.period_count = 0
        self.amplitude_data = []

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.update_frame()

    def on_closing(self):
        self.app_running = False
        cv2.destroyAllWindows()
        self.cap.release()
        self.root.destroy()

    def start_tracking(self):
        try:
            self.duration = int(self.entry.get())
            if self.duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Insira um valor válido maior que zero.")
            return

        self.running = True
        self.start_time = time.time()

        self.positions.clear()
        self.timestamps.clear()
        self.periods.clear()
        self.center_x_reference = None
        self.last_side = None
        self.crossed_center_time = None
        self.period_count = 0
        self.amplitude_data.clear()

        print("Experimento iniciado...")

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            self.display_frame = frame.copy()

            if self.running:
                elapsed = time.time() - self.start_time
                remaining = max(0, int(self.duration - elapsed))
                self.timer_label.config(text=f"Timer: {remaining}s")

                if elapsed >= self.duration:
                    self.running = False
                    self.timer_label.config(text="Finalizado.")
                    save_and_plot(self.positions, self.periods)
                    self.print_data()
                else:
                    track_pendulum(self, frame)

            rgb = cv2.cvtColor(self.display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        if self.app_running:
            self.root.after(10, self.update_frame)

    def print_data(self):
        print("Dados do experimento:")
        print(f"Tempo total: {self.duration} segundos")
        print(f"Períodos registrados: {len(self.periods)}")
