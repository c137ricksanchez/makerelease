import webbrowser
from tkinter import BooleanVar, StringVar, filedialog

import customtkinter as ctk

from src.app import MakeRelease
from src.constants import crew


def callback(url):
    webbrowser.open_new(url)


class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MakeRelease")
        self.geometry("400x360")
        self.grid_columnconfigure(0, weight=1)

        ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
        ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        ctk.CTkLabel(
            self, text="Select the type of release", fg_color="transparent"
        ).grid(row=1, column=0, sticky="w", padx=10, pady=0)

        self.option_map = {
            "Movie (File)": "movie",
            "Movie (Folder)": "movie_folder",
            "TV Series (Single Season)": "tv_single",
            "TV Series (Multiple Seasons)": "tv_multi",
        }
        options = list(self.option_map.keys())
        self.var_type = StringVar(value=options[0])
        self.option_menu = ctk.CTkOptionMenu(
            self, variable=self.var_type, values=options
        )
        self.option_menu.grid(row=2, column=0, sticky="nsew", padx=10, pady=2)

        self.select_button = ctk.CTkButton(
            self, text="Select Path", command=self.select
        )
        self.select_button.grid(row=3, column=0, sticky="nsew", padx=10, pady=2)

        self.selected_path = StringVar(value="")
        self.selected_path_label = ctk.CTkLabel(
            self,
            text="Path not selected",
            fg_color="transparent",
        )
        self.selected_path_label.grid(row=4, column=0, sticky="w", padx=10, pady=0)

        self.make_release_button = ctk.CTkButton(
            self, text="Make Release!", state="disabled", command=self.make_release
        )
        self.make_release_button.grid(row=5, column=0, sticky="nsew", padx=10, pady=2)

        self.var_rename = BooleanVar(value=False)
        self.rename_option_menu = ctk.CTkSwitch(
            self, text="Rename the file", variable=self.var_rename
        )
        self.rename_option_menu.grid(row=6, column=0, sticky="nsew", padx=10, pady=2)

        # Add custom crew name
        ctk.CTkLabel(
            self, text="Add custom crew name (optional)", fg_color="transparent"
        ).grid(row=7, column=0, sticky="w", padx=10, pady=0)
        self.var_crew = StringVar(value=crew)
        self.crew_entry = ctk.CTkEntry(self, textvariable=self.var_crew)
        self.crew_entry.grid(row=8, column=0, sticky="nsew", padx=10, pady=2)

        # Add TMDB ID
        ctk.CTkLabel(self, text="Add TMDB ID (optional)", fg_color="transparent").grid(
            row=9, column=0, sticky="w", padx=10, pady=0
        )
        self.var_idtmdb = StringVar(value="")
        self.idtmdb_entry = ctk.CTkEntry(self, textvariable=self.var_idtmdb)
        self.idtmdb_entry.grid(row=10, column=0, sticky="nsew", padx=10, pady=2)

        self.author_label = ctk.CTkLabel(
            self,
            justify="left",
            text="Authors: RickSanchez & Norman",
            fg_color="transparent",
        )
        self.author_label.grid(row=11, column=0, sticky="w", padx=10, pady=0)

        self.check_updates = ctk.CTkLabel(
            self,
            justify="left",
            text="Check for updates",
            fg_color="transparent",
            text_color="green",
        )
        self.check_updates.bind(
            "<Button-1>",
            lambda e: callback("https://github.com/c137ricksanchez/automatic-releaser"),
        )
        self.check_updates.grid(row=12, column=0, sticky="w", padx=10, pady=0)

    def select(self):
        if self.var_type.get() == "Movie (File)":
            file_path = filedialog.askopenfilename()
        else:
            file_path = filedialog.askdirectory()
        if file_path:
            self.selected_path.set(file_path)
            self.make_release_button.configure(state="normal")
            self.select_button.configure(text="Change Path")
            self.selected_path_label.configure(
                text=f"Selected path: {self.selected_path.get()}"
            )

    def make_release(self, debug: bool = False):
        if debug:
            print(
                f"Calling MakeRelease with:\n"
                f"crew={self.var_crew.get()},\n"
                f"rename={self.var_rename.get()},\n"
                f"type={self.option_map[self.var_type.get()]},\n"
                f"path={self.selected_path.get()}"
            )

        releaser = MakeRelease(
            crew=self.var_crew.get(),
            rename=self.var_rename.get(),
            type=self.option_map[self.var_type.get()],
            path=self.selected_path.get(),
            id=self.var_idtmdb.get(),
        )
        releaser.make_release()
        exit()


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
