#!/usr/bin/env python3
"""
╔═══════════════════════════════════════╗
║  YouTube Downloader  ·  Premium v4   ║
║  Free · Unlimited · With Sound       ║
╚═══════════════════════════════════════╝
"""
import subprocess, sys, os

def _pip(pkg):
    subprocess.check_call([sys.executable,"-m","pip","install",pkg,"-q"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for _p,_i in [("yt-dlp","yt_dlp"),("static-ffmpeg","static_ffmpeg")]:
    try: __import__(_i)
    except: print(f"  Installing {_p}…"); _pip(_p)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading, re, json, hashlib, datetime, time
import yt_dlp, static_ffmpeg, shutil

static_ffmpeg.add_paths()
FFMPEG = shutil.which("ffmpeg") or ""

# ── Paths ─────────────────────────────────────────────────────────────────────
APP_DIR   = os.path.join(os.path.expanduser("~"), ".ytdl_app")
ACCS_FILE = os.path.join(APP_DIR, "accounts.json")
HIST_FILE = os.path.join(APP_DIR, "history.json")
SESS_FILE = os.path.join(APP_DIR, "session.json")
os.makedirs(APP_DIR, exist_ok=True)

def jload(p,d):
    try:
        with open(p) as f: return json.load(f)
    except: return d
def jsave(p,d):
    with open(p,"w") as f: json.dump(d,f,indent=2)
def hashpw(pw): return hashlib.sha256(pw.encode()).hexdigest()

# ── Design tokens ─────────────────────────────────────────────────────────────
C = {
    "bg":      "#080808",
    "bg2":     "#0e0e0e",
    "card":    "#131313",
    "card2":   "#191919",
    "s3":      "#202020",
    "s4":      "#282828",
    "bdr":     "#242424",
    "bdr2":    "#2e2e2e",
    "red":     "#e03030",
    "redh":    "#f54545",
    "redf":    "#1e0808",
    "grn":     "#1db954",
    "ylw":     "#e8a020",
    "blue":    "#3b82f6",
    "fg":      "#ececec",
    "fg2":     "#707070",
    "fg3":     "#3a3a3a",
    "fg4":     "#222222",
    "white":   "#ffffff",
}

# Fonts — tight, clean, monospace accents
FH  = ("Helvetica", 20, "bold")   # hero
FT  = ("Helvetica", 12, "bold")   # title
FM  = ("Helvetica", 10, "bold")   # medium
FN  = ("Helvetica", 9)            # normal
FS  = ("Helvetica", 8)            # small
FB  = ("Helvetica", 8, "bold")    # small bold
FCo = ("Courier New", 8)          # mono


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED WIDGET HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def btn(parent, text, cmd, bg=None, fg=None, hbg=None, font=None,
        px=14, py=6, side=None, **kw):
    _bg  = bg  or C["s3"]
    _fg  = fg  or C["fg2"]
    _hbg = hbg or C["s4"]
    b = tk.Button(parent, text=text, command=cmd,
                  bg=_bg, fg=_fg, activebackground=_hbg, activeforeground=_fg,
                  font=font or FN, relief="flat", bd=0, cursor="hand2",
                  padx=px, pady=py, **kw)
    if side: b.pack(side=side, padx=(4,0))
    b.bind("<Enter>", lambda e: b.config(bg=_hbg))
    b.bind("<Leave>", lambda e: b.config(bg=_bg))
    return b

def redbtn(parent, text, cmd, font=None, px=18, py=8, **kw):
    return btn(parent, text, cmd,
               bg=C["red"], fg=C["white"], hbg=C["redh"],
               font=font or FM, px=px, py=py, **kw)

def card(parent, pady=12, padx=16):
    f = tk.Frame(parent, bg=C["card"],
                 highlightbackground=C["bdr"], highlightthickness=1)
    f.pack(fill="x", padx=14, pady=(0,8))
    inner = tk.Frame(f, bg=C["card"], padx=padx, pady=pady)
    inner.pack(fill="both", expand=True)
    return inner

def label(parent, text, font=None, fg=None, bg=None, **kw):
    return tk.Label(parent, text=text, font=font or FN,
                    fg=fg or C["fg2"], bg=bg or C["card"], **kw)

def tiny_label(parent, text, bg=None):
    return tk.Label(parent, text=text.upper(), font=FB,
                    fg=C["fg3"], bg=bg or C["card"])

def entry(parent, var, font=None, show="", width=None):
    kw = dict(textvariable=var, font=font or FN,
              bg=C["s3"], fg=C["fg"], insertbackground=C["red"],
              relief="flat", bd=0, show=show,
              highlightthickness=1,
              highlightbackground=C["bdr"],
              highlightcolor=C["red"])
    if width: kw["width"] = width
    return tk.Entry(parent, **kw)

def separator(parent, bg=None):
    tk.Frame(parent, bg=bg or C["bdr"], height=1).pack(fill="x", padx=14, pady=4)

def dropdown(parent, var, options, width=16):
    """Styled OptionMenu"""
    om = tk.OptionMenu(parent, var, *options)
    om.config(bg=C["s3"], fg=C["fg"],
              activebackground=C["s4"], activeforeground=C["fg"],
              relief="flat", bd=0, cursor="hand2",
              font=FN, highlightthickness=0,
              width=width, indicatoron=True)
    om["menu"].config(bg=C["s3"], fg=C["fg"],
                      activebackground=C["red"],
                      activeforeground=C["white"],
                      font=FN, relief="flat", bd=0)
    return om

def progress_canvas(parent):
    c = tk.Canvas(parent, height=4, bg=C["s3"],
                  highlightthickness=0)
    c.pack(fill="x", pady=(4,0))
    return c

def draw_bar(canvas, pct, color=None):
    canvas.delete("bar")
    w = canvas.winfo_width()
    if w > 1 and pct > 0:
        canvas.create_rectangle(
            0, 0, int(w * pct / 100), 4,
            fill=color or C["red"], outline="", tags="bar")


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
class LoginWin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("400x560")
        self.resizable(False, False)
        self.configure(bg=C["bg"])
        self._center(400, 560)
        self._accounts = jload(ACCS_FILE, {})
        self._mode = "login"
        self._build()

    def _center(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        # Red top stripe
        tk.Frame(self, bg=C["red"], height=3).pack(fill="x")

        # Logo area
        logo_frame = tk.Frame(self, bg=C["bg"], pady=28)
        logo_frame.pack(fill="x")

        # Canvas logo
        cv = tk.Canvas(logo_frame, width=48, height=36,
                       bg=C["bg"], highlightthickness=0)
        cv.pack()
        cv.create_rectangle(0, 0, 48, 36, fill=C["red"], outline="")
        cv.create_polygon(19,8, 19,28, 38,18, fill=C["white"])

        tk.Label(logo_frame, text="YouTube Downloader",
                 font=("Helvetica",13,"bold"),
                 bg=C["bg"], fg=C["fg"]).pack(pady=(8,0))
        tk.Label(logo_frame, text="free  ·  unlimited  ·  with sound",
                 font=FS, bg=C["bg"], fg=C["fg3"]).pack()

        # Card
        self._box = tk.Frame(self, bg=C["card"],
                             highlightbackground=C["bdr"], highlightthickness=1)
        self._box.pack(fill="x", padx=30, pady=(4,0))
        inner = tk.Frame(self._box, bg=C["card"], padx=24, pady=20)
        inner.pack(fill="both")
        self._inner = inner

        self._title = tk.Label(inner, text="Sign in",
                               font=FT, bg=C["card"], fg=C["fg"])
        self._title.pack(anchor="w", pady=(0,14))

        # Name (register only)
        self._name_frame = tk.Frame(inner, bg=C["card"])
        tiny_label(self._name_frame, "Full Name").pack(anchor="w", pady=(0,3))
        self._inp_name = entry(self._name_frame, tk.StringVar())
        self._inp_name.pack(fill="x", ipady=7, pady=(0,10))

        # Email
        tiny_label(inner, "Email").pack(anchor="w", pady=(0,3))
        self._email_v = tk.StringVar()
        e_email = entry(inner, self._email_v)
        e_email.pack(fill="x", ipady=7, pady=(0,10))
        e_email.bind("<Return>", lambda e: self._action())

        # Password
        tiny_label(inner, "Password").pack(anchor="w", pady=(0,3))
        self._pw_v = tk.StringVar()
        e_pw = entry(inner, self._pw_v, show="●")
        e_pw.pack(fill="x", ipady=7, pady=(0,4))
        e_pw.bind("<Return>", lambda e: self._action())

        # Confirm pw (register)
        self._cpw_frame = tk.Frame(inner, bg=C["card"])
        tiny_label(self._cpw_frame, "Confirm Password").pack(anchor="w", pady=(8,3))
        self._cpw_v = tk.StringVar()
        entry(self._cpw_frame, self._cpw_v, show="●").pack(fill="x", ipady=7)

        # Error
        self._err = tk.Label(inner, text="", font=FS,
                             bg=C["card"], fg=C["red"], wraplength=300, anchor="w")
        self._err.pack(fill="x", pady=(6,0))

        # Main button
        self._main_btn = redbtn(inner, "Sign In", self._action, py=9)
        self._main_btn.pack(fill="x", pady=(10,0))

        # Divider
        div = tk.Frame(inner, bg=C["card"])
        div.pack(fill="x", pady=(12,12))
        tk.Frame(div, bg=C["bdr2"], height=1).pack(side="left", fill="x", expand=True, pady=6)
        tk.Label(div, text="  or  ", font=FS, bg=C["card"], fg=C["fg3"]).pack(side="left")
        tk.Frame(div, bg=C["bdr2"], height=1).pack(side="left", fill="x", expand=True, pady=6)

        # Google
        g = btn(inner, "  Continue with Google  ", self._google_flow,
                bg=C["s3"], fg=C["fg"], hbg=C["s4"], font=FN, px=0, py=9)
        g.pack(fill="x")

        # Toggle
        tog = tk.Frame(self, bg=C["bg"])
        tog.pack(pady=14)
        self._tog_lbl = tk.Label(tog, text="No account?",
                                  font=FN, bg=C["bg"], fg=C["fg3"])
        self._tog_lbl.pack(side="left")
        tl = tk.Label(tog, text=" Create one", font=FM,
                      bg=C["bg"], fg=C["red"], cursor="hand2")
        tl.pack(side="left")
        tl.bind("<Button-1>", lambda e: self._toggle())
        self._tog_link = tl

    def _toggle(self):
        is_reg = self._mode == "login"
        self._mode = "register" if is_reg else "login"
        if is_reg:
            self._title.config(text="Create account")
            self._main_btn.config(text="Create Account")
            self._tog_lbl.config(text="Already have one?")
            self._tog_link.config(text=" Sign in")
            self._name_frame.pack(before=self._inner.winfo_children()[1])
            self._cpw_frame.pack(after=self._err)
        else:
            self._title.config(text="Sign in")
            self._main_btn.config(text="Sign In")
            self._tog_lbl.config(text="No account?")
            self._tog_link.config(text=" Create one")
            self._name_frame.pack_forget()
            self._cpw_frame.pack_forget()
        self._err.config(text="")

    def _set_err(self, msg):
        self._err.config(text=msg)

    def _action(self):
        self._set_err("")
        email = self._email_v.get().strip().lower()
        pw    = self._pw_v.get()
        if not email or "@" not in email:
            self._set_err("Enter a valid email address."); return
        if not pw:
            self._set_err("Enter your password."); return

        if self._mode == "register":
            name = self._inp_name.get().strip()
            cpw  = self._cpw_v.get()
            if not name: self._set_err("Enter your name."); return
            if len(pw) < 6: self._set_err("Password must be 6+ characters."); return
            if pw != cpw:   self._set_err("Passwords don't match."); return
            if email in self._accounts:
                self._set_err("Account already exists. Sign in instead."); return
            self._accounts[email] = {
                "name": name, "pw_hash": hashpw(pw),
                "joined": str(datetime.date.today()), "method": "email"
            }
            jsave(ACCS_FILE, self._accounts)
            self._launch(email)
        else:
            if email not in self._accounts:
                self._set_err("No account found with this email."); return
            if self._accounts[email].get("pw_hash") != hashpw(pw):
                self._set_err("Wrong password."); return
            self._launch(email)

    def _google_flow(self):
        dlg = tk.Toplevel(self)
        dlg.title("Google Sign-In")
        dlg.geometry("340x220")
        dlg.resizable(False, False)
        dlg.configure(bg=C["card"])
        dlg.transient(self); dlg.grab_set()
        x = self.winfo_rootx() + (400-340)//2
        y = self.winfo_rooty() + (560-220)//2
        dlg.geometry(f"340x220+{x}+{y}")
        tk.Frame(dlg, bg=C["blue"], height=3).pack(fill="x")
        inner = tk.Frame(dlg, bg=C["card"], padx=22, pady=18)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text="Continue with Google",
                 font=FM, bg=C["card"], fg=C["fg"]).pack(anchor="w")
        tk.Label(inner, text="Enter your Gmail address",
                 font=FN, bg=C["card"], fg=C["fg3"]).pack(anchor="w", pady=(3,10))
        gv = tk.StringVar()
        ge = entry(inner, gv)
        ge.pack(fill="x", ipady=7)
        ge.focus_set()
        errl = tk.Label(inner, text="", font=FS, bg=C["card"], fg=C["red"])
        errl.pack(anchor="w", pady=(4,0))
        def _confirm():
            em = gv.get().strip().lower()
            if not em or "@" not in em:
                errl.config(text="Enter a valid Gmail."); return
            if em not in self._accounts:
                gname = em.split("@")[0].replace("."," ").title()
                self._accounts[em] = {
                    "name": gname, "pw_hash": "",
                    "joined": str(datetime.date.today()), "method": "google"
                }
                jsave(ACCS_FILE, self._accounts)
            dlg.destroy()
            self._launch(em)
        b = btn(inner, "Continue", _confirm,
                bg=C["blue"], fg=C["white"], hbg="#5a9bff",
                font=FM, px=0, py=9)
        b.pack(fill="x", pady=(10,0))
        ge.bind("<Return>", lambda e: _confirm())

    def _launch(self, email):
        u = self._accounts[email]
        jsave(SESS_FILE, {"email": email, "name": u["name"],
                          "method": u.get("method","email")})
        self.destroy()
        MainApp(email, u["name"], u.get("method","email")).mainloop()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════
class MainApp(tk.Tk):
    def __init__(self, email, name, method):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("720x640")
        self.minsize(660, 580)
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self._center()

        self._email  = email
        self._name   = name
        self._method = method
        self._hist   = jload(HIST_FILE, [])
        self._busy   = False
        self._job_es = None

        # Load saved prefs for this user
        _accs  = jload(ACCS_FILE, {})
        _prefs = _accs.get(email, {}).get("prefs", {})
        self.savepath = _prefs.get("savepath",
                        jload(SESS_FILE, {}).get("savepath",
                        os.path.join(os.path.expanduser("~"), "Downloads")))

        # Vars — restored from saved prefs
        self.url_v   = tk.StringVar()
        self.mode_v  = tk.StringVar(value=_prefs.get("mode",    "Video"))
        self.qual_v  = tk.StringVar(value=_prefs.get("quality", "Best (Max Quality)"))
        self.fmt_v   = tk.StringVar(value=_prefs.get("format",  "mp4"))
        self.prog_v  = tk.DoubleVar(value=0)
        self.stat_v  = tk.StringVar(value="Ready")

        # Auto-save prefs whenever any setting changes
        def _save_prefs(*_):
            accs = jload(ACCS_FILE, {})
            if email in accs:
                accs[email]["prefs"] = {
                    "mode":     self.mode_v.get(),
                    "quality":  self.qual_v.get(),
                    "format":   self.fmt_v.get(),
                    "savepath": self.savepath,
                }
                jsave(ACCS_FILE, accs)
        self._save_prefs = _save_prefs
        self.mode_v.trace_add("write", _save_prefs)
        self.qual_v.trace_add("write", _save_prefs)
        self.fmt_v.trace_add("write",  _save_prefs)

        self._build()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 720) // 2
        y = (self.winfo_screenheight() - 640) // 2
        self.geometry(f"720x640+{x}+{y}")

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build(self):
        # Thin red top stripe
        tk.Frame(self, bg=C["red"], height=2).pack(fill="x")

        # Header bar
        hdr = tk.Frame(self, bg=C["bg2"], height=46)
        hdr.pack(fill="x"); hdr.pack_propagate(False)

        # Logo
        cv = tk.Canvas(hdr, width=26, height=20,
                       bg=C["bg2"], highlightthickness=0)
        cv.pack(side="left", padx=(14,6), pady=13)
        cv.create_rectangle(0,0,26,20, fill=C["red"], outline="")
        cv.create_polygon(10,4, 10,16, 22,10, fill=C["white"])
        tk.Label(hdr, text="YouTube Downloader",
                 font=FM, bg=C["bg2"], fg=C["fg"]).pack(side="left", pady=13)

        # User chip
        chip = tk.Frame(hdr, bg=C["bg2"])
        chip.pack(side="right", padx=12)
        init = self._name[0].upper()
        av = tk.Canvas(chip, width=24, height=24,
                       bg=C["red"], highlightthickness=0)
        av.pack(side="left", padx=(0,6))
        av.create_text(12,12, text=init, fill=C["white"], font=FM)
        ui = tk.Frame(chip, bg=C["bg2"])
        ui.pack(side="left")
        tk.Label(ui, text=self._name, font=FB,
                 bg=C["bg2"], fg=C["fg"]).pack(anchor="w")
        tk.Label(ui, text=self._email[:28]+("…" if len(self._email)>28 else ""),
                 font=("Helvetica",7), bg=C["bg2"], fg=C["fg3"]).pack(anchor="w")
        so = tk.Label(chip, text="  sign out  ", font=FS,
                      bg=C["bg2"], fg=C["fg3"], cursor="hand2")
        so.pack(side="left", padx=(8,0))
        so.bind("<Button-1>", lambda e: self._signout())

        # Tab bar
        self._tab_bar = tk.Frame(self, bg=C["bg2"],
                                  highlightbackground=C["bdr"], highlightthickness=1)
        self._tab_bar.pack(fill="x")
        self._tabs = {}; self._pages = {}
        for n, icon, lbl in [
            ("download","⬇","Download"),
            ("history", "🕘","History"),
            ("settings","⚙","Settings"),
        ]:
            b = tk.Label(self._tab_bar,
                         text=f"  {icon}  {lbl}  ",
                         font=FN, bg=C["bg2"], fg=C["fg3"],
                         cursor="hand2", pady=8)
            b.pack(side="left")
            b.bind("<Button-1>", lambda e, name=n: self._tab(name))
            self._tabs[n] = b

        # Content
        self._cnt = tk.Frame(self, bg=C["bg"])
        self._cnt.pack(fill="both", expand=True)

        self._pages["download"] = self._pg_download()
        self._pages["history"]  = self._pg_history()
        self._pages["settings"] = self._pg_settings()
        self._tab("download")

    def _tab(self, name):
        for p in self._pages.values(): p.place_forget()
        self._pages[name].place(relwidth=1, relheight=1)
        for n, b in self._tabs.items():
            active = n == name
            b.config(
                fg    = C["fg"]   if active else C["fg3"],
                bg    = C["card"] if active else C["bg2"],
                font  = FB        if active else FN,
            )
        if name == "history":  self._refresh_hist()

    # ── DOWNLOAD PAGE ─────────────────────────────────────────────────────────
    def _pg_download(self):
        pg = tk.Frame(self._cnt, bg=C["bg"])
        scroll = tk.Frame(pg, bg=C["bg"])
        scroll.pack(fill="both", expand=True, pady=(10,0))

        # URL card
        c1 = card(scroll)
        tiny_label(c1, "YouTube URL").pack(anchor="w", pady=(0,5))
        row = tk.Frame(c1, bg=C["card"]); row.pack(fill="x")
        self._url_e = entry(row, self.url_v, font=("Courier New",9))
        self._url_e.pack(side="left", fill="x", expand=True, ipady=8, padx=(0,6))
        self._url_e.bind("<Return>", lambda e: self._start())
        btn(row, "Paste", self._paste, side="left", py=7)
        btn(row, "✕",    lambda: self.url_v.set(""),
            side="left", px=10, py=7)

        # Options card
        c2 = card(scroll)
        tiny_label(c2, "Options").pack(anchor="w", pady=(0,8))
        og = tk.Frame(c2, bg=C["card"]); og.pack(fill="x")

        for lbl, var, opts, w in [
            ("Mode",    self.mode_v,
             ["Video","Audio Only","Playlist — Video","Playlist — Audio"], 20),
            ("Quality", self.qual_v,
             ["Best (Max Quality)","4K","1080p","720p","480p","360p"], 18),
            ("Format",  self.fmt_v,
             ["mp4","mkv","webm","mp3","m4a"], 8),
        ]:
            col = tk.Frame(og, bg=C["card"])
            col.pack(side="left", padx=(0,16))
            tiny_label(col, lbl).pack(anchor="w", pady=(0,4))
            dropdown(col, var, opts, w).pack(anchor="w")

        # Save path card
        c3 = card(scroll)
        tiny_label(c3, "Save Folder").pack(anchor="w", pady=(0,6))
        prow = tk.Frame(c3, bg=C["card"]); prow.pack(fill="x")
        self._pathlbl = tk.Label(prow,
            text=self.savepath, font=FCo,
            bg=C["s3"], fg=C["fg2"], anchor="w",
            padx=10, pady=7, cursor="hand2")
        self._pathlbl.pack(side="left", fill="x", expand=True, padx=(0,6))
        self._pathlbl.bind("<Button-1>", lambda e: self._browse())
        btn(prow, "📁 Change", self._browse, side="left", py=7)

        # Action card
        c4 = card(scroll, pady=14)
        arow = tk.Frame(c4, bg=C["card"]); arow.pack(fill="x")
        self._dl_btn = redbtn(c4, "⬇   DOWNLOAD NOW",
                              self._start, font=("Helvetica",10,"bold"),
                              px=24, py=10)
        self._dl_btn.pack(side="left")
        btn(c4, "Cancel", self._cancel,
            fg=C["fg3"], side="left", px=14, py=10)

        # Progress
        self._pbar = progress_canvas(c4)
        self._pbar.bind("<Configure>", lambda e: self._redraw())

        # Status + speed row
        srow = tk.Frame(c4, bg=C["card"]); srow.pack(fill="x", pady=(5,0))
        self._stat_lbl = tk.Label(srow, textvariable=self.stat_v,
                                   font=FS, bg=C["card"], fg=C["fg2"], anchor="w")
        self._stat_lbl.pack(side="left")
        self._speed_lbl = tk.Label(srow, text="",
                                    font=FCo, bg=C["card"], fg=C["fg3"], anchor="e")
        self._speed_lbl.pack(side="right")

        # Log
        self._log = tk.Text(c4, height=6, bg=C["bg2"],
                             fg=C["fg3"], font=FCo, relief="flat",
                             state="disabled", wrap="word",
                             padx=10, pady=8, spacing1=1)
        self._log.pack(fill="x", pady=(8,0))
        self._log.tag_config("g", foreground=C["grn"])
        self._log.tag_config("r", foreground=C["red"])
        self._log.tag_config("y", foreground=C["ylw"])
        self._log.tag_config("d", foreground=C["fg3"])

        return pg

    # ── HISTORY PAGE ──────────────────────────────────────────────────────────
    def _pg_history(self):
        pg = tk.Frame(self._cnt, bg=C["bg"])

        # Header
        hdr = tk.Frame(pg, bg=C["bg"], padx=14, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Download History",
                 font=FT, bg=C["bg"], fg=C["fg"]).pack(side="left")
        btn(hdr, "🗑 Clear All", self._clr_hist,
            fg=C["fg3"], side="right", py=5)

        # Scrollable list
        wrap = tk.Frame(pg, bg=C["bg"], padx=14)
        wrap.pack(fill="both", expand=True)

        self._hcv = tk.Canvas(wrap, bg=C["bg"], highlightthickness=0)
        sb = tk.Scrollbar(wrap, orient="vertical",
                          command=self._hcv.yview, width=6)
        self._hinn = tk.Frame(self._hcv, bg=C["bg"])

        self._hcv.configure(yscrollcommand=sb.set)
        self._hcv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._hw = self._hcv.create_window((0,0), window=self._hinn, anchor="nw")
        self._hinn.bind("<Configure>",
            lambda e: self._hcv.configure(scrollregion=self._hcv.bbox("all")))
        self._hcv.bind("<Configure>",
            lambda e: self._hcv.itemconfig(self._hw, width=e.width))
        self._hcv.bind_all("<MouseWheel>",
            lambda e: self._hcv.yview_scroll(int(-1*(e.delta/120)), "units"))
        return pg

    def _refresh_hist(self):
        for w in self._hinn.winfo_children(): w.destroy()
        mine = [h for h in self._hist if h.get("user")==self._email]
        if not mine:
            tk.Label(self._hinn,
                     text="\n\n🎬  No downloads yet.\nDownload something — it'll show up here.",
                     font=FN, bg=C["bg"], fg=C["fg3"], justify="center"
                     ).pack(pady=50)
            return
        for item in reversed(mine[-80:]):
            self._hist_row(item)

    def _hist_row(self, item):
        row = tk.Frame(self._hinn, bg=C["card"],
                       highlightbackground=C["bdr"], highlightthickness=1)
        row.pack(fill="x", pady=(0,6))

        # Status dot
        dot_color = C["grn"] if item.get("status")=="done" else C["red"]
        dk = tk.Canvas(row, width=8, height=8,
                       bg=C["card"], highlightthickness=0)
        dk.pack(side="left", padx=(12,0))
        dk.create_oval(0,0,8,8, fill=dot_color, outline="")

        info = tk.Frame(row, bg=C["card"])
        info.pack(side="left", fill="x", expand=True, padx=10, pady=9)

        title = (item.get("title") or item.get("url","?"))[:64]
        tk.Label(info, text=title, font=FB,
                 bg=C["card"], fg=C["fg"], anchor="w").pack(fill="x")

        meta_parts = [item.get("mode",""), item.get("quality",""),
                      (item.get("format","")).upper(), item.get("date","")]
        meta = "  ·  ".join(p for p in meta_parts if p)
        tk.Label(info, text=meta, font=FS,
                 bg=C["card"], fg=C["fg3"], anchor="w").pack(fill="x")

        u = item.get("url","")
        btn(row, "↺",
            lambda url=u: (self.url_v.set(url), self._tab("download")),
            side="right", px=14, py=10)

    def _clr_hist(self):
        if messagebox.askyesno("Clear History",
                               "Delete your download history?"):
            self._hist = [h for h in self._hist if h.get("user")!=self._email]
            jsave(HIST_FILE, self._hist)
            self._refresh_hist()

    # ── SETTINGS PAGE ─────────────────────────────────────────────────────────
    def _pg_settings(self):
        pg = tk.Frame(self._cnt, bg=C["bg"])

        # Make it scrollable
        canvas = tk.Canvas(pg, bg=C["bg"], highlightthickness=0)
        sb2 = tk.Scrollbar(pg, orient="vertical", command=canvas.yview, width=6)
        inner = tk.Frame(canvas, bg=C["bg"])
        canvas.configure(yscrollcommand=sb2.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")
        win = canvas.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win, width=e.width))

        pady = (10,0)

        # ── Account ──
        ac = card(inner)
        tiny_label(ac, "Account").pack(anchor="w", pady=(0,8))

        arow = tk.Frame(ac, bg=C["card"]); arow.pack(fill="x")
        av2 = tk.Canvas(arow, width=36, height=36,
                        bg=C["red"], highlightthickness=0)
        av2.pack(side="left", padx=(0,10))
        av2.create_text(18,18, text=self._name[0].upper(),
                        fill=C["white"], font=FM)
        ai = tk.Frame(arow, bg=C["card"]); ai.pack(side="left")
        tk.Label(ai, text=self._name, font=FM,
                 bg=C["card"], fg=C["fg"]).pack(anchor="w")
        tk.Label(ai, text=self._email, font=FCo,
                 bg=C["card"], fg=C["fg3"]).pack(anchor="w")
        meth = "Google" if self._method=="google" else "Email & Password"
        tk.Label(ai, text=f"Signed in with {meth}", font=FS,
                 bg=C["card"], fg=C["fg3"]).pack(anchor="w")

        # ── Save folder ──
        sf = card(inner)
        tiny_label(sf, "Default Save Folder").pack(anchor="w", pady=(0,6))
        sfrow = tk.Frame(sf, bg=C["card"]); sfrow.pack(fill="x")
        self._set_pathlbl = tk.Label(sfrow, text=self.savepath,
                                      font=FCo, bg=C["s3"], fg=C["fg"],
                                      anchor="w", padx=10, pady=7)
        self._set_pathlbl.pack(side="left", fill="x", expand=True, padx=(0,8))
        redbtn(sfrow, "📁 Browse", self._browse, py=6).pack(side="left")

        # ── System info ──
        si = card(inner)
        tiny_label(si, "System Info").pack(anchor="w", pady=(0,6))

        rows_data = [
            ("FFmpeg",   "✓ Ready — sound merging works" if FFMPEG else "✓ Built-in (static-ffmpeg)",
             C["grn"]),
            ("yt-dlp",   f"v{yt_dlp.version.__version__}", C["fg2"]),
            ("App",      "YouTube Downloader v4", C["fg2"]),
        ]
        for key, val, vc in rows_data:
            r = tk.Frame(si, bg=C["card"])
            r.pack(fill="x", pady=2)
            tk.Label(r, text=key, font=FB, bg=C["card"],
                     fg=C["fg3"], width=10, anchor="w").pack(side="left")
            tk.Label(r, text=val, font=FCo, bg=C["card"],
                     fg=vc, anchor="w").pack(side="left")

        # ── Update ──
        uc = card(inner)
        tiny_label(uc, "Update").pack(anchor="w", pady=(0,8))
        self._upd_btn = btn(uc, "🔄  Update yt-dlp to Latest",
                             self._update_ytdlp, font=FN, px=14, py=7)
        self._upd_btn.pack(anchor="w")
        self._upd_lbl = tk.Label(uc, text="", font=FS,
                                  bg=C["card"], fg=C["fg3"])
        self._upd_lbl.pack(anchor="w", pady=(5,0))

        # ── Rate us ──
        rc = card(inner)
        rrow = tk.Frame(rc, bg=C["card"]); rrow.pack(fill="x")
        tk.Label(rrow, text="⭐", font=("Helvetica",20),
                 bg=C["card"]).pack(side="left", padx=(0,10))
        ri = tk.Frame(rrow, bg=C["card"]); ri.pack(side="left")
        tk.Label(ri, text="Enjoying the app?", font=FM,
                 bg=C["card"], fg=C["fg"]).pack(anchor="w")
        tk.Label(ri, text="Leave a quick rating — it really helps!",
                 font=FS, bg=C["card"], fg=C["fg3"]).pack(anchor="w")
        redbtn(rrow, "Rate Us ⭐", self._rate_dialog,
               py=7, px=14).pack(side="right")

        # ── Sign out ──
        oc = card(inner, pady=10)
        btn(oc, "←  Sign Out", self._signout,
            fg=C["fg3"], py=7, px=14).pack(anchor="w")

        return pg

    # ── RATE DIALOG ───────────────────────────────────────────────────────────
    def _rate_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Rate Us")
        dlg.geometry("320x260")
        dlg.resizable(False, False)
        dlg.configure(bg=C["card"])
        dlg.transient(self); dlg.grab_set()
        x = self.winfo_rootx() + (self.winfo_width()-320)//2
        y = self.winfo_rooty() + (self.winfo_height()-260)//2
        dlg.geometry(f"320x260+{x}+{y}")
        tk.Frame(dlg, bg=C["red"], height=2).pack(fill="x")
        inner = tk.Frame(dlg, bg=C["card"], padx=22, pady=18)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text="Rate YouTube Downloader",
                 font=FM, bg=C["card"], fg=C["fg"]).pack(anchor="w")
        tk.Label(inner, text="How was your experience?",
                 font=FN, bg=C["card"], fg=C["fg3"]).pack(anchor="w", pady=(3,10))

        self._stars = 0
        star_row = tk.Frame(inner, bg=C["card"])
        star_row.pack()
        star_lbls = []
        def set_stars(n):
            self._stars = n
            for i,s in enumerate(star_lbls):
                s.config(fg="#f59e0b" if i<n else C["fg3"])
        def hover(n):
            for i,s in enumerate(star_lbls):
                s.config(fg="#f59e0b" if i<n else C["fg3"])
        def unhover():
            set_stars(self._stars)
        for i in range(5):
            s = tk.Label(star_row, text="★", font=("Helvetica",22),
                         bg=C["card"], fg=C["fg3"], cursor="hand2")
            s.pack(side="left", padx=2)
            s.bind("<Button-1>", lambda e,n=i+1: set_stars(n))
            s.bind("<Enter>",    lambda e,n=i+1: hover(n))
            s.bind("<Leave>",    lambda e: unhover())
            star_lbls.append(s)

        fb = tk.Text(inner, height=3, bg=C["s3"], fg=C["fg"],
                     font=FN, relief="flat", padx=8, pady=6)
        fb.pack(fill="x", pady=(10,0))
        fb.insert("1.0", "Tell us what you think (optional)…")
        fb.config(fg=C["fg3"])
        fb.bind("<FocusIn>", lambda e: (fb.delete("1.0","end"), fb.config(fg=C["fg"])) if fb.get("1.0","end-1c")=="Tell us what you think (optional)…" else None)

        def submit():
            if not self._stars:
                messagebox.showinfo("Rating", "Pick a star rating first!",
                                    parent=dlg); return
            dlg.destroy()
            msg = f"Thanks for the {self._stars}★ rating!"
            if self._stars >= 4: msg += " 🎉"
            messagebox.showinfo("Thank You!", msg, parent=self)

        redbtn(inner, "Submit Rating", submit, py=8).pack(fill="x", pady=(10,0))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _browse(self):
        p = filedialog.askdirectory(initialdir=self.savepath)
        if p:
            self.savepath = p
            self._pathlbl.config(text=p)
            if hasattr(self,"_set_pathlbl"):
                self._set_pathlbl.config(text=p)
            # Save path into user prefs immediately
            self._save_prefs()

    def _paste(self):
        try:
            self.url_v.set(self.clipboard_get().strip())
        except: pass

    def _wlog(self, msg, tag=""):
        def _do():
            self._log.configure(state="normal")
            self._log.insert("end", msg+"\n", tag)
            self._log.see("end")
            self._log.configure(state="disabled")
        self.after(0, _do)

    def _setstat(self, msg, col=None):
        def _do():
            self.stat_v.set(msg)
            self._stat_lbl.config(fg=col or C["fg2"])
        self.after(0, _do)

    def _setspeed(self, spd, eta):
        def _do():
            t = f"{spd}  ·  ETA {eta}" if spd.strip() else ""
            self._speed_lbl.config(text=t)
        self.after(0, _do)

    def _setprog(self, pct):
        def _do():
            self.prog_v.set(pct)
            draw_bar(self._pbar, pct)
        self.after(0, _do)

    def _redraw(self):
        draw_bar(self._pbar, self.prog_v.get())

    def _signout(self):
        try: os.remove(SESS_FILE)
        except: pass
        self.destroy()
        LoginWin().mainloop()

    # ── Download opts ─────────────────────────────────────────────────────────
    def _build_opts(self):
        mode = self.mode_v.get()
        qual = self.qual_v.get()
        fmt  = self.fmt_v.get()
        out  = os.path.join(self.savepath, "%(title)s.%(ext)s")
        q_map = {
            "Best (Max Quality)": "bestvideo+bestaudio/best",
            "4K":                 "bestvideo[height<=2160]+bestaudio/best",
            "1080p":              "bestvideo[height<=1080]+bestaudio/best",
            "720p":               "bestvideo[height<=720]+bestaudio/best",
            "480p":               "bestvideo[height<=480]+bestaudio/best",
            "360p":               "bestvideo[height<=360]+bestaudio/best",
        }
        o = {
            "outtmpl":        out,
            "noplaylist":     "Playlist" not in mode,
            "progress_hooks": [self._hook],
            "quiet":          True,
            "no_warnings":    True,
            "ignoreerrors":   True,
        }
        if FFMPEG:
            o["ffmpeg_location"] = os.path.dirname(FFMPEG)
        if "Audio" in mode:
            ext = fmt if fmt in ("mp3","m4a") else "mp3"
            o["format"] = "bestaudio/best"
            o["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": ext,
                "preferredquality": "320",
            }]
        else:
            o["format"] = q_map.get(qual, "bestvideo+bestaudio/best")
            o["merge_output_format"] = fmt if fmt in ("mp4","mkv","webm") else "mp4"
        return o

    def _hook(self, d):
        if d["status"] == "downloading":
            raw = d.get("_percent_str","0%").strip()
            pct = float(re.sub(r"[^\d.]","",raw) or 0)
            spd = d.get("_speed_str","").strip()
            eta = d.get("_eta_str","").strip()
            self._setprog(pct)
            self._setstat(f"Downloading  {pct:.1f}%", C["ylw"])
            self._setspeed(spd, eta)
        elif d["status"] == "finished":
            self._setstat("Merging video + audio…", C["ylw"])

    def _start(self):
        url = self.url_v.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Paste a YouTube URL first!",
                                   parent=self); return
        if self._busy: return
        self._busy = True
        self._dl_btn.config(state="disabled")
        self._setprog(0)
        self._setstat("Starting…", C["ylw"])
        self._log.configure(state="normal")
        self._log.delete("1.0","end")
        self._log.configure(state="disabled")
        self._wlog(f"► {url}", "d")
        threading.Thread(target=self._dl, args=(url,), daemon=True).start()

    def _dl(self, url):
        title = url
        try:
            with yt_dlp.YoutubeDL({"quiet":True,"no_warnings":True}) as y:
                try:
                    info  = y.extract_info(url, download=False)
                    title = info.get("title", url)[:80]
                    self._wlog(f"  {title}", "d")
                except: pass
            with yt_dlp.YoutubeDL(self._build_opts()) as y:
                y.download([url])
            self._setprog(100)
            self._setstat("✔  Done!  Saved to: " + self.savepath, C["grn"])
            self._setspeed("","")
            self._wlog("✔  Complete — with sound!", "g")
            self._hist.append({
                "user":self._email,"url":url,"title":title,
                "mode":self.mode_v.get(),"quality":self.qual_v.get(),
                "format":self.fmt_v.get(),"status":"done",
                "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            jsave(HIST_FILE, self._hist)
        except Exception as e:
            self._setstat(f"Error: {e}", C["red"])
            self._wlog(f"✖  {e}", "r")
            self._hist.append({
                "user":self._email,"url":url,"title":title,"status":"error",
                "mode":self.mode_v.get(),"quality":self.qual_v.get(),
                "format":self.fmt_v.get(),
                "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            jsave(HIST_FILE, self._hist)
        finally:
            self._busy = False
            self.after(0, lambda: self._dl_btn.config(state="normal"))

    def _cancel(self):
        self._busy = False
        self._setstat("Cancelled.", C["fg2"])
        self._setprog(0)
        self._setspeed("","")
        self.after(0, lambda: self._dl_btn.config(state="normal"))

    def _update_ytdlp(self):
        self._upd_btn.config(state="disabled")
        self._upd_lbl.config(text="Updating…", fg=C["ylw"])
        def _do():
            try:
                subprocess.check_output(
                    [sys.executable,"-m","pip","install","--upgrade","yt-dlp"],
                    stderr=subprocess.STDOUT)
                self.after(0, lambda: self._upd_lbl.config(
                    text="✔  Updated successfully!", fg=C["grn"]))
            except Exception as e:
                self.after(0, lambda: self._upd_lbl.config(
                    text=f"Failed: {e}", fg=C["red"]))
            finally:
                self.after(0, lambda: self._upd_btn.config(state="normal"))
        threading.Thread(target=_do, daemon=True).start()


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        sess = jload(SESS_FILE, {})
        accs = jload(ACCS_FILE, {})
        if sess.get("email") and sess["email"] in accs:
            u = accs[sess["email"]]
            MainApp(sess["email"], u["name"],
                    u.get("method","email")).mainloop()
        else:
            LoginWin().mainloop()
    except Exception as e:
        import traceback
        try:
            r = tk.Tk(); r.withdraw()
            messagebox.showerror("Startup Error",
                f"App crashed on startup:\n\n{e}\n\n{traceback.format_exc()}")
            r.destroy()
        except:
            print(traceback.format_exc()); input("Press Enter…")
