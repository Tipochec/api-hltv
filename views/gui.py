import customtkinter as ctk
from database.db import get_connection
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Цвета
CLR_BG = "#1a1a2e"
CLR_CARD = "#16213e"
CLR_CARD2 = "#0f3460"
CLR_ACCENT = "#e94560"
CLR_TEXT = "#eaeaea"
CLR_MUTED = "#8892a4"
CLR_SUCCESS= "#4ecca3"


class MainWindow:
    def __init__(self):
        self.conn = get_connection()
        self.make_widget()
        

    def make_widget(self):
        app = ctk.CTk()
        app.title("CS2 Dashboard")
        app.geometry("700x500")
        app.configure(fg_color=CLR_BG)

        cursor = self.conn.cursor()
        matches = cursor.execute(
            """
            SELECT id, team1, team2, score1, score2, status, tournament, date
            FROM matchs
            """
        ).fetchall()
        
        for c in range(3):
            app.columnconfigure(index=c, weight=1)
        
        for index, match in enumerate(matches):
            match_id, team1, team2, score1, score2, status, tournament, date = match
            
            base_row = index * 5
        



            # ── Строка 0: "VS" по центру ──────────────────────────────
            vs_font = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
            ctk.CTkLabel(
                app, text="VS",
                font=vs_font,
                text_color=CLR_ACCENT
            ).grid(row=base_row, column=1)

            # ── Строка 1: команды и счёт ──────────────────────────────
            team_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
            score_font = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")

            # Команда 1
            
            ctk.CTkLabel(
                    app, text=f"{team1}",
                    font=team_font,
                    text_color=CLR_TEXT
                ).grid(row=base_row + 1,  column=0)

            # Счёт
            ctk.CTkLabel(
                app, text=f"{score1} : {score2}",
                font=score_font,
                text_color=CLR_SUCCESS
            ).grid(row=base_row + 1, column=1)

            # Команда 2
            ctk.CTkLabel(
                app, text=f"{team2}",
                font=team_font,
                text_color=CLR_TEXT
            ).grid(row=base_row + 1, column=2)

            # ── Строка 2: статус ──────────────────────────────────────
            ctk.CTkLabel(
                app, text=f"{status}",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=CLR_MUTED
            ).grid(row=base_row + 2, column=1)

            # ── Разделитель ───────────────────────────────────────────
            ctk.CTkFrame(
                app, height=1, fg_color=CLR_CARD2
            ).grid(row=base_row + 3, column=0, columnspan=3, sticky="ew", padx=20, pady=(30, 0))

            # ── Строка 3: турнир и дата ───────────────────────────────
            info_font = ctk.CTkFont(family="Segoe UI", size=11)

            ctk.CTkLabel(
                app, text=f"🏆{tournament}",
                font=info_font,
                text_color=CLR_MUTED,
                anchor="w"
            ).grid(row=base_row + 4, column=0, padx=10, sticky="w")

            ctk.CTkLabel(
                app, text=f"🕐 {date}",
                font=info_font,
                text_color=CLR_MUTED,
                anchor="e"
            ).grid(row=base_row + 4, column=2, padx=10, sticky="e")

        app.mainloop()


