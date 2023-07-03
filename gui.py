import webbrowser
from tkinter import BooleanVar, StringVar, filedialog

import customtkinter as ctk

# from makerelease import MakeRelease


def callback(url):
    webbrowser.open_new(url)


class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MakeRelease")
        self.geometry("400x250")
        self.grid_columnconfigure(0, weight=1)

        ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
        ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        ctk.CTkLabel(
            self, text="Select the type of release", fg_color="transparent"
        ).grid(row=1, column=0, sticky="w", padx=10, pady=0)

        self.var_type = StringVar(value="Movie (File)")
        options = [
            "Movie (File)",
            "Movie (Folder)",
            "TV Series (Single Season)",
            "TV Series (Multiple Seasons)",
        ]
        self.option_menu = ctk.CTkOptionMenu(
            self, variable=self.var_type, values=options
        )
        self.option_menu.grid(row=2, column=0, sticky="nsew", padx=10, pady=2)

        self.select_button = ctk.CTkButton(
            self, text="Select Path", command=self.select
        )
        self.select_button.grid(row=3, column=0, sticky="nsew", padx=10, pady=2)

        self.make_release_button = ctk.CTkButton(
            self, text="Make Release!", state="disabled", command=self.make_release
        )
        self.make_release_button.grid(row=4, column=0, sticky="nsew", padx=10, pady=2)
        # TODO add text with the selected path

        self.var_rename = BooleanVar(value=False)
        self.rename_option_menu = ctk.CTkSwitch(
            self, text="Rename the file", variable=self.var_rename
        )
        self.rename_option_menu.grid(row=5, column=0, sticky="nsew", padx=10, pady=2)

        self.author_label = ctk.CTkLabel(
            self,
            justify="left",
            text="Authors: RickSanchez & Norman",
            fg_color="transparent",
        )
        self.author_label.grid(row=7, column=0, sticky="w", padx=10, pady=0)

        self.check_updates = ctk.CTkLabel(
            self,
            justify="left",
            text="Check for updates",
            fg_color="transparent",
            text_color="green",
        )
        self.check_updates.bind(
            "<Button-1>", lambda e: callback("http://www.github.com")
        )
        self.check_updates.grid(row=8, column=0, sticky="w", padx=10, pady=0)

        self.selected_path = StringVar(value="")

    def select(self):
        if self.var_type.get() == "Movie (File)":
            file_path = filedialog.askopenfilename()
        else:
            file_path = filedialog.askdirectory()
        if file_path:
            self.selected_path.set(file_path)
            self.make_release_button.configure(state="normal")
            self.select_button.configure(text="Change Path")

    def make_release(self):
        print(f"Selected path: {self.selected_path.get()}")
        print(f"Rename option: {self.var_rename.get()}")
        print(f"Type: {self.var_type.get()}")
        # releaser = MakeRelease(self.var_type.get(), self.selected_path.get(), self.var_rename.get())
        # releaser.run()


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
