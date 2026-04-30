import customtkinter as ctk
import requests
import threading
import queue
from io import BytesIO
from PIL import Image
from datetime import datetime, timezone, timedelta

from database.db import get_connection, filling_table

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
        self.queue = queue.Queue()
        self.scroll = None
        self.app = None
        self.make_widget()

    # ── Загрузка картинок ─────────────────────────────────────────

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

    def load_image_async(self, url, label):
        def task():
            img = self.load_image(url)
            if img:
                self.queue.put((label, img))
        threading.Thread(target=task, daemon=True).start()

    def _process_queue(self):
        try:
            while True:
                label, img = self.queue.get_nowait()
                label.configure(image=img, text="")
        except queue.Empty:
            pass
        self.app.after(100, self._process_queue)

    def _load_default(self, label):
        try:
            default = Image.open("data/defolt_logo_team.png").resize(LOGO_SIZE, Image.LANCZOS)
            default_img = ctk.CTkImage(light_image=default, dark_image=default, size=LOGO_SIZE)
            label.configure(image=default_img)
        except Exception:
            pass

    # ── Форматирование даты ───────────────────────────────────────

    def format_date(self, date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        dt = dt.replace(tzinfo=timezone.utc) + timedelta(hours=7)
        return dt.strftime("%d/%m/%Y, %H:%M")

    # ── Построение карточек ───────────────────────────────────────

    def build_matches(self):
        # Удаляем старый scroll если есть
        for widget in self.scroll.winfo_children():
            widget.destroy()

        conn = get_connection()
        cursor = conn.cursor()
        matches = cursor.execute(
            """
            SELECT team1, team2, logo1, logo2, score1, score2, status, tournament, date
            FROM matchs
            """
        ).fetchall()
        conn.close()

        # Шрифты
        vs_font     = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        team_font   = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        score_font  = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        info_font   = ctk.CTkFont(family="Segoe UI", size=11)
        status_font = ctk.CTkFont(family="Segoe UI", size=12)

        for c in range(3):
            self.scroll.columnconfigure(index=c, weight=1)

        for index, match in enumerate(matches):
            team1, team2, logo1, logo2, score1, score2, status, tournament, date = match
            base_row = index * 5

            # VS
            ctk.CTkLabel(
                self.scroll, text="VS",
                font=vs_font, text_color=CLR_ACCENT
            ).grid(row=base_row, column=1, pady=(10, 0))

            # Левая сторона
            left = ctk.CTkFrame(self.scroll, fg_color="transparent")
            left.grid(row=base_row + 1, column=0, sticky="e", padx=10)

            logo1_label = ctk.CTkLabel(left, text="", width=40, height=40)
            logo1_label.pack(side="left", padx=(0, 6))
            if logo1:
                self.load_image_async(logo1, logo1_label)
            else:
                self._load_default(logo1_label)

            ctk.CTkLabel(
                left, text=team1,
                font=team_font, text_color=CLR_TEXT
            ).pack(side="left")

            # Счёт
            ctk.CTkLabel(
                self.scroll, text=f"{score1} : {score2}",
                font=score_font, text_color=CLR_SUCCESS
            ).grid(row=base_row + 1, column=1)

            # Правая сторона
            right = ctk.CTkFrame(self.scroll, fg_color="transparent")
            right.grid(row=base_row + 1, column=2, sticky="w", padx=10)

            ctk.CTkLabel(
                right, text=team2,
                font=team_font, text_color=CLR_TEXT
            ).pack(side="left")

            logo2_label = ctk.CTkLabel(right, text="", width=40, height=40)
            logo2_label.pack(side="left", padx=(6, 0))
            if logo2:
                self.load_image_async(logo2, logo2_label)
            else:
                self._load_default(logo2_label)

            # Статус
            ctk.CTkLabel(
                self.scroll, text=f"● {status}",
                font=status_font, text_color=CLR_MUTED
            ).grid(row=base_row + 2, column=1)

            # Турнир и дата
            ctk.CTkLabel(
                self.scroll, text=f"🏆 {tournament}",
                font=info_font, text_color=CLR_MUTED, anchor="w"
            ).grid(row=base_row + 3, column=0, padx=10, sticky="w")

            ctk.CTkLabel(
                self.scroll, text=f"🕐 {self.format_date(date)}",
                font=info_font, text_color=CLR_MUTED, anchor="e"
            ).grid(row=base_row + 3, column=2, padx=10, sticky="e")

            # Разделитель
            ctk.CTkFrame(
                self.scroll, height=2, fg_color=CLR_CARD2
            ).grid(row=base_row + 4, column=0, columnspan=3,
                   sticky="ew", padx=20, pady=(10, 0))

    # ── Обновление ────────────────────────────────────────────────

    def refresh(self):
        filling_table()
        self.build_matches()

    # ── Главное окно ──────────────────────────────────────────────

    def make_widget(self):
        self.app = ctk.CTk()
        self.app.title("CS2 Dashboard")
        self.app.geometry("700x500")
        self.app.resizable(False, False)
        self.app.configure(fg_color=CLR_BG)

        # Кнопка обновить
        ctk.CTkButton(
            self.app,
            text="🔄 Обновить",
            command=self.refresh
        ).pack(side="top", pady=10)
        self.scroll = ctk.CTkScrollableFrame(self.app, fg_color=CLR_BG)
        self.scroll.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 10))
        self.build_matches()
        self.app.after(100, self._process_queue)
        self.app.mainloop()