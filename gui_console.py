"""tkinter GUI for the Tax Automation Suite server console.

Ship with PyInstaller:  pyinstaller --onefile --windowed --name TaxSuiteGUI gui_console.py
Reuses the actions from server_console.py (start/stop/status/backup/restore).
"""

import re
import threading
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk

import server_console as sc
from server_console import BACKUP_DIR, URL

_ANSI = re.compile(r"\033\[[0-9;]*m")

COLOR_RUNNING = "#198754"
COLOR_STALE = "#b45309"
COLOR_STOPPED = "#6c757d"


class ServerConsoleGUI:
    def __init__(self, root):
        self.root = root
        root.title("Tax Automation Suite - Server Console")
        root.geometry("620x460")
        root.minsize(520, 380)

        self._log_pos = 0
        self._last_state = None

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._poll()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main)
        header.pack(fill="x")

        ttk.Label(
            header, text="Tax Automation Suite",
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")

        self.status_label = ttk.Label(
            header, text="Status: checking\u2026",
            font=("Segoe UI", 11, "bold"),
            foreground=COLOR_STOPPED,
        )
        self.status_label.pack(side="right")
        ttk.Label(
            header, text=URL, font=("Segoe UI", 9),
            foreground="#6c757d",
        ).pack(side="right", padx=12)

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=(14, 8))

        self.btn_start = ttk.Button(buttons, text="Start Server", command=self._start)
        self.btn_stop = ttk.Button(buttons, text="Stop Server", command=self._stop)
        self.btn_browser = ttk.Button(buttons, text="Open in Browser", command=self._open_browser)
        self.btn_backup = ttk.Button(buttons, text="Backup", command=self._backup)
        self.btn_restore = ttk.Button(buttons, text="Restore\u2026", command=self._restore)

        self.btn_start.pack(side="left", padx=(0, 6))
        self.btn_stop.pack(side="left", padx=6)
        self.btn_browser.pack(side="left", padx=6)
        self.btn_backup.pack(side="left", padx=(12, 6))
        self.btn_restore.pack(side="left", padx=6)

        log_frame = ttk.Frame(main)
        log_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.log_text = tk.Text(
            log_frame, height=12, wrap="word", state="disabled",
            font=("Consolas", 9), bg="#111318", fg="#d7dae0",
            insertbackground="#d7dae0",
        )
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.log_text.tag_configure("info", foreground="#d7dae0")
        self.log_text.tag_configure("ok", foreground="#2ecc71")
        self.log_text.tag_configure("warn", foreground="#f1c40f")
        self.log_text.tag_configure("err", foreground="#e74c3c")
        self.log_text.tag_configure("server", foreground="#7fa8d9")

        self._log("Console ready. Project: " + str(BACKUP_DIR), "info")

    # ---------------------------------------------------------------- utils
    def _log(self, message, tag="info"):
        message = _ANSI.sub("", str(message))
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _busy(self, busy):
        state = "disabled" if busy else "normal"
        for btn in (self.btn_start, self.btn_stop, self.btn_browser,
                    self.btn_backup, self.btn_restore):
            btn.configure(state=state)

    # -------------------------------------------------------------- poller
    def _poll(self):
        ok, msg = sc.server_status()
        message = _ANSI.sub("", msg)

        if "RUNNING" in message:
            state = "running"
            label = message
            color = COLOR_RUNNING
        elif "STALE" in message:
            state = "stale"
            label = message
            color = COLOR_STALE
        else:
            state = "stopped"
            label = message
            color = COLOR_STOPPED

        self.status_label.configure(text=label, foreground=color)

        if state != self._last_state:
            self._log(message, "ok" if state == "running"
                      else ("warn" if state == "stale" else "info"))
            self._last_state = state

        self._tail_log()
        self.root.after(2000, self._poll)

    def _tail_log(self):
        try:
            log_file = BACKUP_DIR.parent / "server.log"
            with open(log_file, "rb") as fh:
                fh.seek(self._log_pos)
                data = fh.read()
                self._log_pos = fh.tell()
            if data:
                text = data.decode("utf-8", "replace").rstrip()
                for line in text.splitlines():
                    if line.strip():
                        self._log(line, "server")
        except OSError:
            pass

    # ------------------------------------------------------------- actions
    def _start(self):
        self._busy(True)
        self._log("Starting server\u2026", "info")
        threading.Thread(target=self._start_worker, daemon=True).start()

    def _start_worker(self):
        ok, msg = sc.start_server()
        self.root.after(0, lambda: (self._log(msg, "ok" if ok else "err"),
                                    self._busy(False)))

    def _stop(self):
        self._busy(True)
        self._log("Stopping server\u2026", "info")
        threading.Thread(target=self._stop_worker, daemon=True).start()

    def _stop_worker(self):
        ok, msg = sc.stop_server()
        self.root.after(0, lambda: (self._log(msg, "ok" if ok else "warn"),
                                    self._busy(False)))

    def _open_browser(self):
        webbrowser.open(URL)

    def _backup(self):
        self._busy(True)
        threading.Thread(target=self._backup_worker, daemon=True).start()

    def _backup_worker(self):
        ok, msg = sc.create_backup()
        self.root.after(0, lambda: (self._log(msg, "ok" if ok else "err"),
                                    self._busy(False)))

    def _restore(self):
        path = filedialog.askopenfilename(
            initialdir=str(BACKUP_DIR),
            title="Select a backup",
            filetypes=[("Backup archive", "backup-*.zip"), ("All files", "*.*")],
        )
        if not path:
            return
        if not messagebox.askyesno(
            "Restore backup",
            f"Restore from '{path.split(chr(92))[-1]}'?\n"
            "This overwrites the current credentials.",
            icon="warning",
        ):
            return
        self._busy(True)
        threading.Thread(target=self._restore_worker, args=(path,), daemon=True).start()

    def _restore_worker(self, path):
        ok, msg = sc.perform_restore(path)
        self.root.after(0, lambda: (self._log(msg, "ok" if ok else "err"),
                                    self._busy(False)))

    def _on_close(self):
        if sc.running_pid():
            answer = messagebox.askyesnocancel(
                "Server is running",
                "The web server is still running.\n\n"
                "Yes = stop the server, No = keep it running, Cancel = go back.",
            )
            if answer is None:
                return
            if answer:
                ok, msg = sc.stop_server()
                self._log(msg, "ok" if ok else "warn")
        self.root.destroy()


def main():
    root = tk.Tk()
    ServerConsoleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()