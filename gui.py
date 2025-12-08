"""Tkinter GUI for the Password Health Analyzer."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import tkinter.font as tkfont
from typing import List
import logging

from strength_checker import analyze_password, score_password
from reuse_detector import detect_reuse
from generator import generate_password
from storage import save_passwords, load_passwords


log = logging.getLogger(__name__)


class PasswordHealthAnalyzerApp(tk.Tk):
    """Main application window for Password Health Analyzer."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Password Health Analyzer")
        self.geometry("800x600")
        self.minsize(700, 500)
        self.passwords: List[str] = []
        self.dark_mode_var = tk.BooleanVar(value=False)
        self.default_font = tkfont.Font(family="Arial", size=11)
        self._apply_modern_theme()
        self._build_ui()
        self._bind_shortcuts()

    def _apply_modern_theme(self) -> None:
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.colors = {
            "bg": "#f5f6f8",
            "fg": "#1f2937",
            "muted": "#6b7280",
            "primary": "#4f46e5",
            "primary_hover": "#4338ca",
            "secondary": "#0ea5e9",
            "secondary_hover": "#0284c7",
            "success": "#22c55e",
            "danger": "#ef4444",
            "surface": "#ffffff",
        }
        self.configure(bg=self.colors["bg"]) 
        self.style.configure("TFrame", background=self.colors["bg"]) 
        self.style.configure("TLabelframe", background=self.colors["bg"], borderwidth=1, relief="solid")
        self.style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["fg"], font=("Segoe UI", 11, "bold"))
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"]) 
        self.style.configure("TCheckbutton", background=self.colors["bg"], foreground=self.colors["fg"]) 
        self.style.configure("TEntry", fieldbackground=self.colors["surface"]) 
        self.style.configure("Primary.TButton", background=self.colors["primary"], foreground="#ffffff", padding=8) 
        self.style.map("Primary.TButton", background=[("active", self.colors["primary_hover"])])
        self.style.configure("Secondary.TButton", background=self.colors["secondary"], foreground="#ffffff", padding=8)
        self.style.map("Secondary.TButton", background=[("active", self.colors["secondary_hover"])])
        self.style.configure("Danger.TButton", background=self.colors["danger"], foreground="#ffffff", padding=8)
        self.style.map("Danger.TButton", background=[("active", "#dc2626")])
        self.style.configure("Horizontal.TProgressbar", background=self.colors["success"]) 
        self.style.configure("ToolTip.TLabel", background=self.colors["surface"], foreground=self.colors["fg"], borderwidth=1, relief="solid", padding=6)

    def _build_ui(self) -> None:
        hud = ttk.Frame(self)
        hud.pack(fill="x", padx=12, pady=(12, 0))
        self.title_label = ttk.Label(hud, text="Password Health Analyzer", font=("Segoe UI", 20, "bold"))
        self.title_label.pack(side="left")

        input_frame = ttk.LabelFrame(self, text="Add Password")
        input_frame.pack(fill="x", padx=12, pady=8)

        self.password_entry = ttk.Entry(input_frame)
        self.password_entry.pack(fill="x", padx=12, pady=12)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=12, pady=4)

        add_btn = ttk.Button(btn_frame, text="Add Password", command=self.add_password, style="Primary.TButton")
        add_btn.pack(side="left")

        analyze_btn = ttk.Button(btn_frame, text="Analyze Strength", command=self.analyze_last_password, style="Secondary.TButton")
        analyze_btn.pack(side="left", padx=(8, 0))

        reuse_btn = ttk.Button(btn_frame, text="Check Reuses", command=self.check_reuse_all, style="Secondary.TButton")
        reuse_btn.pack(side="left", padx=(8, 0))

        clear_btn = ttk.Button(btn_frame, text="Clear List", command=self.clear_list, style="Danger.TButton")
        clear_btn.pack(side="left", padx=(8, 0))

        save_btn = ttk.Button(btn_frame, text="Save List", command=self.save_list, style="Primary.TButton")
        save_btn.pack(side="left", padx=(8, 0))

        load_btn = ttk.Button(btn_frame, text="Load List", command=self.load_list, style="Primary.TButton")
        load_btn.pack(side="left", padx=(8, 0))

        dark_mode_btn = ttk.Checkbutton(btn_frame, text="Dark Mode", variable=self.dark_mode_var, command=self._toggle_dark_mode)
        dark_mode_btn.pack(side="left", padx=(8, 0))

        self.strength_label = tk.Label(btn_frame, text="Score: -", font=("Segoe UI", 12))
        self.strength_label.pack(side="right")

        gen_frame = ttk.LabelFrame(self, text="Generate Password")
        gen_frame.pack(fill="x", padx=12, pady=8)

        self.length_var = tk.IntVar(value=16)
        self.use_upper_var = tk.BooleanVar(value=True)
        self.use_lower_var = tk.BooleanVar(value=True)
        self.use_digits_var = tk.BooleanVar(value=True)
        self.use_symbols_var = tk.BooleanVar(value=True)

        ttk.Label(gen_frame, text="Length").pack(side="left", padx=(8, 4))
        self.length_spin = tk.Spinbox(gen_frame, from_=8, to=128, textvariable=self.length_var, width=5)
        self.length_spin.pack(side="left")

        ttk.Checkbutton(gen_frame, text="Upper", variable=self.use_upper_var).pack(side="left", padx=6)
        ttk.Checkbutton(gen_frame, text="Lower", variable=self.use_lower_var).pack(side="left", padx=6)
        ttk.Checkbutton(gen_frame, text="Digits", variable=self.use_digits_var).pack(side="left", padx=6)
        ttk.Checkbutton(gen_frame, text="Symbols", variable=self.use_symbols_var).pack(side="left", padx=6)

        gen_btn = ttk.Button(gen_frame, text="Generate Password", command=self.generate_password_action, style="Primary.TButton")
        gen_btn.pack(side="left", padx=8)

        copy_btn = ttk.Button(gen_frame, text="Copy", command=self.copy_generated_to_clipboard, style="Secondary.TButton")
        copy_btn.pack(side="left")

        self.last_generated: str | None = None

        list_frame = ttk.LabelFrame(self, text="Stored Passwords")
        list_frame.pack(fill="both", padx=12, pady=8, expand=True)

        list_inner = ttk.Frame(list_frame)
        list_inner.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(list_inner, height=6, exportselection=False)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(list_inner, orient="vertical", command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=sb.set)

        list_btns = ttk.Frame(self)
        list_btns.pack(fill="x", padx=12, pady=(0, 8))
        edit_btn = ttk.Button(list_btns, text="Edit Selected", command=self.edit_selected, style="Secondary.TButton")
        edit_btn.pack(side="left")
        remove_btn = ttk.Button(list_btns, text="Remove Selected", command=self.remove_selected, style="Danger.TButton")
        remove_btn.pack(side="left", padx=(8, 0))

        results_frame = ttk.LabelFrame(self, text="Results")
        results_frame.pack(fill="both", padx=12, pady=8, expand=True)

        self.progress = ttk.Progressbar(results_frame, mode="indeterminate")
        self.progress.pack(fill="x", padx=8, pady=(8, 0))

        self.results_text = tk.Text(results_frame, height=16, wrap="none", state="disabled")
        self.results_text.pack(fill="both", padx=8, pady=8, expand=True)
        self._style_text_widgets()
        # Removed the fake timer as it's not essential for a modern UI

        self._add_tooltips({
            add_btn: "Add the password to the list",
            analyze_btn: "Analyze the strength of the last added password",
            reuse_btn: "Check for password reuses in the list",
            clear_btn: "Clear the password list",
            save_btn: "Save the password list (encrypted)",
            load_btn: "Load a saved password list",
            gen_btn: "Generate a new secure password",
            copy_btn: "Copy the generated password to clipboard",
            edit_btn: "Edit the selected password",
            remove_btn: "Remove the selected password",
        })

    def add_password(self) -> None:
        pwd = self.password_entry.get().strip()
        if not pwd:
            messagebox.showinfo("Empty", "Enter a password to add.")
            return
        self.passwords.append(pwd)
        self.refresh_listbox()
        self.password_entry.delete(0, "end")
        log.info("Added password; total=%d", len(self.passwords))

    def analyze_last_password(self) -> None:
        if not self.passwords:
            messagebox.showinfo("No Passwords", "Add passwords first.")
            return
        pwd = self.passwords[-1]
        res = analyze_password(pwd)
        s = res["score"]
        self._set_strength_label(s)
        details = (
            f"Strength: {s}/10\n"
            f"Entropy: {res['entropy_bits']} bits\n"
            f"Length: {res['length']}\n"
            f"Categories: {res['categories']}\n"
            f"Common: {res['common']}\n"
            f"Sequence: {res['sequence']}\n"
            f"Keyboard: {res['keyboard']}\n"
            f"Repeats: {res['repeats']}"
        )
        self._set_results(details)
        log.info("Analyzed last; score=%d", s)

    def check_reuse_all(self) -> None:
        if not self.passwords:
            messagebox.showinfo("No Passwords", "Add passwords first.")
            return
        self.progress.start()
        self.update_idletasks()
        try:
            res = detect_reuse(self.passwords)
            out = "Reuse Check:\n"
            if res["exact"]:
                out += "Exact duplicates:\n"
                for p, c in res["exact"].items():
                    out += f" - '{self._mask(p)}' used {c} times\n"
            else:
                out += "No exact duplicates.\n"
            if res["similar"]:
                out += "Similar passwords:\n"
                for a, b, sim in res["similar"]:
                    out += f" - '{self._mask(a)}' ~ '{self._mask(b)}' ({sim:.2f})\n"
            else:
                out += "No similar passwords.\n"
            self._set_results(out)
            log.info("Reuse check done; exact=%d similar=%d", len(res["exact"]), len(res["similar"]))
        finally:
            self.progress.stop()

    def clear_list(self) -> None:
        self.passwords.clear()
        self.refresh_listbox()
        self._set_results("List cleared.")
        log.info("Cleared list")

    def _set_results(self, text: str) -> None:
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("end", text)
        self.results_text.config(state="disabled")

    def _set_strength_label(self, score: int) -> None:
        self.strength_label.config(text=f"Score: {score}/10")

    def _style_text_widgets(self) -> None:
        self.results_text.config(font=self.default_font, bg=self.colors["surface"], fg=self.colors["fg"], relief="solid", bd=1)
        self.listbox.config(font=self.default_font, bg=self.colors["surface"], fg=self.colors["fg"], relief="solid", bd=1)

    def _toggle_dark_mode(self) -> None:
        val = self.dark_mode_var.get()
        if val:
            self.colors.update({
                "bg": "#121212",
                "fg": "#f3f4f6",
                "muted": "#9ca3af",
                "primary": "#6366f1",
                "primary_hover": "#4f46e5",
                "secondary": "#38bdf8",
                "secondary_hover": "#0ea5e9",
                "success": "#22c55e",
                "danger": "#f87171",
                "surface": "#1f2937",
            })
        else:
            self.colors.update({
                "bg": "#f5f6f8",
                "fg": "#1f2937",
                "muted": "#6b7280",
                "primary": "#4f46e5",
                "primary_hover": "#4338ca",
                "secondary": "#0ea5e9",
                "secondary_hover": "#0284c7",
                "success": "#22c55e",
                "danger": "#ef4444",
                "surface": "#ffffff",
            })
        self.configure(bg=self.colors["bg"]) 
        self.style.configure("TFrame", background=self.colors["bg"]) 
        self.style.configure("TLabelframe", background=self.colors["bg"], borderwidth=1, relief="solid")
        self.style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["fg"], font=("Segoe UI", 11, "bold"))
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"]) 
        self.style.configure("TCheckbutton", background=self.colors["bg"], foreground=self.colors["fg"]) 
        self.style.configure("TEntry", fieldbackground=self.colors["surface"]) 
        self.style.configure("Primary.TButton", background=self.colors["primary"], foreground="#ffffff", padding=8) 
        self.style.map("Primary.TButton", background=[("active", self.colors["primary_hover"])])
        self.style.configure("Secondary.TButton", background=self.colors["secondary"], foreground="#ffffff", padding=8)
        self.style.map("Secondary.TButton", background=[("active", self.colors["secondary_hover"])])
        self.style.configure("Danger.TButton", background=self.colors["danger"], foreground="#ffffff", padding=8)
        self.style.map("Danger.TButton", background=[("active", "#dc2626")])
        self.style.configure("Horizontal.TProgressbar", background=self.colors["success"]) 
        self.style.configure("ToolTip.TLabel", background=self.colors["surface"], foreground=self.colors["fg"]) 
        self.results_text.config(bg=self.colors["surface"], fg=self.colors["fg"]) 
        self.listbox.config(bg=self.colors["surface"], fg=self.colors["fg"]) 
        self.strength_label.config(bg=self.colors["bg"], fg=self.colors["fg"]) 
        self.title_label.config(foreground=self.colors["fg"]) 

    def save_list(self) -> None:
        if not self.passwords:
            messagebox.showinfo("Empty List", "No passwords to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pha", filetypes=[("Encrypted", "*.pha"), ("All Files", "*.*")])
        if not path:
            return
        master = simpledialog.askstring("Master Password", "Enter master password:", show="*")
        if not master:
            return
        try:
            save_passwords(path, self.passwords, master)
            self._set_results(f"Encrypted list saved to {path}")
            messagebox.showinfo("Saved", f"Encrypted list saved to {path}")
            log.info("Saved encrypted list to %s", path)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            log.error("Save failed: %s", e)

    def load_list(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Encrypted", "*.pha"), ("All Files", "*.*")])
        if not path:
            return
        master = simpledialog.askstring("Master Password", "Enter master password:", show="*")
        if not master:
            return
        try:
            loaded = load_passwords(path, master)
            self.passwords = loaded
            self._set_results(f"Loaded {len(loaded)} password(s) from encrypted file.")
            messagebox.showinfo("Loaded", f"Encrypted list loaded from {path}")
            self.refresh_listbox()
            log.info("Loaded encrypted list from %s; count=%d", path, len(loaded))
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            log.error("Load failed: %s", e)

    def refresh_listbox(self) -> None:
        self.listbox.delete(0, "end")
        for p in self.passwords:
            self.listbox.insert("end", self._mask(p))

    def edit_selected(self) -> None:
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a password to edit.")
            return
        idx = sel[0]
        new = simpledialog.askstring("Edit Password", "Enter new password:", show="*")
        if not new:
            return
        self.passwords[idx] = new.strip()
        self.refresh_listbox()

    def remove_selected(self) -> None:
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a password to remove.")
            return
        idx = sel[0]
        del self.passwords[idx]
        self.refresh_listbox()

    def _mask(self, s: str) -> str:
        return "•" * len(s)

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-a>", lambda e: self.add_password())
        self.bind("<Control-e>", lambda e: self.analyze_last_password())
        self.bind("<Control-r>", lambda e: self.check_reuse_all())
        self.bind("<Control-l>", lambda e: self.clear_list())
        self.bind("<Control-s>", lambda e: self.save_list())
        self.bind("<Control-o>", lambda e: self.load_list())
        self.bind("<Control-g>", lambda e: self.generate_password_action())
        self.bind("<Control-c>", lambda e: self.copy_generated_to_clipboard())
        self.bind("<F2>", lambda e: self._toggle_dark_mode())

    def _add_tooltips(self, mapping: dict) -> None:
        for w, text in mapping.items():
            _Tooltip(w, text, "ToolTip.TLabel")

    def generate_password_action(self) -> None:
        try:
            pwd = generate_password(
                length=int(self.length_var.get()),
                use_upper=bool(self.use_upper_var.get()),
                use_lower=bool(self.use_lower_var.get()),
                use_digits=bool(self.use_digits_var.get()),
                use_symbols=bool(self.use_symbols_var.get()),
            )
        except Exception as e:
            messagebox.showerror("Generate Error", str(e))
            log.error("Generate error: %s", e)
            return
        self.last_generated = pwd
        s = score_password(pwd)
        self._set_strength_label(s)
        self._set_results(f"Generated: {pwd}\nStrength: {s}/10")
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, pwd)
        log.info("Generated password; length=%d", len(pwd))

    def copy_generated_to_clipboard(self) -> None:
        if not self.last_generated:
            messagebox.showinfo("No Password", "Generate a password first.")
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(self.last_generated)
            self.update()
            messagebox.showinfo("Copied", "Generated password copied to clipboard.")
            log.info("Copied generated password to clipboard")
        except Exception as e:
            messagebox.showerror("Clipboard Error", str(e))
            log.error("Clipboard error: %s", e)


class _Tooltip:
    """Lightweight tooltip attached to a widget."""

    def __init__(self, widget, text: str, style_name: str | None = None):
        self.widget = widget
        self.text = text
        self.tip = None
        self.style_name = style_name
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        if self.style_name:
            lbl = ttk.Label(self.tip, text=self.text, style=self.style_name, relief="solid")
        else:
            lbl = ttk.Label(self.tip, text=self.text, padding=4, relief="solid")
        lbl.pack()

    def _hide(self, _):
        if self.tip:
            self.tip.destroy()
            self.tip = None
