import webbrowser
from tkinter import BooleanVar, StringVar, filedialog

import customtkinter as ctk

from src.makerelease import MakeRelease, SearchCancelled, constants

REPO_URL = "https://github.com/c137ricksanchez/makerelease"

# Spaziatura orizzontale comune ai blocchi principali
PAD_X = 24
# Spaziatura interna alla card
CARD_PAD = 18

# Lingue disponibili nel selettore in alto a destra
LANGUAGES = ("IT", "EN")
DEFAULT_LANG = "IT"

# Valori interni dei tipi di release (NON tradurre: sono usati da MakeRelease)
RELEASE_VALUES = ("movie", "movie_folder", "tv_episode", "tv_single", "tv_multi")

# Tabella delle traduzioni: per aggiungere una lingua basta una nuova voce qui
TR = {
    "IT": {
        "subtitle": "Generatore di release per forum P2P",
        "section_type": "TIPO DI RELEASE",
        "section_template": "TEMPLATE",
        "all_templates": "Tutti i template",
        "section_path": "FILE / CARTELLA",
        "section_options": "OPZIONI (FACOLTATIVE)",
        "select_path": "📁  Seleziona percorso",
        "change_path": "📁  Cambia percorso",
        "no_path": "Nessun percorso selezionato",
        "rename": "Rinomina il file",
        "crew_label": "Nome della crew",
        "tmdb_label": "ID TheMovieDB (es. 27205)",
        "make_release": "Crea release!",
        "authors": "Autori: RickSanchez & Norman",
        "updates": "Controlla aggiornamenti ↗",
        "tmdb_dialog_title": "Seleziona il titolo",
        "tmdb_results": "Più risultati trovati su TheMovieDB — scegli quello corretto:",
        "tmdb_none": "Nessun risultato trovato su TheMovieDB.",
        "tmdb_manual": "...oppure inserisci manualmente un ID TMDB:",
        "confirm": "Conferma",
        "cancel": "Annulla",
        "cancelled_msg": "Operazione annullata: nessun titolo selezionato.",
        "types": {
            "movie": "Film (file)",
            "movie_folder": "Film (cartella)",
            "tv_episode": "Serie TV (episodio singolo)",
            "tv_single": "Serie TV (stagione singola)",
            "tv_multi": "Serie TV (più stagioni)",
        },
    },
    "EN": {
        "subtitle": "Release maker for P2P forums",
        "section_type": "RELEASE TYPE",
        "section_template": "TEMPLATE",
        "all_templates": "All templates",
        "section_path": "FILE / FOLDER",
        "section_options": "OPTIONS (OPTIONAL)",
        "select_path": "📁  Select Path",
        "change_path": "📁  Change Path",
        "no_path": "No path selected",
        "rename": "Rename the file",
        "crew_label": "Custom crew name",
        "tmdb_label": "TheMovieDB ID (e.g. 27205)",
        "make_release": "Make Release!",
        "authors": "Authors: RickSanchez & Norman",
        "updates": "Check for updates ↗",
        "tmdb_dialog_title": "Select the title",
        "tmdb_results": "Multiple results found on TheMovieDB — pick the correct one:",
        "tmdb_none": "No results found on TheMovieDB.",
        "tmdb_manual": "...or enter a TMDB ID manually:",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "cancelled_msg": "Cancelled: no title selected.",
        "types": {
            "movie": "Movie (File)",
            "movie_folder": "Movie (Folder)",
            "tv_episode": "TV Series (Single Episode)",
            "tv_single": "TV Series (Single Season)",
            "tv_multi": "TV Series (Multiple Seasons)",
        },
    },
}


def callback(url):
    webbrowser.open_new(url)


class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MakeRelease")
        self.geometry("440x800")
        self.minsize(440, 800)
        self.grid_columnconfigure(0, weight=1)

        # Modes: system (default), light, dark
        ctk.set_appearance_mode("System")
        # Themes: blue (default), dark-blue, green
        ctk.set_default_color_theme("blue")

        # Gerarchia tipografica
        self.font_title = ctk.CTkFont(size=26, weight="bold")
        self.font_subtitle = ctk.CTkFont(size=13)
        self.font_section = ctk.CTkFont(size=11, weight="bold")
        self.font_body = ctk.CTkFont(size=13)
        self.font_cta = ctk.CTkFont(size=15, weight="bold")
        self.font_small = ctk.CTkFont(size=11)

        # Colori "muted" coerenti tra tema chiaro e scuro
        self.color_muted = ("gray45", "gray60")
        self.color_section = ("gray40", "gray60")
        self.color_link = ("#1f6aa5", "#5aa9e6")

        # Stato della lingua e del tipo selezionato (valore interno)
        self.lang = DEFAULT_LANG
        self._type_value = RELEASE_VALUES[0]
        self._template_value = None  # None = tutti i template

        self._build_header()
        self._build_card()
        self._build_action()
        self._build_footer()

        # Applica le stringhe nella lingua di default
        self._apply_language()

    # --- Costruzione UI -----------------------------------------------------

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PAD_X, pady=(24, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="🎬  MakeRelease", font=self.font_title).grid(
            row=0, column=0, sticky="w"
        )
        self.subtitle_label = ctk.CTkLabel(
            header, text="", font=self.font_subtitle, text_color=self.color_muted
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Selettore lingua: cambia l'interfaccia al volo
        self.lang_switch = ctk.CTkSegmentedButton(
            header,
            values=list(LANGUAGES),
            command=self._on_language_change,
            font=self.font_small,
            width=92,
            height=28,
        )
        self.lang_switch.set(self.lang)
        self.lang_switch.grid(row=0, column=1, rowspan=2, sticky="e")

    def _build_card(self):
        card = ctk.CTkFrame(self, corner_radius=12)
        card.grid(row=1, column=0, sticky="ew", padx=PAD_X, pady=8)
        card.grid_columnconfigure(0, weight=1)

        # --- Tipo di release ---
        self.section_type = self._section(card, row=0, top=CARD_PAD)
        self.var_type = StringVar()
        self.option_menu = ctk.CTkOptionMenu(
            card,
            variable=self.var_type,
            values=self._release_labels(),
            command=self._on_type_change,
            font=self.font_body,
            height=36,
            corner_radius=8,
        )
        self.option_menu.grid(row=1, column=0, sticky="ew", padx=CARD_PAD, pady=(0, 6))

        # --- Template ---
        self.section_template = self._section(card, row=2)
        self.var_template = StringVar()
        self.template_menu = ctk.CTkOptionMenu(
            card,
            variable=self.var_template,
            values=self._template_labels(),
            command=self._on_template_change,
            font=self.font_body,
            height=36,
            corner_radius=8,
        )
        self.template_menu.grid(row=3, column=0, sticky="ew", padx=CARD_PAD, pady=(0, 6))

        # --- Percorso ---
        self.section_path = self._section(card, row=4)
        self.select_button = ctk.CTkButton(
            card,
            text="",
            command=self.select,
            font=self.font_body,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=("gray65", "gray40"),
            text_color=("gray10", "gray90"),
            hover_color=("gray90", "gray25"),
        )
        self.select_button.grid(row=5, column=0, sticky="ew", padx=CARD_PAD, pady=(0, 4))

        self.selected_path = StringVar(value="")
        self.selected_path_label = ctk.CTkLabel(
            card,
            text="",
            font=self.font_small,
            text_color=self.color_muted,
            anchor="w",
            justify="left",
            wraplength=350,
        )
        self.selected_path_label.grid(row=6, column=0, sticky="ew", padx=CARD_PAD, pady=(0, 8))

        self.var_rename = BooleanVar(value=False)
        self.rename_switch = ctk.CTkSwitch(
            card, text="", variable=self.var_rename, font=self.font_body
        )
        self.rename_switch.grid(row=7, column=0, sticky="w", padx=CARD_PAD, pady=(0, 4))

        # --- Opzioni facoltative ---
        self.section_options = self._section(card, row=8)

        self.label_crew = ctk.CTkLabel(
            card, text="", font=self.font_small, text_color=("gray25", "gray75"), anchor="w"
        )
        self.label_crew.grid(row=9, column=0, sticky="ew", padx=CARD_PAD, pady=(0, 2))
        self.var_crew = StringVar(value="")
        self.crew_entry = ctk.CTkEntry(
            card,
            textvariable=self.var_crew,
            font=self.font_body,
            height=36,
            corner_radius=8,
        )
        self.crew_entry.grid(row=10, column=0, sticky="ew", padx=CARD_PAD, pady=(0, 8))

        self.label_tmdb = ctk.CTkLabel(
            card, text="", font=self.font_small, text_color=("gray25", "gray75"), anchor="w"
        )
        self.label_tmdb.grid(row=11, column=0, sticky="ew", padx=CARD_PAD, pady=(0, 2))
        self.var_idtmdb = StringVar(value="")
        self.idtmdb_entry = ctk.CTkEntry(
            card,
            textvariable=self.var_idtmdb,
            font=self.font_body,
            height=36,
            corner_radius=8,
        )
        self.idtmdb_entry.grid(row=12, column=0, sticky="ew", padx=CARD_PAD, pady=(0, CARD_PAD))

    def _build_action(self):
        self.make_release_button = ctk.CTkButton(
            self,
            text="",
            state="disabled",
            command=self.make_release,
            font=self.font_cta,
            height=46,
            corner_radius=10,
        )
        self.make_release_button.grid(row=2, column=0, sticky="ew", padx=PAD_X, pady=(12, 8))

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=PAD_X, pady=(0, 16))
        footer.grid_columnconfigure(0, weight=1)

        self.authors_label = ctk.CTkLabel(
            footer, text="", font=self.font_small, text_color=self.color_muted
        )
        self.authors_label.grid(row=0, column=0, sticky="w")

        self.update_link = ctk.CTkLabel(
            footer, text="", font=self.font_small, text_color=self.color_link, cursor="hand2"
        )
        self.update_link.grid(row=1, column=0, sticky="w", pady=(2, 0))
        self.update_link.bind("<Button-1>", lambda e: callback(REPO_URL))

    def _section(self, parent, row, top=14):
        """Crea un'etichetta di sezione (piccola, maiuscola, attenuata) e la restituisce."""
        label = ctk.CTkLabel(
            parent, text="", font=self.font_section, text_color=self.color_section, anchor="w"
        )
        label.grid(row=row, column=0, sticky="ew", padx=CARD_PAD, pady=(top, 4))
        return label

    # --- Lingua -------------------------------------------------------------

    def _release_labels(self):
        """Etichette dei tipi di release nella lingua corrente."""
        return [TR[self.lang]["types"][value] for value in RELEASE_VALUES]

    def _on_type_change(self, label):
        """Aggiorna il valore interno quando l'utente cambia il tipo dal menu."""
        for value, text in TR[self.lang]["types"].items():
            if text == label:
                self._type_value = value
                return

    def _template_labels(self):
        """Voci del menu template: 'Tutti' + i singoli file .jinja in config/."""
        return [TR[self.lang]["all_templates"], *constants.templates]

    def _on_template_change(self, label):
        """Aggiorna il template selezionato (None = tutti)."""
        if label == TR[self.lang]["all_templates"]:
            self._template_value = None
        else:
            self._template_value = label

    def _on_language_change(self, lang):
        self.lang = lang
        self._apply_language()

    def _apply_language(self):
        """Aggiorna tutte le stringhe dell'interfaccia nella lingua corrente."""
        t = TR[self.lang]

        self.subtitle_label.configure(text=t["subtitle"])
        self.section_type.configure(text=t["section_type"])
        self.section_template.configure(text=t["section_template"])
        self.section_path.configure(text=t["section_path"])
        self.section_options.configure(text=t["section_options"])

        # Menu dei tipi: aggiorna le etichette mantenendo la selezione corrente
        self.option_menu.configure(values=self._release_labels())
        self.var_type.set(t["types"][self._type_value])

        # Menu template: solo la voce "Tutti" cambia con la lingua, i nomi file no
        self.template_menu.configure(values=self._template_labels())
        self.var_template.set(self._template_value or t["all_templates"])

        self.rename_switch.configure(text=t["rename"])
        self.label_crew.configure(text=t["crew_label"])
        self.label_tmdb.configure(text=t["tmdb_label"])
        self.make_release_button.configure(text=t["make_release"])
        self.authors_label.configure(text=t["authors"])
        self.update_link.configure(text=t["updates"])

        # Pulsante percorso ed etichetta dipendono dallo stato di selezione
        if self.selected_path.get():
            self.select_button.configure(text=t["change_path"])
            self.selected_path_label.configure(
                text=self.selected_path.get(), text_color=("gray10", "gray90")
            )
        else:
            self.select_button.configure(text=t["select_path"])
            self.selected_path_label.configure(text=t["no_path"], text_color=self.color_muted)

    # --- Logica -------------------------------------------------------------

    def select(self):
        # 'movie' e 'tv_episode' sono singoli file; gli altri tipi sono cartelle
        if self._type_value in ("movie", "tv_episode"):
            file_path = filedialog.askopenfilename()
        else:
            file_path = filedialog.askdirectory()
        if file_path:
            self.selected_path.set(file_path)
            self.make_release_button.configure(state="normal")
            self.select_button.configure(text=TR[self.lang]["change_path"])
            self.selected_path_label.configure(text=file_path, text_color=("gray10", "gray90"))

    def _choose_tmdb(self, candidates):
        """Dialog di selezione del titolo TMDB; ritorna l'id (str) o None se annullato."""
        t = TR[self.lang]
        result = {"id": None}

        dialog = ctk.CTkToplevel(self)
        dialog.title(t["tmdb_dialog_title"])
        dialog.geometry("460x300")
        dialog.transient(self)
        dialog.grid_columnconfigure(0, weight=1)

        # Mappa "Titolo (anno)" -> id TMDB
        label_to_id = {f"{c['title']} ({c['year']})": c["id"] for c in candidates}

        row = 0
        if candidates:
            ctk.CTkLabel(
                dialog, text=t["tmdb_results"], font=self.font_body,
                anchor="w", justify="left", wraplength=420,
            ).grid(row=row, column=0, sticky="ew", padx=20, pady=(20, 6))
            row += 1

            var_choice = StringVar(value=next(iter(label_to_id)))
            ctk.CTkOptionMenu(
                dialog, variable=var_choice, values=list(label_to_id),
                font=self.font_body, height=36, corner_radius=8, dynamic_resizing=False,
            ).grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 12))
            row += 1
        else:
            var_choice = None
            ctk.CTkLabel(
                dialog, text=t["tmdb_none"], font=self.font_body,
                anchor="w", justify="left", wraplength=420,
            ).grid(row=row, column=0, sticky="ew", padx=20, pady=(20, 6))
            row += 1

        ctk.CTkLabel(
            dialog, text=t["tmdb_manual"], font=self.font_small,
            text_color=self.color_muted, anchor="w",
        ).grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 2))
        row += 1
        manual_entry = ctk.CTkEntry(dialog, placeholder_text="es. 27205", height=36, corner_radius=8)
        manual_entry.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 16))
        row += 1

        def confirm():
            manual = manual_entry.get().strip()
            if manual.isdigit():
                result["id"] = manual
            elif var_choice is not None:
                result["id"] = label_to_id[var_choice.get()]
            dialog.destroy()

        def cancel():
            result["id"] = None
            dialog.destroy()

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 16))
        buttons.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(
            buttons, text=t["cancel"], command=cancel, height=38, corner_radius=8,
            fg_color="transparent", border_width=1, border_color=("gray65", "gray40"),
            text_color=("gray10", "gray90"), hover_color=("gray90", "gray25"),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            buttons, text=t["confirm"], command=confirm, height=38, corner_radius=8, font=self.font_cta
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        dialog.protocol("WM_DELETE_WINDOW", cancel)
        dialog.update()
        dialog.lift()
        dialog.grab_set()
        self.wait_window(dialog)
        return result["id"]

    def make_release(self, debug: bool = False):
        if debug:
            print(
                f"Calling MakeRelease with:\n"
                f"crew={self.var_crew.get()},\n"
                f"rename={self.var_rename.get()},\n"
                f"type={self._type_value},\n"
                f"template={self._template_value},\n"
                f"path={self.selected_path.get()}"
            )

        releaser = MakeRelease(
            crew=self.var_crew.get(),
            rename=self.var_rename.get(),
            type=self._type_value,
            path=self.selected_path.get(),
            id=self.var_idtmdb.get(),
            template=self._template_value,
            chooser=self._choose_tmdb,
        )
        try:
            releaser.make_release()
        except SearchCancelled:
            print(TR[self.lang]["cancelled_msg"])


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
