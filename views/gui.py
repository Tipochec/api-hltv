import customtkinter as ctk
import requests
import threading
import queue
from io import BytesIO
from PIL import Image

from database.db import get_connection

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Цвета
CLR_BG      = "#1a1a2e"
CLR_CARD    = "#16213e"
CLR_CARD2   = "#0f3460"
CLR_ACCENT  = "#e94560"
CLR_TEXT    = "#eaeaea"
CLR_MUTED   = "#8892a4"
CLR_SUCCESS = "#4ecca3"

LOGO_SIZE = (40, 40)


class MainWindow:
    def __init__(self):
        self.conn = get_connection()
        self.queue = queue.Queue()  # ← добавь это
        self.make_widget()

    def load_image_async(self, url, label, app):
        def task():
            img = self.load_image(url)
            if img:
                self.queue.put((label, img))  # кладём в очередь
        threading.Thread(target=task, daemon=True).start()
        
    def load_image(self, url: str | None):
        if not url:
            return None
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            img_bytes = BytesIO(response.content)
            img_bytes.seek(0)
            pil_img = Image.open(img_bytes).convert("RGBA").resize(LOGO_SIZE, Image.LANCZOS)
            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=LOGO_SIZE)
        except Exception as e:
            print(f"[logo] {e}")
            return None

    def _process_queue(self, app):
        try:
            while True:
                label, img = self.queue.get_nowait()
                label.configure(image=img, text="")
        except queue.Empty:
            pass
        app.after(100, self._process_queue, app)

    def make_widget(self):
        app = ctk.CTk()
        app.title("CS2 Dashboard")
        app.geometry("700x500")
        app.resizable(False, False)
        app.configure(fg_color=CLR_BG)

        scroll = ctk.CTkScrollableFrame(app, fg_color=CLR_BG)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        cursor = self.conn.cursor()
        matches = cursor.execute(
            """
            SELECT id, team1, team2, logo1, logo2, score1, score2, status, tournament, date
            FROM matchs
            """
        ).fetchall()

        # ── Шрифты ───────────────────────────────────────────────
        vs_font     = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        team_font   = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        score_font  = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        info_font   = ctk.CTkFont(family="Segoe UI", size=11)
        status_font = ctk.CTkFont(family="Segoe UI", size=12)

        for c in range(3):
            scroll.columnconfigure(index=c, weight=1)

        for index, match in enumerate(matches):
            match_id, team1, team2, logo1, logo2, score1, score2, status, tournament, date = match

            base_row = index * 5

            # ── Строка 0: VS по центру ────────────────────────────
            ctk.CTkLabel(
                scroll, text="VS",
                font=vs_font,
                text_color=CLR_ACCENT
            ).grid(row=base_row, column=1)

            # ── Строка 1: логотип + команда | счёт | команда + логотип

            # Левая сторона
            left = ctk.CTkFrame(scroll, fg_color="transparent")
            left.grid(row=base_row + 1, column=0, sticky="e", padx=10)

            # Создаём пустой label для логотипа — картинка подгрузится позже
            logo1_label = ctk.CTkLabel(left, text="", width=40, height=40)
            logo1_label.pack(side="left", padx=(0, 6))
            if logo1:
                self.load_image_async(logo1, logo1_label, app)

            ctk.CTkLabel(
                left, text=team1,
                font=team_font,
                text_color=CLR_TEXT
            ).pack(side="left")

            # Счёт
            ctk.CTkLabel(
                scroll, text=f"{score1} : {score2}",
                font=score_font,
                text_color=CLR_SUCCESS
            ).grid(row=base_row + 1, column=1)

            # Правая сторона
            right = ctk.CTkFrame(scroll, fg_color="transparent")
            right.grid(row=base_row + 1, column=2, sticky="w", padx=10)

            ctk.CTkLabel(
                right, text=team2,
                font=team_font,
                text_color=CLR_TEXT
            ).pack(side="left")

            # Создаём пустой label для логотипа — картинка подгрузится позже
            logo2_label = ctk.CTkLabel(right, text="", width=40, height=40)
            logo2_label.pack(side="left", padx=(6, 0))
            if logo2:
                self.load_image_async(logo2, logo2_label, app)

            # ── Строка 2: статус ──────────────────────────────────
            ctk.CTkLabel(
                scroll, text=f"● {status}",
                font=status_font,
                text_color=CLR_MUTED
            ).grid(row=base_row + 2, column=1)

            # ── Разделитель ───────────────────────────────────────
            ctk.CTkFrame(
                scroll, height=2, fg_color=CLR_CARD2
            ).grid(row=base_row + 3, column=0, columnspan=3,
                   sticky="ew", padx=20, pady=(10, 10))

            # ── Строка 4: турнир и дата ───────────────────────────
            ctk.CTkLabel(
                scroll, text=f"🏆 {tournament}",
                font=info_font,
                text_color=CLR_MUTED,
                anchor="w"
            ).grid(row=base_row + 4, column=0, padx=10, sticky="w")

            ctk.CTkLabel(
                scroll, text=f"🕐 {date}",
                font=info_font,
                text_color=CLR_MUTED,
                anchor="e"
            ).grid(row=base_row + 4, column=2, padx=10, sticky="e")
        app.after(100, self._process_queue, app)
        app.mainloop()