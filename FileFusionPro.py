import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import webbrowser

PRIMARY_EXTENSIONS = ['.txt', '.py', '.md', '.csv', '.json', '.html', '.css', '.js', '.xml']
ADDITIONAL_EXTENSIONS = ['.log', '.tsv', '.yaml', '.yml', '.ini', '.conf', '.cfg', '.env', '.toml',
                         '.ts', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.kt', '.kts', '.swift',
                         '.rb', '.php', '.sh', '.bat', '.ps1', '.go', '.rs', '.rst', '.tex', '.sql']
SUPPORTED_EXTENSIONS = PRIMARY_EXTENSIONS + ADDITIONAL_EXTENSIONS


class FileCombinerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FileFusion Pro")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("dark-blue")

        # Set window to open maximized
        self.after(100, lambda: self.state('zoomed'))
        self.minsize(800, 650)

        self.selected_dir = None
        self.check_vars = {}
        self.all_checkboxes = []
        self.dark_mode = True

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_widgets()
        self.apply_styles()
        self.toggle_theme()

    def create_widgets(self):
        # Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.logo_label = ctk.CTkLabel(self.header_frame, text="FileFusion Pro", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, columnspan=2, padx=20, pady=15, sticky="n")

        self.version_label = ctk.CTkLabel(self.header_frame, text="v1.0.1", text_color="gray70", font=ctk.CTkFont(size=10))
        self.version_label.grid(row=0, column=1, padx=20, pady=0, sticky="e")

        # Main Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)

        # Directory Selection Frame
        self.dir_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        self.dir_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.dir_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.dir_frame, text="Project Folder:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")

        self.dir_label = ctk.CTkLabel(self.dir_frame, text="No folder selected", text_color="gray70", anchor="w")
        self.dir_label.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.select_button = ctk.CTkButton(self.dir_frame, text="Browse", width=100, command=self.select_directory)
        self.select_button.grid(row=0, column=2, padx=(5, 15), pady=10, sticky="e")

        # Filetypes Frame
        self.filetypes_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        self.filetypes_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        label_frame = ctk.CTkFrame(self.filetypes_frame, fg_color="transparent")
        label_frame.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(label_frame, text="File Types to Include:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        self.select_all_var = ctk.BooleanVar(value=True)
        self.select_all_checkbox = ctk.CTkCheckBox(label_frame, text="Select All", variable=self.select_all_var, command=self.toggle_all_checkboxes)
        self.select_all_checkbox.pack(side="right")

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.filetypes_frame, placeholder_text="Search extensions...", textvariable=self.search_var)
        self.search_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.search_var.trace_add("write", self.filter_checkboxes)

        self.check_frame = ctk.CTkScrollableFrame(self.filetypes_frame, height=150)
        self.check_frame.pack(pady=(0, 10), padx=10, fill='both', expand=True)

        self.build_checkboxes()

        # Options Frame
        self.options_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        self.options_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.options_frame.grid_columnconfigure((0, 1), weight=1)

        self.theme_switch = ctk.CTkSwitch(self.options_frame, text="Dark Mode", command=self.toggle_theme, variable=ctk.BooleanVar(value=True))
        self.theme_switch.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.filename_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.filename_frame.grid(row=0, column=1, padx=15, pady=10, sticky="e")

        ctk.CTkLabel(self.filename_frame, text="Output File:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 5))

        self.output_entry = ctk.CTkEntry(self.filename_frame, width=180, placeholder_text="combined_output.txt")
        self.output_entry.pack(side="left")

        # Buttons Frame
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1)

        self.combine_button = ctk.CTkButton(self.buttons_frame, text="Combine Files", command=self.combine_files, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.combine_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.preview_button = ctk.CTkButton(self.buttons_frame, text="Preview Files", command=self.preview_files, height=40, font=ctk.CTkFont(size=14))
        self.preview_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        # Status Bar
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_bar.grid(row=2, column=0, sticky="sew", padx=0, pady=0)
        self.status_bar.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", text_color="gray70", anchor="w")
        self.status_label.grid(row=0, column=0, padx=15, sticky="w")

    def apply_styles(self):
        """Apply professional styling to all components"""
        # Main window styling
        self.configure(fg_color=("#F0F0F0", "#1E1E1E"))  # Light/Dark bg
        
        # Header styling
        self.header_frame.configure(fg_color=("#2B579A", "#1E4B8B"), corner_radius=0)
        self.logo_label.configure(text_color="white")
        self.version_label.configure(text_color="#B3D3FF")
        
        # Frame styling
        for frame in [self.main_frame, self.dir_frame, self.filetypes_frame, self.options_frame]:
            frame.configure(
                corner_radius=8,
                border_width=1,
                fg_color=("#F8F8F8", "#252525"),
                border_color=("#E0E0E0", "#404040")
            )
        
        # Button styling
        self.select_button.configure(
            corner_radius=6,
            border_width=1,
            border_color=("#3a7ebf", "#1f538d"),
            fg_color=("#3a7ebf", "#1f538d"),
            hover_color=("#2d63a5", "#14375e"),
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        
        self.combine_button.configure(
            corner_radius=6,
            border_width=0,
            fg_color="#0066CC",
            hover_color="#0052A3",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        
        self.preview_button.configure(
            corner_radius=6,
            border_width=0,
            fg_color="#4E4E4E",
            hover_color="#3A3A3A",
            text_color="white",
            font=ctk.CTkFont(size=14)
        )
        
        # Entry styling
        self.search_entry.configure(
            corner_radius=20,
            border_width=1,
            fg_color=("#FFFFFF", "#2D2D2D"),
            border_color=("#3a7ebf", "#1f538d"),
            placeholder_text_color=("#888888", "#AAAAAA"),
            text_color=("#333333", "#E0E0E0"),
            font=ctk.CTkFont(size=12),
            height=32
        )
        
        self.output_entry.configure(
            corner_radius=6,
            border_width=1,
            fg_color=("#FFFFFF", "#2D2D2D"),
            border_color=("#CCCCCC", "#555555"),
            text_color=("#333333", "#E0E0E0"),
            placeholder_text_color=("#888888", "#888888"),
            font=ctk.CTkFont(size=12)
        )
        
        # Checkbox styling
        self.select_all_checkbox.configure(
            corner_radius=4,
            border_width=1,
            fg_color=("#3a7ebf", "#1f538d"),
            hover_color=("#2d63a5", "#14375e"),
            border_color=("#3a7ebf", "#1f538d"),
            text_color=("#333333", "#E0E0E0"),
            font=ctk.CTkFont(size=12)
        )
        
        # Theme switch styling
        self.theme_switch.configure(
            progress_color=("#3a7ebf", "#1f538d"),
            button_color=("#FFFFFF", "#E0E0E0"),
            button_hover_color=("#F5F5F5", "#D5D5D5")
        )
        
        # Status bar styling
        self.status_bar.configure(fg_color=("#E0E0E0", "#252525"))
        self.status_label.configure(font=ctk.CTkFont(size=11), text_color=("#555555", "#AAAAAA"))

    def build_checkboxes(self):
        self.check_vars.clear()
        for widget in self.check_frame.winfo_children():
            widget.destroy()
        row = col = 0
        for ext in PRIMARY_EXTENSIONS + ["--"] + ADDITIONAL_EXTENSIONS:
            if ext == "--":
                row += 1
                col = 0
                continue
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(self.check_frame, text=ext, variable=var)
            chk.configure(
                corner_radius=4,
                border_width=1,
                fg_color=("#3a7ebf", "#1f538d"),
                hover_color=("#2d63a5", "#14375e"),
                border_color=("#3a7ebf", "#1f538d"),
                text_color=("#333333", "#E0E0E0"),
                font=ctk.CTkFont(size=12)
            )
            chk.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            self.check_vars[ext] = var
            self.all_checkboxes.append(chk)
            col += 1
            if col == 3:
                col = 0
                row += 1

    def filter_checkboxes(self, *args):
        search = self.search_var.get().lower()
        for chk in self.all_checkboxes:
            if search in chk.cget("text").lower():
                chk.grid()
            else:
                chk.grid_remove()

    def toggle_theme(self):
        ctk.set_appearance_mode("Dark" if self.theme_switch.get() else "Light")
        self.theme_switch.configure(text="Dark Mode" if self.theme_switch.get() else "Light Mode")

    def toggle_all_checkboxes(self):
        val = self.select_all_var.get()
        for var in self.check_vars.values():
            var.set(val)

    def select_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_dir = folder
            short_path = folder if len(folder) < 50 else f"...{folder[-47:]}"
            self.dir_label.configure(text=short_path)
            self.update_status(f"Selected folder: {short_path}")

    def get_selected_extensions(self):
        return {ext for ext, var in self.check_vars.items() if var.get()}

    def get_all_files(self, directory, extensions):
        files = []
        for dirpath, _, filenames in os.walk(directory):
            for file in filenames:
                if os.path.splitext(file)[1].lower() in extensions:
                    files.append(os.path.join(dirpath, file))
        return sorted(files)

    def read_file_content(self, path):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"[ERROR reading {path}]: {str(e)}\n"

    def update_status(self, msg):
        self.status_label.configure(text=msg)
        self.update()

    def preview_files(self):
        if not self.selected_dir:
            messagebox.showerror("Error", "Please select a directory first.")
            return
        selected_exts = self.get_selected_extensions()
        files = self.get_all_files(self.selected_dir, selected_exts)
        if not files:
            messagebox.showinfo("Information", "No matching files found.")
            return

        win = ctk.CTkToplevel(self)
        win.title("File Preview")
        
        # Center the preview window
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        window_width = 600
        window_height = 500
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        
        win.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        win.grab_set()

        ctk.CTkLabel(win, text=f"Found {len(files)} files", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        scroll_frame = ctk.CTkScrollableFrame(win)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        for file in files:
            frame = ctk.CTkFrame(scroll_frame, corner_radius=5)
            frame.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(frame, text=f"📄 {os.path.basename(file)}", anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(frame, text=os.path.dirname(file), text_color="gray70", font=ctk.CTkFont(size=10), anchor="w").pack(side="right", padx=5)

        ctk.CTkButton(win, text="Close", command=win.destroy).pack(pady=10)

    def combine_files(self):
        if not self.selected_dir:
            messagebox.showerror("Error", "Please select a directory first.")
            return
        selected_exts = self.get_selected_extensions()
        files = self.get_all_files(self.selected_dir, selected_exts)
        if not files:
            messagebox.showinfo("Information", "No matching files found.")
            return

        user_home = os.path.expanduser("~")
        desktop_path = os.path.join(user_home, "Desktop")
        if not os.path.exists(desktop_path):
            os.makedirs(desktop_path)

        filename = self.output_entry.get().strip() or "combined_output.txt"
        output_path = os.path.join(desktop_path, filename)

        try:
            with open(output_path, 'a+'):
                pass
        except PermissionError:
            messagebox.showerror("File Open", f"Cannot write to {filename}.\n\nPlease close the file before combining.")
            return

        self.update_status(f"Processing {len(files)} files...")
        self.combine_button.configure(state="disabled")
        self.update()

        combined_text = f"// Combined {len(files)} files from: {self.selected_dir}\n// Generated by Pro\n\n"
        for path in files:
            rel_path = os.path.relpath(path, self.selected_dir)
            content = self.read_file_content(path)
            combined_text += f"\n\n// ----- FILE: {rel_path} -----\n{content}\n"

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(combined_text)

            self.update_status(f"Saved to: {output_path}")

            msg = ctk.CTkToplevel(self)
            msg.title("Success")
            
            # Center the success message window
            screen_width = msg.winfo_screenwidth()
            screen_height = msg.winfo_screenheight()
            window_width = 400
            window_height = 200
            x_position = (screen_width // 2) - (window_width // 2)
            y_position = (screen_height // 2) - (window_height // 2)
            
            msg.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
            msg.grab_set()

            ctk.CTkLabel(msg, text=f"Successfully combined {len(files)} files!", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)
            ctk.CTkLabel(msg, text=f"Output file saved to:\n{output_path}", wraplength=350).pack()

            ctk.CTkButton(msg, text="Open File", command=lambda: (webbrowser.open(output_path), msg.destroy()), fg_color="#0066CC").pack(side="left", padx=20, pady=20)
            ctk.CTkButton(msg, text="OK", command=msg.destroy).pack(side="right", padx=20, pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
            self.update_status(f"Error: {str(e)}")
        finally:
            self.combine_button.configure(state="normal")


if __name__ == "__main__":
    app = FileCombinerApp()
    app.mainloop()
