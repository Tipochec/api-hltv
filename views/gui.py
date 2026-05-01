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
        self.search_after_id = None
        # NEW: полный список матчей
        self.all_matches = []
        self.image_cache = {}
        # NEW: поле поиска
        self.search_entry = None

        self.make_widget()

    # ── Загрузка картинок ─────────────────────────────────────────

    def load_image(self, url: str | None):
        if not url:
            return None

        if url in self.image_cache:
            return self.image_cache[url]

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            img_bytes = BytesIO(response.content)
            pil_img = Image.open(img_bytes).convert("RGBA").resize(LOGO_SIZE, Image.LANCZOS)

            ctk_img = ctk.CTkImage(
                light_image=pil_img,
                dark_image=pil_img,
                size=LOGO_SIZE
            )

            self.image_cache[url] = ctk_img
            return ctk_img

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

                if label.winfo_exists():
                    label.configure(image=img, text="")
                    label.image = img  # защита от garbage collector

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

    # ── Получение матчей из БД ────────────────────────────────────

    def delayed_search(self, event=None):
        if self.search_after_id:
            self.app.after_cancel(self.search_after_id)

        self.search_after_id = self.app.after(300, self.on_search)
    
    def fetch_matches(self):
        conn = get_connection()
        cursor = conn.cursor()

        matches = cursor.execute(
            """
            SELECT team1, team2, logo1, logo2, score1, score2, status, tournament, date
            FROM matchs
            """
        ).fetchall()

        conn.close()
        return matches

    # ── Поиск ─────────────────────────────────────────────────────

    def on_search(self, event=None):
        search_text = self.search_entry.get().lower().strip()

        if not search_text:
            filtered_matches = self.all_matches
        else:
            filtered_matches = [
                match for match in self.all_matches
                if search_text in (match[0] or "").lower()   # team1
                or search_text in (match[1] or "").lower()   # team2
                or search_text in (match[7] or "").lower()   # tournament
            ]

        self.display_matches(filtered_matches)

    # ── Построение карточек ───────────────────────────────────────

    def build_matches(self):
        # Загружаем все матчи
        self.all_matches = self.fetch_matches()

        # Показываем все
        self.display_matches(self.all_matches)

    # ── Отображение матчей ────────────────────────────────────────

    def display_matches(self, matches):
        # Удаляем старые виджеты
        for widget in self.scroll.winfo_children():
            widget.destroy()

        # Если ничего не найдено
        if not matches:
            ctk.CTkLabel(
                self.scroll,
                text="Ничего не найдено",
                text_color=CLR_MUTED,
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=30)
            return

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
                self.scroll,
                text="VS",
                font=vs_font,
                text_color=CLR_ACCENT
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
                left,
                text=team1,
                font=team_font,
                text_color=CLR_TEXT
            ).pack(side="left")

            # Счёт
            ctk.CTkLabel(
                self.scroll,
                text=f"{score1} : {score2}",
                font=score_font,
                text_color=CLR_SUCCESS
            ).grid(row=base_row + 1, column=1)

            # Правая сторона
            right = ctk.CTkFrame(self.scroll, fg_color="transparent")
            right.grid(row=base_row + 1, column=2, sticky="w", padx=10)

            ctk.CTkLabel(
                right,
                text=team2,
                font=team_font,
                text_color=CLR_TEXT
            ).pack(side="left")

            logo2_label = ctk.CTkLabel(right, text="", width=40, height=40)
            logo2_label.pack(side="left", padx=(6, 0))

            if logo2:
                self.load_image_async(logo2, logo2_label)
            else:
                self._load_default(logo2_label)

            # Статус
            ctk.CTkLabel(
                self.scroll,
                text=f"● {status}",
                font=status_font,
                text_color=CLR_MUTED
            ).grid(row=base_row + 2, column=1)

            # Турнир
            ctk.CTkLabel(
                self.scroll,
                text=f"🏆 {tournament}",
                font=info_font,
                text_color=CLR_MUTED,
                anchor="w"
            ).grid(row=base_row + 3, column=0, padx=10, sticky="w")

            # Дата
            ctk.CTkLabel(
                self.scroll,
                text=f"🕐 {self.format_date(date)}",
                font=info_font,
                text_color=CLR_MUTED,
                anchor="e"
            ).grid(row=base_row + 3, column=2, padx=10, sticky="e")

            # Разделитель
            ctk.CTkFrame(
                self.scroll,
                height=2,
                fg_color=CLR_CARD2
            ).grid(
                row=base_row + 4,
                column=0,
                columnspan=3,
                sticky="ew",
                padx=20,
                pady=(10, 0)
            )

    # ── Обновление ────────────────────────────────────────────────

    def refresh(self):
        filling_table()
        self.build_matches()

        # NEW: сохраняем поиск после обновления
        self.on_search()

    # ── Главное окно ──────────────────────────────────────────────

    def make_widget(self):
        self.app = ctk.CTk()
        self.app.title("CS2 Dashboard")
        self.app.geometry("700x550")
        self.app.resizable(False, False)
        self.app.configure(fg_color=CLR_BG)

        # Верхняя панель
        top_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        top_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))

        # Кнопка обновить
        ctk.CTkButton(
            top_frame,
            text="🔄 Обновить",
            command=self.refresh,
            width=120
        ).pack(side="left", padx=(0, 10))

        # NEW: Поиск
        self.search_entry = ctk.CTkEntry(
            top_frame,
            placeholder_text="Поиск по команде или турниру..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True)

        self.search_entry.bind("<KeyRelease>", self.delayed_search)

        # Скролл
        self.scroll = ctk.CTkScrollableFrame(
            self.app,
            fg_color=CLR_BG
        )
        self.scroll.pack(
            side="top",
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        self.build_matches()
        self.app.after(100, self._process_queue)
        self.app.mainloop()