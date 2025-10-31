"""Tkinter view for the BulkToPDF desktop application."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from bulktopdf.config import CONFIG

try:  # Optional dependency for drag-and-drop.
    from tkinterdnd2 import DND_FILES  # type: ignore
except ImportError:  # pragma: no cover - used only when optional package installed.
    DND_FILES = None


class ControllerProtocol:
    """Protocol used only for static typing of the view."""

    def browse_input(self) -> None: ...

    def start_conversion(self) -> None: ...

    def download_converted(self) -> None: ...

    def set_input_directory(self, directory: str) -> None: ...


class PDFConverterView(tk.Frame):
    """Tkinter view responsible for rendering the BulkToPDF UI."""

    def __init__(self, master: tk.Widget, controller: ControllerProtocol):
        super().__init__(master)
        self.controller = controller
        self.dnd_supported = DND_FILES is not None and hasattr(master, "drop_target_register")
        self.selected_path = tk.StringVar(value="Drop a folder here or click Browse")
        self.copy_mode = tk.BooleanVar(value=CONFIG.conversion.copy_unsupported_by_default)
        self._themes = {
            "light": {
                "background": "#F8FAFC",
                "foreground": "#0F172A",
                "surface": "#FFFFFF",
                "surface_border": "#CBD5F5",
                "surface_hover": "#E2E8F0",
                "accent": "#2563EB",
                "accent_active": "#1D4ED8",
                "accent_disabled": "#94A3B8",
                "button_bg": "#2563EB",
                "button_fg": "#FFFFFF",
                "button_active_bg": "#1D4ED8",
                "button_disabled_bg": "#E2E8F0",
                "button_disabled_fg": "#94A3B8",
            "progress_trough": "#E2E8F0",
            "progress_bg": "#2563EB",
            "text_bg": "#FFFFFF",
            "text_fg": "#0F172A",
            "text_border": "#CBD5F5",
            "tooltip_bg": "#FFFFE0",
            "tooltip_fg": "#1F2933",
            "tooltip_border": "#CBD5F5",
        },
        "dark": {
            "background": "#0C0C0D",
            "foreground": "#E4E4E7",
            "surface": "#18181B",
            "surface_border": "#27272A",
            "surface_hover": "#202023",
            "accent": "#D4D4D8",
            "accent_active": "#E4E4E7",
            "accent_disabled": "#3F3F46",
            "button_bg": "#2B2B2F",
            "button_fg": "#F4F4F5",
            "button_active_bg": "#3F3F46",
            "button_disabled_bg": "#18181B",
            "button_disabled_fg": "#71717A",
            "progress_trough": "#151517",
            "progress_bg": "#52525B",
            "text_bg": "#0F0F10",
            "text_fg": "#E4E4E7",
            "text_border": "#27272A",
            "tooltip_bg": "#1F1F22",
            "tooltip_fg": "#E4E4E7",
            "tooltip_border": "#3F3F46",
        },
    }
        default_theme = CONFIG.ui.default_theme.lower()
        if default_theme not in {"light", "dark"}:
            default_theme = "light"
        self._dark_mode = tk.BooleanVar(value=default_theme == "dark")
        self._current_theme: str | None = None
        self._status_normal_fg = "#1F2933"
        self._status_error_fg = "#B91C1C"
        self.config(padx=20, pady=20)
        self.columnconfigure(0, weight=1)
        self._build_widgets()

    # --------------------------------------------------------------------- UI construction
    def _build_widgets(self) -> None:
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 11), padding=5)
        style.configure("DropFrame.TFrame", borderwidth=2, relief="ridge")

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Input Folder").grid(row=0, column=0, sticky="w")
        self.theme_toggle = ttk.Checkbutton(
            header,
            text="Dark mode",
            variable=self._dark_mode,
            command=self._apply_current_theme,
        )
        self.theme_toggle.grid(row=0, column=1, sticky="e")

        self.drop_frame = ttk.Frame(self, style="DropFrame.TFrame", padding=20)
        self.drop_frame.grid(row=1, column=0, sticky="ew", pady=(10, 5))
        self.drop_frame.columnconfigure(0, weight=1)

        drop_label = ttk.Label(
            self.drop_frame,
            textvariable=self.selected_path,
            anchor="center",
            justify="center",
            wraplength=520,
        )
        drop_label.grid(row=0, column=0, sticky="ew")

        if self.dnd_supported:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind("<<Drop>>", self._on_drop)

        button_row = ttk.Frame(self)
        button_row.grid(row=2, column=0, sticky="ew", pady=(5, 15))
        for column in range(3):
            button_row.columnconfigure(column, weight=0)
        button_row.columnconfigure(3, weight=1)

        browse_button = ttk.Button(button_row, text="Browse...", command=self.controller.browse_input)
        browse_button.grid(row=0, column=0, padx=(0, 10))

        self.convert_button = ttk.Button(
            button_row,
            text="Convert",
            command=self.controller.start_conversion,
            state=tk.DISABLED,
        )
        self.convert_button.grid(row=0, column=1, padx=(0, 10))

        self.download_button = ttk.Button(
            button_row,
            text="Download Zip",
            command=self.controller.download_converted,
            state=tk.DISABLED,
        )
        self.download_button.grid(row=0, column=2)

        copy_checkbox = ttk.Checkbutton(
            button_row,
            text="Copy other files",
            variable=self.copy_mode,
        )
        copy_checkbox.grid(row=1, column=0, sticky="w", pady=(8, 0))

        info_label = ttk.Label(button_row, text="ⓘ", cursor="hand2", padding=(4, 0))
        info_label.grid(row=1, column=1, sticky="w", pady=(8, 0))
        self._attach_tooltip(
            info_label,
            "When enabled, files that are not Word/Excel/PDF will be copied into the output archive.",
        )

        self.progress_frame = ttk.Frame(self)
        self.progress_frame.grid(row=3, column=0, sticky="ew", pady=(10, 5))
        self.progress_frame.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(self.progress_frame, mode="determinate")
        self.progress.configure(style="App.Horizontal.TProgressbar")
        self.progress.grid(row=0, column=0, sticky="ew")

        self.progress_label = ttk.Label(self.progress_frame, text="0% • 0/0 files")
        self.progress_label.grid(row=1, column=0, sticky="e", pady=(4, 0))

        self.status_box = ttk.LabelFrame(self, text="Status")
        self.status_box.grid(row=4, column=0, sticky="ew", pady=(5, 5))
        self.status_box.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(self.status_box, text="Ready.", font=("Arial", 11))
        self.status_label.grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self._configure_status_colors()

        self.error_frame = ttk.LabelFrame(self, text="Errors", padding=(10, 10, 10, 10))
        self.error_frame.grid(row=5, column=0, sticky="nsew", pady=(0, 40))
        self.rowconfigure(5, weight=1, minsize=220)
        self.error_frame.columnconfigure(0, weight=1)
        self.error_frame.rowconfigure(0, weight=1)

        self.error_text = tk.Text(
            self.error_frame,
            height=8,
            wrap="word",
            state=tk.DISABLED,
            font=("Arial", 10),
            relief="flat",
            bg=self.cget("background"),
            padx=6,
            pady=6,
        )
        self.error_text.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        status_scrollbar = ttk.Scrollbar(self.error_frame, orient="vertical", command=self.error_text.yview)
        status_scrollbar.grid(row=0, column=1, sticky="ns")
        self.error_text.configure(yscrollcommand=status_scrollbar.set)

        self.download_button.grid_remove()
        self.error_count = 0
        self._update_error_header()
        self._tooltip_window: tk.Toplevel | None = None
        self._apply_current_theme()

    # --------------------------------------------------------------------- Controller API
    def set_input_display(self, path: str) -> None:
        display_text = path if path else "Drop a folder here or click Browse"
        self.selected_path.set(display_text)
        self.convert_button.config(state=tk.NORMAL if path else tk.DISABLED)

    def display_info(self, message: str) -> None:
        self._set_status(message, is_error=False)

    def display_error(self, message: str) -> None:
        self._set_status(message, is_error=True)

    def display_progress(self, message: str) -> None:
        self._set_status(message, is_error=False)

    def update_progress(self, current: int, total: int) -> None:
        total = max(total, 1)
        current = min(current, total)
        self.progress.configure(maximum=total, value=current)
        percent = int((current / total) * 100)
        self.progress_label.config(text=f"{percent}% • {current}/{total} files")

    def reset_progress(self) -> None:
        self.progress.configure(value=0)
        self.progress_label.config(text="0% • 0/0 files")

    def show_download_ready(self, zip_available: bool) -> None:
        if zip_available:
            self.download_button.grid()
            self.download_button.config(state=tk.NORMAL)
        else:
            self.download_button.config(state=tk.DISABLED)
            self.download_button.grid_remove()

    def reset_after_download(self) -> None:
        self.download_button.config(state=tk.DISABLED)
        self.display_info("Zip saved successfully.")
        self.download_button.grid_remove()

    def should_copy_unsupported(self) -> bool:
        return bool(self.copy_mode.get())

    def clear_errors(self) -> None:
        self.error_text.configure(state=tk.NORMAL)
        self.error_text.delete("1.0", tk.END)
        self.error_text.configure(state=tk.DISABLED)
        self.error_count = 0
        self._update_error_header()

    def record_conversion_error(self, message: str) -> None:
        self._set_status(message, is_error=True)
        self._append_error(message)

    # --------------------------------------------------------------------- Internal helpers
    def _apply_current_theme(self) -> None:
        theme = "dark" if self._dark_mode.get() else "light"
        self._apply_theme(theme)

    def _apply_theme(self, theme: str) -> None:
        if theme not in self._themes:
            theme = "light"
        if theme == self._current_theme:
            return
        palette = self._themes[theme]
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=palette["background"])
        style.configure("TLabel", background=palette["background"], foreground=palette["foreground"])
        style.configure(
            "TButton",
            background=palette["button_bg"],
            foreground=palette["button_fg"],
            bordercolor=palette["button_bg"],
            focusthickness=1,
        )
        style.map(
            "TButton",
            background=[
                ("active", palette["button_active_bg"]),
                ("disabled", palette["button_disabled_bg"]),
            ],
            foreground=[("disabled", palette["button_disabled_fg"])],
        )
        style.configure(
            "TCheckbutton",
            background=palette["background"],
            foreground=palette["foreground"],
        )
        style.map(
            "TCheckbutton",
            background=[("active", palette["surface_hover"])],
            foreground=[("disabled", palette["button_disabled_fg"])],
        )
        style.configure(
            "TLabelframe",
            background=palette["background"],
            bordercolor=palette["surface_border"],
        )
        style.configure(
            "TLabelframe.Label",
            background=palette["background"],
            foreground=palette["foreground"],
        )
        style.configure(
            "DropFrame.TFrame",
            background=palette["surface"],
            bordercolor=palette["surface_border"],
            relief="ridge",
        )
        style.map(
            "DropFrame.TFrame",
            background=[("active", palette["surface_hover"])],
        )
        style.configure(
            "App.Horizontal.TProgressbar",
            troughcolor=palette["progress_trough"],
            bordercolor=palette["progress_trough"],
            background=palette["progress_bg"],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=palette["background"],
            troughcolor=palette["surface"],
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", palette["surface_hover"])],
        )

        root = self.winfo_toplevel()
        try:
            root.configure(bg=palette["background"])
        except tk.TclError:
            pass
        self.configure(bg=palette["background"])
        self.drop_frame.configure(style="DropFrame.TFrame")
        self.progress.configure(style="App.Horizontal.TProgressbar")
        self.status_box.configure(style="TLabelframe")
        self.error_frame.configure(style="TLabelframe")
        self.error_text.configure(
            bg=palette["surface"],
            fg=palette["text_fg"],
            insertbackground=palette["text_fg"],
            highlightbackground=palette["text_border"],
            highlightcolor=palette["text_border"],
            highlightthickness=1,
        )
        self._configure_status_colors(background=palette["background"])
        self._current_theme = theme

    def _configure_status_colors(self, background: str | None = None) -> None:
        style = ttk.Style()
        if not background:
            background = (
                self.status_label.cget("background")
                or style.lookup("TLabel", "background")
                or style.lookup("TFrame", "background")
            )
        if not background:
            background = self.cget("background") or "#FFFFFF"
        try:
            r, g, b = self.winfo_rgb(background)
        except tk.TclError:
            r, g, b = (0xFFFF, 0xFFFF, 0xFFFF)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 65535
        if luminance > 0.5:
            self._status_normal_fg = "#1F2933"
            self._status_error_fg = "#B91C1C"
        else:
            self._status_normal_fg = "#F1F5F9"
            self._status_error_fg = "#FCA5A5"
        current_text = self.status_label.cget("text")
        self.status_label.config(foreground=self._status_normal_fg, text=current_text)

    def _set_status(self, message: str, is_error: bool) -> None:
        foreground = self._status_error_fg if is_error else self._status_normal_fg
        self.status_label.config(text=message, foreground=foreground)

    def _append_error(self, message: str) -> None:
        self.error_text.configure(state=tk.NORMAL)
        if self.error_text.index("end-1c") != "1.0":
            self.error_text.insert(tk.END, "\n")
        self.error_count += 1
        self._update_error_header()
        self.error_text.insert(tk.END, f"[{self.error_count}] {message}")
        self.error_text.see(tk.END)
        self.error_text.configure(state=tk.DISABLED)

    def _update_error_header(self) -> None:
        if self.error_count:
            self.error_frame.config(text=f"Errors ({self.error_count})")
        else:
            self.error_frame.config(text="Errors")

    # --------------------------------------------------------------------- Drag-and-drop
    def _on_drop(self, event: tk.Event) -> None:  # type: ignore[override]
        paths = self._split_dnd_event(event.data)
        if paths:
            self.controller.set_input_directory(paths[0])

    @staticmethod
    def _split_dnd_event(data: str | None) -> list[str]:
        if not data:
            return []
        result: list[str] = []
        current = ""
        in_braces = False
        for char in data:
            if char == "{":
                in_braces = True
                current = ""
            elif char == "}":
                in_braces = False
                result.append(current)
                current = ""
            elif char == " " and not in_braces:
                if current:
                    result.append(current)
                    current = ""
            else:
                current += char
        if current:
            result.append(current)
        return result

    # --------------------------------------------------------------------- Tooltip helper
    def _attach_tooltip(self, widget: ttk.Widget, text: str) -> None:
        def on_enter(event):  # noqa: ANN001
            if self._tooltip_window is not None:
                return
            palette = self._themes.get(
                self._current_theme or ("dark" if self._dark_mode.get() else "light")
            )
            if palette is None:
                palette = self._themes["light"]
            tooltip_bg = palette.get("tooltip_bg", "#FFFFE0")
            tooltip_fg = palette.get("tooltip_fg", "#1F2933")
            tooltip_border = palette.get("tooltip_border", "#CBD5F5")
            self._tooltip_window = tk.Toplevel(self)
            self._tooltip_window.wm_overrideredirect(True)
            self._tooltip_window.attributes("-topmost", True)
            self._tooltip_window.configure(background=tooltip_border)
            label = tk.Label(
                self._tooltip_window,
                text=text,
                background=tooltip_bg,
                foreground=tooltip_fg,
                relief="flat",
                borderwidth=0,
                padx=8,
                pady=4,
                wraplength=260,
            )
            label.pack(padx=1, pady=1)
            x = event.x_root + 10
            y = event.y_root + 10
            self._tooltip_window.wm_geometry(f"+{x}+{y}")

        def on_leave(_event):  # noqa: ANN001
            if self._tooltip_window is not None:
                self._tooltip_window.destroy()
                self._tooltip_window = None

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
