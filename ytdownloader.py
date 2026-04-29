#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║   YouTube Downloader  —  by YTDLApp          ║
║   Free · Unlimited · With Sound · Accounts   ║
╚══════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading, subprocess, sys, os, re, json
import datetime, hashlib, webbrowser, time

# ── Auto-install ──────────────────────────────────────────────────────────────
def pip(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for _p, _i in [("yt-dlp","yt_dlp"),("static-ffmpeg","static_ffmpeg")]:
    try: __import__(_i)
    except: pip(_p)

import yt_dlp, static_ffmpeg
static_ffmpeg.add_paths()
import shutil
FFMPEG = shutil.which("ffmpeg") or ""

# ── App data paths ────────────────────────────────────────────────────────────
APP_DIR   = os.path.join(os.path.expanduser("~"), ".ytdl_app")
ACCS_FILE = os.path.join(APP_DIR, "accounts.json")
HIST_FILE = os.path.join(APP_DIR, "history.json")
SESS_FILE = os.path.join(APP_DIR, "session.json")
os.makedirs(APP_DIR, exist_ok=True)

def jload(p, d):
    try:
        with open(p) as f: return json.load(f)
    except: return d

def jsave(p, d):
    with open(p,"w") as f: json.dump(d, f, indent=2)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── Palette ───────────────────────────────────────────────────────────────────
B = {
    "bg":     "#0e0e0e",
    "card":   "#1a1a1a",
    "s3":     "#252525",
    "s4":     "#2f2f2f",
    "bdr":    "#333333",
    "red":    "#e63232",
    "redh":   "#ff5050",
    "redf":   "#3d0f0f",
    "grn":    "#22c55e",
    "ylw":    "#f59e0b",
    "blue":   "#4285F4",
    "blueh":  "#5a9bff",
    "fg":     "#f0f0f0",
    "fg2":    "#888888",
    "fg3":    "#444444",
    "white":  "#ffffff",
}
# Fonts
FXL  = ("Helvetica",22,"bold")
FLG  = ("Helvetica",14,"bold")
FMD  = ("Helvetica",11,"bold")
FN   = ("Helvetica",10)
FB   = ("Helvetica",10,"bold")
FS   = ("Helvetica",9)
FSB  = ("Helvetica",9,"bold")
FM   = ("Courier New",9)


# ═══════════════════════════════════════════════════════════════════════════════
#  LOGIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader — Sign In")
        self.geometry("460x620")
        self.resizable(False, False)
        self.configure(bg=B["bg"])
        self._accounts = jload(ACCS_FILE, {})
        self._mode     = "login"   # "login" or "register"
        self._logged_user = None
        self._build()
        # Centre on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 460) // 2
        y = (self.winfo_screenheight() - 620) // 2
        self.geometry(f"460x620+{x}+{y}")

    def _build(self):
        # ── Logo area ──
        top = tk.Frame(self, bg=B["bg"], pady=30)
        top.pack(fill="x")

        # YouTube-style logo drawn with canvas
        logo_frame = tk.Frame(top, bg=B["bg"])
        logo_frame.pack()
        cv = tk.Canvas(logo_frame, width=54, height=38,
                       bg=B["bg"], highlightthickness=0)
        cv.pack(side="left", padx=(0,10))
        # Red rounded rect
        cv.create_rectangle(2,2,52,36, fill=B["red"], outline="", width=0)
        cv.create_polygon(22,9, 22,29, 40,19, fill=B["white"])

        tk.Label(logo_frame, text="YouTube\nDownloader",
                 font=("Helvetica",15,"bold"), bg=B["bg"], fg=B["fg"],
                 justify="left").pack(side="left")

        tk.Label(top, text="Free · Unlimited · With Sound",
                 font=FS, bg=B["bg"], fg=B["fg3"]).pack(pady=(6,0))

        # ── Card ──
        card = tk.Frame(self, bg=B["card"], padx=36, pady=30)
        card.pack(fill="x", padx=30)

        self._title_lbl = tk.Label(card, text="Sign in to your account",
                                    font=FMD, bg=B["card"], fg=B["fg"])
        self._title_lbl.pack(anchor="w", pady=(0,20))

        # Name field (register only)
        self._name_frame = tk.Frame(card, bg=B["card"])
        tk.Label(self._name_frame, text="FULL NAME",
                 font=FSB, bg=B["card"], fg=B["fg3"]).pack(anchor="w", pady=(0,4))
        self._name_entry = self._entry(self._name_frame)
        self._name_entry.pack(fill="x", pady=(0,12))

        # Email
        tk.Label(card, text="EMAIL ADDRESS",
                 font=FSB, bg=B["card"], fg=B["fg3"]).pack(anchor="w", pady=(0,4))
        self._email = self._entry(card, placeholder="you@example.com")
        self._email.pack(fill="x", pady=(0,12))

        # Password
        tk.Label(card, text="PASSWORD",
                 font=FSB, bg=B["card"], fg=B["fg3"]).pack(anchor="w", pady=(0,4))
        self._pw = self._entry(card, show="●")
        self._pw.pack(fill="x", pady=(0,4))

        # Confirm password (register only)
        self._cpw_frame = tk.Frame(card, bg=B["card"])
        tk.Label(self._cpw_frame, text="CONFIRM PASSWORD",
                 font=FSB, bg=B["card"], fg=B["fg3"]).pack(anchor="w", pady=(0,4))
        self._cpw = self._entry(self._cpw_frame, show="●")
        self._cpw.pack(fill="x", pady=(0,4))

        # Error label
        self._err_lbl = tk.Label(card, text="", font=FS,
                                  bg=B["card"], fg=B["red"], wraplength=360,
                                  justify="left")
        self._err_lbl.pack(anchor="w", pady=(6,0))

        # Main action button
        self._main_btn = tk.Button(card, text="Sign In",
                                    font=("Helvetica",11,"bold"),
                                    bg=B["red"], fg=B["white"],
                                    activebackground=B["redh"],
                                    activeforeground=B["white"],
                                    relief="flat", cursor="hand2",
                                    padx=0, pady=12, bd=0,
                                    command=self._action)
        self._main_btn.pack(fill="x", pady=(14,0))
        self._main_btn.bind("<Enter>", lambda e: self._main_btn.config(bg=B["redh"]))
        self._main_btn.bind("<Leave>", lambda e: self._main_btn.config(bg=B["red"]))

        # Divider
        div = tk.Frame(card, bg=B["card"]); div.pack(fill="x", pady=(18,18))
        tk.Frame(div, bg=B["bdr"], height=1).pack(side="left", fill="x", expand=True)
        tk.Label(div, text="  OR  ", font=FS, bg=B["card"], fg=B["fg3"]).pack(side="left")
        tk.Frame(div, bg=B["bdr"], height=1).pack(side="left", fill="x", expand=True)

        # Google button
        g_btn = tk.Button(card, text="🔵  Continue with Google",
                          font=FB, bg=B["s3"], fg=B["fg"],
                          activebackground=B["s4"],
                          activeforeground=B["fg"],
                          relief="flat", cursor="hand2",
                          padx=0, pady=11, bd=0,
                          command=self._google_login)
        g_btn.pack(fill="x")
        g_btn.bind("<Enter>", lambda e: g_btn.config(bg=B["s4"]))
        g_btn.bind("<Leave>", lambda e: g_btn.config(bg=B["s3"]))

        # Toggle login / register
        toggle = tk.Frame(self, bg=B["bg"]); toggle.pack(pady=20)
        self._toggle_lbl = tk.Label(toggle, text="Don't have an account? ",
                                     font=FN, bg=B["bg"], fg=B["fg2"])
        self._toggle_lbl.pack(side="left")
        self._toggle_btn = tk.Label(toggle, text="Create one",
                                     font=FB, bg=B["bg"], fg=B["red"],
                                     cursor="hand2")
        self._toggle_btn.pack(side="left")
        self._toggle_btn.bind("<Button-1>", lambda e: self._switch_mode())

        self._name_frame.pack_forget()
        self._cpw_frame.pack_forget()

    def _entry(self, parent, placeholder="", show=""):
        e = tk.Entry(parent, font=("Helvetica",10), bg=B["s3"],
                     fg=B["fg"], insertbackground=B["red"],
                     relief="flat", bd=0, show=show)
        e.configure(highlightthickness=1, highlightbackground=B["bdr"],
                    highlightcolor=B["red"])
        if placeholder:
            e.insert(0, placeholder)
            e.config(fg=B["fg3"])
            e.bind("<FocusIn>",  lambda ev, en=e, ph=placeholder:
                   (en.delete(0,"end"), en.config(fg=B["fg"])) if en.get()==ph else None)
            e.bind("<FocusOut>", lambda ev, en=e, ph=placeholder:
                   (en.insert(0,ph), en.config(fg=B["fg3"])) if en.get()=="" else None)
        return e

    def _switch_mode(self):
        if self._mode == "login":
            self._mode = "register"
            self._title_lbl.config(text="Create a new account")
            self._main_btn.config(text="Create Account")
            self._toggle_lbl.config(text="Already have an account? ")
            self._toggle_btn.config(text="Sign in")
            self._name_frame.pack(before=self._email.master
                                  if hasattr(self._email,"master") else None)
            # Repack in right order
            for w in self._main_btn.master.winfo_children():
                w.pack_forget()
            self._title_lbl.pack(anchor="w", pady=(0,20))
            self._name_frame.pack(fill="x", pady=(0,12))
            tk.Label(self._main_btn.master, text="EMAIL ADDRESS",
                     font=FSB, bg=B["card"], fg=B["fg3"]).pack(anchor="w",pady=(0,4))
            self._email.pack(fill="x", pady=(0,12))
            tk.Label(self._main_btn.master, text="PASSWORD",
                     font=FSB, bg=B["card"], fg=B["fg3"]).pack(anchor="w",pady=(0,4))
            self._pw.pack(fill="x", pady=(0,4))
            self._cpw_frame.pack(fill="x", pady=(0,4))
            self._err_lbl.pack(anchor="w", pady=(6,0))
            self._main_btn.pack(fill="x", pady=(14,0))
        else:
            self._mode = "login"
            self._title_lbl.config(text="Sign in to your account")
            self._main_btn.config(text="Sign In")
            self._toggle_lbl.config(text="Don't have an account? ")
            self._toggle_btn.config(text="Create one")
            for w in self._main_btn.master.winfo_children():
                w.pack_forget()
            self._title_lbl.pack(anchor="w", pady=(0,20))
            self._email.pack(fill="x", pady=(0,12))
            self._pw.pack(fill="x", pady=(0,4))
            self._err_lbl.pack(anchor="w", pady=(6,0))
            self._main_btn.pack(fill="x", pady=(14,0))

    def _action(self):
        self._err_lbl.config(text="")
        email = self._email.get().strip().lower()
        pw    = self._pw.get()

        if not email or email == "you@example.com":
            self._err_lbl.config(text="Please enter your email address."); return
        if not pw:
            self._err_lbl.config(text="Please enter a password."); return
        if "@" not in email or "." not in email:
            self._err_lbl.config(text="Please enter a valid email address."); return

        if self._mode == "register":
            name = self._name_entry.get().strip()
            cpw  = self._cpw.get()
            if not name:
                self._err_lbl.config(text="Please enter your full name."); return
            if len(pw) < 6:
                self._err_lbl.config(text="Password must be at least 6 characters."); return
            if pw != cpw:
                self._err_lbl.config(text="Passwords do not match."); return
            if email in self._accounts:
                self._err_lbl.config(text="An account with this email already exists."); return
            self._accounts[email] = {
                "name":    name,
                "pw_hash": hash_pw(pw),
                "joined":  datetime.datetime.now().strftime("%Y-%m-%d"),
                "method":  "email",
            }
            jsave(ACCS_FILE, self._accounts)
            self._launch_app(email)
        else:
            if email not in self._accounts:
                self._err_lbl.config(text="No account found with this email."); return
            if self._accounts[email].get("pw_hash") != hash_pw(pw):
                self._err_lbl.config(text="Incorrect password. Please try again."); return
            self._launch_app(email)

    def _google_login(self):
        # Simulate Google login flow — opens Google sign-in page
        # For a real OAuth flow you'd need a Google Cloud client_id
        name  = "Google User"
        email = "google_user@gmail.com"

        # Show a dialog asking for the Google email
        dlg = tk.Toplevel(self)
        dlg.title("Continue with Google")
        dlg.geometry("380x260")
        dlg.configure(bg=B["card"])
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()
        x = self.winfo_rootx() + (460-380)//2
        y = self.winfo_rooty() + (620-260)//2
        dlg.geometry(f"380x260+{x}+{y}")

        tk.Label(dlg, text="🔵  Sign in with Google",
                 font=FMD, bg=B["card"], fg=B["fg"]).pack(pady=(24,4))
        tk.Label(dlg, text="Enter your Gmail address to continue",
                 font=FS, bg=B["card"], fg=B["fg2"]).pack(pady=(0,16))

        em_e = tk.Entry(dlg, font=FN, bg=B["s3"], fg=B["fg"],
                        insertbackground=B["blue"], relief="flat", bd=0)
        em_e.configure(highlightthickness=1,
                       highlightbackground=B["bdr"],
                       highlightcolor=B["blue"])
        em_e.insert(0, "@gmail.com")
        em_e.pack(fill="x", padx=30, ipady=9)
        em_e.bind("<FocusIn>", lambda e: (em_e.delete(0,"end"),em_e.config(fg=B["fg"])) if em_e.get()=="@gmail.com" else None)

        err_g = tk.Label(dlg, text="", font=FS, bg=B["card"], fg=B["red"])
        err_g.pack(pady=(6,0))

        def _confirm():
            ge = em_e.get().strip().lower()
            if not ge or ge == "@gmail.com" or "@" not in ge:
                err_g.config(text="Enter a valid Gmail address."); return
            # Register/login with Google method
            if ge not in self._accounts:
                gname = ge.split("@")[0].replace(".", " ").title()
                self._accounts[ge] = {
                    "name":   gname,
                    "pw_hash": "",
                    "joined":  datetime.datetime.now().strftime("%Y-%m-%d"),
                    "method":  "google",
                }
                jsave(ACCS_FILE, self._accounts)
            dlg.destroy()
            self._launch_app(ge)

        btn_g = tk.Button(dlg, text="Continue", font=FB,
                          bg=B["blue"], fg=B["white"],
                          activebackground=B["blueh"],
                          activeforeground=B["white"],
                          relief="flat", cursor="hand2",
                          padx=0, pady=10, bd=0,
                          command=_confirm)
        btn_g.pack(fill="x", padx=30, pady=16)
        btn_g.bind("<Enter>", lambda e: btn_g.config(bg=B["blueh"]))
        btn_g.bind("<Leave>", lambda e: btn_g.config(bg=B["blue"]))

    def _launch_app(self, email):
        user = self._accounts[email]
        jsave(SESS_FILE, {"email": email, "name": user["name"],
                          "method": user.get("method","email")})
        self.destroy()
        app = MainApp(email=email, name=user["name"],
                      method=user.get("method","email"))
        app.mainloop()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════
class MainApp(tk.Tk):
    def __init__(self, email, name, method):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("780x700")
        self.minsize(700, 620)
        self.configure(bg=B["bg"])
        self.resizable(True, True)

        self._email   = email
        self._name    = name
        self._method  = method
        self._history = jload(HIST_FILE, [])
        self.savepath = os.path.join(os.path.expanduser("~"), "Downloads")

        self.url_v    = tk.StringVar()
        self.mode_v   = tk.StringVar(value="Video")
        self.qual_v   = tk.StringVar(value="Best (Max Quality)")
        self.fmt_v    = tk.StringVar(value="mp4")
        self.status_v = tk.StringVar(value="Ready to download")
        self.prog_v   = tk.DoubleVar(value=0)
        self._busy    = False

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # ── Header ──
        hdr = tk.Frame(self, bg="#0a0a0a", height=60)
        hdr.pack(fill="x"); hdr.pack_propagate(False)

        # Logo
        cv = tk.Canvas(hdr, width=40,height=28,bg="#0a0a0a",highlightthickness=0)
        cv.pack(side="left", padx=(16,8), pady=16)
        cv.create_rectangle(1,1,39,27, fill=B["red"], outline="")
        cv.create_polygon(16,6, 16,22, 32,14, fill=B["white"])

        tk.Label(hdr, text="YouTube Downloader",
                 font=("Helvetica",14,"bold"), bg="#0a0a0a", fg=B["fg"]
                 ).pack(side="left", pady=16)

        # User chip (right side)
        chip = tk.Frame(hdr, bg=B["card"], pady=0)
        chip.pack(side="right", padx=16, pady=12)

        icon = "🔵" if self._method=="google" else "📧"
        initials = self._name[0].upper() if self._name else "?"
        av = tk.Canvas(chip, width=28,height=28,bg=B["red"],
                       highlightthickness=0)
        av.pack(side="left", padx=(8,4), pady=4)
        av.create_text(14,14, text=initials, fill=B["white"],
                       font=("Helvetica",11,"bold"))

        uinfo = tk.Frame(chip, bg=B["card"])
        uinfo.pack(side="left", padx=(0,4))
        tk.Label(uinfo, text=self._name, font=FSB,
                 bg=B["card"], fg=B["fg"]).pack(anchor="w")
        tk.Label(uinfo, text=self._email[:30], font=("Helvetica",8),
                 bg=B["card"], fg=B["fg3"]).pack(anchor="w")

        logout_btn = tk.Label(chip, text=" Sign out ",
                               font=FS, bg=B["card"], fg=B["fg3"],
                               cursor="hand2", padx=6)
        logout_btn.pack(side="left", padx=(4,6))
        logout_btn.bind("<Button-1>", lambda e: self._logout())

        # ── Tab bar ──
        tabrow = tk.Frame(self, bg="#111111", height=42)
        tabrow.pack(fill="x"); tabrow.pack_propagate(False)
        self._tabs = {}; self._pages = {}
        for n, icon in [("Download","⬇  Download"),
                         ("History", "🕘  History"),
                         ("Settings","⚙  Settings")]:
            b = tk.Label(tabrow, text=f"   {icon}   ", font=FB,
                         bg="#111111", fg=B["fg3"], cursor="hand2", pady=10)
            b.pack(side="left")
            b.bind("<Button-1>", lambda e, name=n: self._tab(name))
            self._tabs[n] = b

        # ── Pages ──
        self._cnt = tk.Frame(self, bg=B["bg"])
        self._cnt.pack(fill="both", expand=True)
        self._pages["Download"] = self._pg_download()
        self._pages["History"]  = self._pg_history()
        self._pages["Settings"] = self._pg_settings()
        self._tab("Download")

    def _tab(self, name):
        for p in self._pages.values(): p.place_forget()
        self._pages[name].place(relwidth=1, relheight=1)
        for n, b in self._tabs.items():
            b.config(fg=B["fg"] if n==name else B["fg3"],
                     bg=B["card"] if n==name else "#111111",
                     font=FB if n==name else FN)
        if name == "History": self._ref_hist()

    # ── Download page ─────────────────────────────────────────────────────────
    def _pg_download(self):
        pg = tk.Frame(self._cnt, bg=B["bg"])

        c1 = self._card(pg, "YouTube Link")
        row = tk.Frame(c1, bg=B["card"]); row.pack(fill="x", pady=(8,0))
        self._url_e = tk.Entry(row, textvariable=self.url_v,
                               font=("Courier New",11), bg=B["s3"], fg=B["fg"],
                               insertbackground=B["red"], relief="flat", bd=0)
        self._url_e.pack(side="left",fill="x",expand=True,ipady=10,padx=(10,8))
        self._btn(row,"Paste", lambda: self.url_v.set(self.clipboard_get()),side="left")
        self._btn(row,"✕",    lambda: self.url_v.set(""),side="left",pad=10)

        c2 = self._card(pg,"Options")
        og = tk.Frame(c2,bg=B["card"]); og.pack(fill="x",pady=(10,0))
        self._dd(og,"MODE",   self.mode_v,
                 ["Video","Audio Only","Playlist — Video","Playlist — Audio"],200)
        self._dd(og,"QUALITY",self.qual_v,
                 ["Best (Max Quality)","4K","1080p","720p","480p","360p"],180)
        self._dd(og,"FORMAT", self.fmt_v,
                 ["mp4","mkv","webm","mp3","m4a"],100)

        c3 = self._card(pg,"Save Folder")
        sr = tk.Frame(c3,bg=B["card"]); sr.pack(fill="x",pady=(8,0))
        self._plbl = tk.Label(sr,text=self.savepath,font=FM,bg=B["s3"],
                               fg=B["fg2"],anchor="w",padx=10,pady=9,cursor="hand2")
        self._plbl.pack(side="left",fill="x",expand=True,padx=(0,8))
        self._plbl.bind("<Button-1>", lambda e: self._browse())
        self._btn(sr,"📁  Change",self._browse,side="left")

        c4 = self._card(pg,""); c4.configure(pady=16)
        self.dl_btn = tk.Button(c4,text="⬇   DOWNLOAD NOW",
                                 font=("Helvetica",11,"bold"),
                                 bg=B["red"],fg=B["white"],
                                 activebackground=B["redh"],
                                 activeforeground=B["white"],
                                 relief="flat",cursor="hand2",
                                 padx=28,pady=12,bd=0,
                                 command=self._start)
        self.dl_btn.pack(side="left")
        self.dl_btn.bind("<Enter>",lambda e: self.dl_btn.config(bg=B["redh"]))
        self.dl_btn.bind("<Leave>",lambda e: self.dl_btn.config(bg=B["red"]))
        self._btn(c4,"Cancel",self._cancel,side="left",pad=14)

        pf = tk.Frame(pg,bg=B["bg"],padx=20); pf.pack(fill="x",pady=(6,0))
        self._pbar = tk.Canvas(pf,height=7,bg=B["s3"],highlightthickness=0)
        self._pbar.pack(fill="x")
        self._pbar.bind("<Configure>",lambda e: self._draw_bar())

        self._stlbl = tk.Label(pg,textvariable=self.status_v,
                                font=FS,bg=B["bg"],fg=B["fg2"],anchor="w",padx=22)
        self._stlbl.pack(fill="x",pady=(5,0))

        lf = tk.Frame(pg,bg=B["bg"],padx=20)
        lf.pack(fill="both",expand=True,pady=(8,14))
        self._logbox = tk.Text(lf,bg=B["card"],fg=B["fg2"],font=FM,
                                relief="flat",state="disabled",wrap="word",
                                padx=12,pady=8)
        self._logbox.pack(fill="both",expand=True)
        self._logbox.tag_config("g",foreground=B["grn"])
        self._logbox.tag_config("y",foreground=B["ylw"])
        self._logbox.tag_config("r",foreground=B["red"])
        self._logbox.tag_config("d",foreground=B["fg3"])
        return pg

    # ── History page ──────────────────────────────────────────────────────────
    def _pg_history(self):
        pg = tk.Frame(self._cnt,bg=B["bg"])
        hr = tk.Frame(pg,bg=B["bg"],padx=20,pady=14); hr.pack(fill="x")
        tk.Label(hr,text="Download History",font=("Helvetica",13,"bold"),
                 bg=B["bg"],fg=B["fg"]).pack(side="left")
        tk.Label(hr,text=f"  Logged in as {self._name}",
                 font=FS,bg=B["bg"],fg=B["fg3"]).pack(side="left",pady=4)
        self._btn(hr,"🗑  Clear All",self._clr_hist,side="right")

        wrap = tk.Frame(pg,bg=B["bg"],padx=20); wrap.pack(fill="both",expand=True)
        self._hcv = tk.Canvas(wrap,bg=B["bg"],highlightthickness=0)
        sb = tk.Scrollbar(wrap,orient="vertical",command=self._hcv.yview)
        self._hinn = tk.Frame(self._hcv,bg=B["bg"])
        self._hcv.configure(yscrollcommand=sb.set)
        self._hcv.pack(side="left",fill="both",expand=True)
        sb.pack(side="right",fill="y")
        self._hw = self._hcv.create_window((0,0),window=self._hinn,anchor="nw")
        self._hinn.bind("<Configure>",
            lambda e: self._hcv.configure(scrollregion=self._hcv.bbox("all")))
        self._hcv.bind("<Configure>",
            lambda e: self._hcv.itemconfig(self._hw,width=e.width))
        self._hcv.bind_all("<MouseWheel>",
            lambda e: self._hcv.yview_scroll(int(-1*(e.delta/120)),"units"))
        return pg

    def _ref_hist(self):
        my_hist = [h for h in self._history if h.get("user")==self._email]
        for w in self._hinn.winfo_children(): w.destroy()
        if not my_hist:
            tk.Label(self._hinn,
                     text="\n\n🎬  No downloads yet.\nDownload something and it will appear here.",
                     font=FN,bg=B["bg"],fg=B["fg3"],justify="center"
                     ).pack(pady=40)
            return
        for item in reversed(my_hist[-60:]):
            dot = B["grn"] if item.get("status")=="done" else B["red"]
            row = tk.Frame(self._hinn,bg=B["card"],
                           highlightbackground=B["bdr"],highlightthickness=1)
            row.pack(fill="x",pady=(0,6))
            tk.Label(row,text="●",font=("Helvetica",9),bg=B["card"],
                     fg=dot,padx=12).pack(side="left")
            inf = tk.Frame(row,bg=B["card"])
            inf.pack(side="left",fill="x",expand=True,pady=10)
            tk.Label(inf,text=item.get("title",item.get("url","?"))[:68],
                     font=FB,bg=B["card"],fg=B["fg"],anchor="w").pack(fill="x")
            tk.Label(inf,
                     text=f"{item.get('mode','')}  ·  {item.get('quality','')}  ·  {item.get('format','').upper()}  ·  {item.get('date','')}",
                     font=FS,bg=B["card"],fg=B["fg3"],anchor="w").pack(fill="x")
            u = item.get("url","")
            self._btn(row,"↺  Re-download",
                      lambda url=u:(self.url_v.set(url),self._tab("Download")),
                      side="right",pad=10)

    def _clr_hist(self):
        if messagebox.askyesno("Clear History","Delete your download history?"):
            self._history = [h for h in self._history if h.get("user")!=self._email]
            jsave(HIST_FILE,self._history)
            self._ref_hist()

    # ── Settings page ─────────────────────────────────────────────────────────
    def _pg_settings(self):
        pg = tk.Frame(self._cnt,bg=B["bg"])
        tk.Label(pg,text="Settings",font=("Helvetica",13,"bold"),
                 bg=B["bg"],fg=B["fg"],pady=16,padx=20,anchor="w").pack(fill="x")

        # Account info
        ac = self._card(pg,"Account")
        arow = tk.Frame(ac,bg=B["card"]); arow.pack(fill="x",pady=(8,0))
        av2 = tk.Canvas(arow,width=40,height=40,bg=B["red"],highlightthickness=0)
        av2.pack(side="left",padx=(0,12))
        av2.create_text(20,20,text=self._name[0].upper(),
                        fill=B["white"],font=("Helvetica",14,"bold"))
        ai = tk.Frame(arow,bg=B["card"]); ai.pack(side="left")
        tk.Label(ai,text=self._name, font=FB,bg=B["card"],fg=B["fg"]).pack(anchor="w")
        tk.Label(ai,text=self._email,font=FS,bg=B["card"],fg=B["fg3"]).pack(anchor="w")
        method_txt = "Google Account" if self._method=="google" else "Email & Password"
        tk.Label(ai,text=f"Signed in with: {method_txt}",
                 font=FS,bg=B["card"],fg=B["fg3"]).pack(anchor="w")

        # Save folder
        c1 = self._card(pg,"Default Save Folder")
        sr = tk.Frame(c1,bg=B["card"]); sr.pack(fill="x",pady=(8,0))
        self._spthlbl = tk.Label(sr,text=self.savepath,font=FM,bg=B["s3"],
                                  fg=B["fg"],anchor="w",padx=10,pady=9)
        self._spthlbl.pack(side="left",fill="x",expand=True,padx=(0,8))
        self._btn(sr,"📁  Browse",self._browse,side="left",red=True)

        # System info
        c2 = self._card(pg,"System Info")
        ff = "✅  FFmpeg ready" if FFMPEG else "✅  FFmpeg (built-in)"
        tk.Label(c2,text=ff,font=FS,bg=B["card"],fg=B["grn"],anchor="w",pady=4).pack(fill="x")
        tk.Label(c2,text=f"yt-dlp  v{yt_dlp.version.__version__}",
                 font=FS,bg=B["card"],fg=B["fg3"],anchor="w").pack(fill="x")

        # Update
        c3 = self._card(pg,"Update")
        self._btn(c3,"🔄  Update yt-dlp",self._update,side="left")
        self._uplog = tk.Text(c3,height=3,bg=B["s3"],fg=B["fg2"],font=FM,
                               relief="flat",state="disabled",padx=10,pady=6)
        self._uplog.pack(fill="x",pady=(10,0))

        # Sign out
        c4 = self._card(pg,"")
        self._btn(c4,"← Sign Out",self._logout,side="left",red=False)
        return pg

    # ── Shared helpers ────────────────────────────────────────────────────────
    def _card(self, parent, title):
        f = tk.Frame(parent,bg=B["card"],padx=18,pady=14)
        f.pack(fill="x",padx=20,pady=(10,0))
        if title:
            tk.Label(f,text=title.upper(),font=("Helvetica",8,"bold"),
                     bg=B["card"],fg=B["fg3"]).pack(anchor="w",pady=(0,2))
        return f

    def _btn(self, parent, text, cmd, side="left", pad=8, red=False):
        bg  = B["red"]  if red else B["s3"]
        hbg = B["redh"] if red else B["s4"]
        fg  = B["white"] if red else B["fg2"]
        b = tk.Button(parent,text=text,font=FN,bg=bg,fg=fg,
                      activebackground=hbg,activeforeground=fg,
                      relief="flat",cursor="hand2",padx=pad,pady=6,bd=0,
                      command=cmd)
        b.pack(side=side,padx=(8,0) if side=="left" else (0,8))
        b.bind("<Enter>",lambda e: b.config(bg=hbg))
        b.bind("<Leave>",lambda e: b.config(bg=bg))
        return b

    def _dd(self, parent, label, var, opts, width):
        col = tk.Frame(parent,bg=B["card"]); col.pack(side="left",padx=(0,16))
        tk.Label(col,text=label,font=("Helvetica",8,"bold"),
                 bg=B["card"],fg=B["fg3"]).pack(anchor="w",pady=(0,4))
        om = tk.OptionMenu(col,var,*opts)
        om.config(bg=B["s3"],fg=B["fg"],activebackground=B["s4"],
                  activeforeground=B["fg"],relief="flat",cursor="hand2",
                  font=FN,highlightthickness=0,bd=0,width=width//8,
                  indicatoron=True)
        om["menu"].config(bg=B["s3"],fg=B["fg"],activebackground=B["red"],
                          activeforeground=B["white"],font=FN,relief="flat",bd=0)
        om.pack(anchor="w")

    def _browse(self):
        p = filedialog.askdirectory(initialdir=self.savepath)
        if p:
            self.savepath = p
            self._plbl.config(text=p)
            if hasattr(self,"_spthlbl"): self._spthlbl.config(text=p)

    def _wlog(self, msg, tag=""):
        def _do():
            self._logbox.configure(state="normal")
            self._logbox.insert("end",msg+"\n",tag)
            self._logbox.see("end")
            self._logbox.configure(state="disabled")
        self.after(0,_do)

    def _setst(self, msg, col=None):
        def _do():
            self.status_v.set(msg)
            self._stlbl.config(fg=col or B["fg2"])
        self.after(0,_do)

    def _setprog(self, pct):
        def _do():
            self.prog_v.set(pct)
            self._draw_bar()
        self.after(0,_do)

    def _draw_bar(self):
        self._pbar.delete("b")
        w   = self._pbar.winfo_width()
        pct = self.prog_v.get()/100
        if pct > 0:
            self._pbar.create_rectangle(0,0,int(w*pct),7,
                                         fill=B["red"],outline="",tags="b")

    # ── Download ──────────────────────────────────────────────────────────────
    def _opts(self):
        mode = self.mode_v.get(); qual = self.qual_v.get(); fmt = self.fmt_v.get()
        out  = os.path.join(self.savepath,"%(title)s.%(ext)s")
        q_map = {
            "Best (Max Quality)":"bestvideo+bestaudio/best",
            "4K":                "bestvideo[height<=2160]+bestaudio/best",
            "1080p":             "bestvideo[height<=1080]+bestaudio/best",
            "720p":              "bestvideo[height<=720]+bestaudio/best",
            "480p":              "bestvideo[height<=480]+bestaudio/best",
            "360p":              "bestvideo[height<=360]+bestaudio/best",
        }
        o = {
            "outtmpl":        out,
            "noplaylist":     "Playlist" not in mode,
            "progress_hooks": [self._hook],
            "quiet":          True,
            "no_warnings":    True,
            "ignoreerrors":   True,
        }
        if FFMPEG: o["ffmpeg_location"] = os.path.dirname(FFMPEG)
        if "Audio" in mode:
            ext = fmt if fmt in ("mp3","m4a") else "mp3"
            o["format"] = "bestaudio/best"
            o["postprocessors"] = [{"key":"FFmpegExtractAudio",
                                    "preferredcodec":ext,
                                    "preferredquality":"320"}]
        else:
            o["format"] = q_map.get(qual,"bestvideo+bestaudio/best")
            o["merge_output_format"] = fmt if fmt in ("mp4","mkv","webm") else "mp4"
        return o

    def _hook(self, d):
        if d["status"] == "downloading":
            raw = d.get("_percent_str","0%").strip()
            pct = float(re.sub(r"[^\d.]","",raw) or 0)
            spd = d.get("_speed_str","—").strip()
            eta = d.get("_eta_str","—").strip()
            self._setprog(pct)
            self._setst(f"Downloading  {pct:.1f}%   {spd}   ETA {eta}",B["ylw"])
        elif d["status"] == "finished":
            self._setst("Merging video + audio…",B["ylw"])

    def _start(self):
        url = self.url_v.get().strip()
        if not url: messagebox.showwarning("No URL","Paste a YouTube URL first!"); return
        if self._busy: return
        self._busy = True
        self.dl_btn.config(state="disabled")
        self._setprog(0)
        self._setst("Starting…",B["ylw"])
        self._wlog(f"► {url}","d")
        threading.Thread(target=self._dl,args=(url,),daemon=True).start()

    def _dl(self, url):
        title = url
        try:
            with yt_dlp.YoutubeDL({"quiet":True,"no_warnings":True}) as y:
                try:
                    info  = y.extract_info(url,download=False)
                    title = info.get("title",url)[:80]
                    self._wlog(f"  {title}","d")
                except: pass
            with yt_dlp.YoutubeDL(self._opts()) as y:
                y.download([url])
            self._setprog(100)
            self._setst("✔  Done! Saved to: "+self.savepath,B["grn"])
            self._wlog("✔  Download complete — with sound!","g")
            self._history.append({
                "user":self._email,"url":url,"title":title,
                "mode":self.mode_v.get(),"quality":self.qual_v.get(),
                "format":self.fmt_v.get(),"status":"done",
                "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            jsave(HIST_FILE,self._history)
        except Exception as e:
            self._setst(f"Error: {e}",B["red"])
            self._wlog(f"✖  {e}","r")
            self._history.append({
                "user":self._email,"url":url,"title":title,"status":"error",
                "mode":self.mode_v.get(),"quality":self.qual_v.get(),
                "format":self.fmt_v.get(),
                "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            jsave(HIST_FILE,self._history)
        finally:
            self._busy = False
            self.after(0,lambda: self.dl_btn.config(state="normal"))

    def _cancel(self):
        self._busy = False
        self._setst("Cancelled.",B["fg2"])
        self._setprog(0)
        self.after(0,lambda: self.dl_btn.config(state="normal"))

    def _update(self):
        def _ul(msg):
            self._uplog.configure(state="normal")
            self._uplog.insert("end",msg+"\n")
            self._uplog.see("end")
            self._uplog.configure(state="disabled")
        def _do():
            _ul("Updating yt-dlp…")
            try:
                subprocess.check_output(
                    [sys.executable,"-m","pip","install","--upgrade","yt-dlp"],
                    stderr=subprocess.STDOUT)
                _ul("✅  Updated!")
            except Exception as e:
                _ul(f"Failed: {e}")
        threading.Thread(target=_do,daemon=True).start()

    def _logout(self):
        try: os.remove(SESS_FILE)
        except: pass
        self.destroy()
        LoginWindow().mainloop()


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        # Auto-resume session
        sess = jload(SESS_FILE, {})
        accs = jload(ACCS_FILE, {})
        if sess and sess.get("email") in accs:
            app = MainApp(email=sess["email"], name=sess["name"],
                         method=sess.get("method","email"))
            app.mainloop()
        else:
            LoginWindow().mainloop()
    except Exception as e:
        import traceback
        try:
            r = tk.Tk(); r.withdraw()
            messagebox.showerror("Error",
                f"App crashed:\n\n{e}\n\n{traceback.format_exc()}")
            r.destroy()
        except:
            print(traceback.format_exc()); input("Press Enter…")
