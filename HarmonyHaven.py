import os
import glob
import hashlib
import pygame
from mutagen.id3 import ID3
from tkinter import *
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
from PIL import Image, ImageTk
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import json
import csv
from datetime import datetime

pygame.mixer.init()

# ─── Resource Path ────────────────────────────────────────────────────────────
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# ─── Globals ──────────────────────────────────────────────────────────────────
music_files    = []
current_song   = None
current_index  = -1
root_directory = None
playlists      = {}

# ─── Color Palette — matched to HarmonyHaven.ico ─────────────────────────────
#  Logo colors:
#    Deep navy    #002050  (outline, dark fills)
#    Sky blue     #10c0f0  (bright inner glow)
#    Light cyan   #50d0f0  (wing highlights)
#    Cream/white  #f0f0e0  (background of logo)
#  We map these to a dark-navy UI theme with sky-blue accents.
COLORS = {
    "bg":          "#010d1a",   # near-black navy — window bg
    "surface":     "#001428",   # deep navy — panel bg
    "surface2":    "#002050",   # mid navy — logo's dark outline color
    "surface3":    "#002d6b",   # lifted navy — hover
    "accent":      "#0ab8e8",   # sky blue — logo's inner glow
    "accent2":     "#50d0f0",   # light cyan — logo wing highlights
    "accent_dim":  "#076e8c",   # muted sky — inactive accent
    "text":        "#eef5ff",   # near-white cream
    "text_dim":    "#5a8fac",   # muted blue-grey
    "text_muted":  "#1e4a68",   # dark muted — placeholders / disabled
    "success":     "#3dd68c",
    "warning":     "#e0a030",
    "danger":      "#e05050",
    "border":      "#003060",   # navy border — logo outline shade
    "highlight":   "#003878",   # selection bg
    "entry_bg":    "#000e1e",   # darkest input bg
    "header_bg":   "#000a14",   # header strip
}

FONT_TITLE  = ("Segoe UI", 14, "bold")
FONT_HEADER = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 8)
FONT_MONO   = ("Consolas", 9)

# ─── Main Window ──────────────────────────────────────────────────────────────
root = Tk()
root.title("HarmonyHaven  ·  TechFusion Repairs LLC")
root.geometry("1000x800")
root.configure(bg=COLORS["bg"])
root.resizable(True, True)
root.minsize(820, 660)

icon_path = resource_path('HarmonyHaven.ico')
try:
    root.iconbitmap(icon_path)
except Exception:
    pass

# ─── ttk Style ────────────────────────────────────────────────────────────────
style = ttk.Style()
style.theme_use("clam")

style.configure(".",
    background=COLORS["bg"], foreground=COLORS["text"],
    font=FONT_BODY, borderwidth=0, relief="flat")
style.configure("TNotebook",
    background=COLORS["header_bg"], tabmargins=[0, 4, 0, 0])
style.configure("TNotebook.Tab",
    background=COLORS["entry_bg"], foreground=COLORS["text_dim"],
    padding=[20, 9], font=FONT_BODY)
style.map("TNotebook.Tab",
    background=[("selected", COLORS["surface2"]), ("active", COLORS["surface2"])],
    foreground=[("selected", COLORS["accent2"]),  ("active", COLORS["text"])])
style.configure("TFrame",  background=COLORS["bg"])
style.configure("TLabel",  background=COLORS["bg"], foreground=COLORS["text"])
style.configure("TEntry",
    fieldbackground=COLORS["entry_bg"], foreground=COLORS["text"],
    insertcolor=COLORS["accent2"], bordercolor=COLORS["border"],
    lightcolor=COLORS["border"],   darkcolor=COLORS["border"],
    selectbackground=COLORS["highlight"])
style.configure("TScrollbar",
    background=COLORS["surface2"], troughcolor=COLORS["surface"],
    arrowcolor=COLORS["text_dim"],  bordercolor=COLORS["border"], width=8)
style.map("TScrollbar",
    background=[("active", COLORS["accent_dim"]), ("!active", COLORS["surface2"])])
style.configure("Accent.TButton",
    background=COLORS["accent"], foreground=COLORS["bg"],
    padding=[12, 7], font=FONT_HEADER, relief="flat")
style.map("Accent.TButton",
    background=[("active", COLORS["accent2"]), ("pressed", COLORS["accent_dim"])])
style.configure("Ghost.TButton",
    background=COLORS["surface2"], foreground=COLORS["text_dim"],
    padding=[10, 6], font=FONT_BODY, relief="flat")
style.map("Ghost.TButton",
    background=[("active", COLORS["surface3"])],
    foreground=[("active", COLORS["text"])])
style.configure("Danger.TButton",
    background=COLORS["danger"], foreground="white",
    padding=[10, 6], font=FONT_BODY, relief="flat")
style.map("Danger.TButton",
    background=[("active", "#b83030")])
style.configure("TCheckbutton",
    background=COLORS["bg"], foreground=COLORS["text"],
    focuscolor=COLORS["accent"])
style.map("TCheckbutton",
    background=[("active", COLORS["bg"])],
    foreground=[("active", COLORS["accent2"])])
style.configure("TScale",
    background=COLORS["surface"], troughcolor=COLORS["surface2"],
    sliderrelief="flat")

# ─── Canvas Transport Button ──────────────────────────────────────────────────
def icon_btn(parent, text, cmd, size=40, accent=False):
    bg_n  = COLORS["accent"]  if accent else COLORS["surface2"]
    fg_n  = COLORS["bg"]      if accent else COLORS["text_dim"]
    bg_h  = COLORS["accent2"] if accent else COLORS["surface3"]
    fg_h  = COLORS["bg"]      if accent else COLORS["text"]
    c = Canvas(parent, width=size, height=size,
               bg=parent["bg"], highlightthickness=0, cursor="hand2")
    def draw(bg, fg):
        c.delete("all")
        c.create_oval(1, 1, size-1, size-1,
                      fill=bg, outline=COLORS["border"], width=1)
        c.create_text(size//2, size//2, text=text, fill=fg,
                      font=("Segoe UI", 11 if size >= 44 else 9, "bold"))
    draw(bg_n, fg_n)
    c.bind("<Enter>",    lambda e: draw(bg_h, fg_h))
    c.bind("<Leave>",    lambda e: draw(bg_n, fg_n))
    c.bind("<Button-1>", lambda e: cmd())
    return c

# ──────────────────────────────────────────────────────────────────────────────
#  HEADER
# ──────────────────────────────────────────────────────────────────────────────
header = Frame(root, bg=COLORS["header_bg"], height=68)
header.pack(fill=X, side=TOP)
header.pack_propagate(False)

# Logo image
_logo_ref = None
try:
    _ico = Image.open(resource_path("HarmonyHaven.ico")).convert("RGBA")
    _ico = _ico.resize((48, 48), Image.LANCZOS)
    _logo_ref = ImageTk.PhotoImage(_ico)
    Label(header, image=_logo_ref, bg=COLORS["header_bg"], padx=10).pack(side=LEFT, pady=10)
except Exception:
    pass

Frame(header, bg=COLORS["border"], width=1).pack(side=LEFT, fill=Y, pady=8)

name_block = Frame(header, bg=COLORS["header_bg"])
name_block.pack(side=LEFT, padx=14, pady=10)
Label(name_block, text="HarmonyHaven",
      bg=COLORS["header_bg"], fg=COLORS["accent2"],
      font=("Segoe UI", 15, "bold")).pack(anchor=W)
Label(name_block, text="by TechFusion Repairs LLC",
      bg=COLORS["header_bg"], fg=COLORS["text_muted"],
      font=FONT_SMALL).pack(anchor=W)

now_playing_var = StringVar(value="No track selected")
np_frame = Frame(header, bg=COLORS["header_bg"])
np_frame.pack(side=RIGHT, padx=20, pady=10)
Label(np_frame, text="NOW PLAYING",
      bg=COLORS["header_bg"], fg=COLORS["text_muted"],
      font=("Segoe UI", 7, "bold")).pack(anchor=E)
Label(np_frame, textvariable=now_playing_var,
      bg=COLORS["header_bg"], fg=COLORS["accent"],
      font=("Segoe UI", 10, "bold")).pack(anchor=E)

# Sky-blue accent line beneath header (matches logo glow)
Frame(root, bg=COLORS["accent"], height=2).pack(fill=X)

# ─── Status Bar ───────────────────────────────────────────────────────────────
status_frame = Frame(root, bg=COLORS["surface"], height=26)
status_frame.pack(side=BOTTOM, fill=X)
status_frame.pack_propagate(False)
status_var = StringVar(value="Ready")
Label(status_frame, textvariable=status_var,
      bg=COLORS["surface"], fg=COLORS["text_dim"],
      font=FONT_SMALL, anchor=W, padx=10).pack(side=LEFT, fill=Y)
Label(status_frame, text="© 2024 TechFusion Repairs LLC  ·  MIT License",
      bg=COLORS["surface"], fg=COLORS["text_muted"],
      font=FONT_SMALL, anchor=E, padx=10).pack(side=RIGHT, fill=Y)

# ─── Logging helpers ──────────────────────────────────────────────────────────
def log_message(log_widget, message):
    ts = datetime.now().strftime("%H:%M:%S")
    log_widget.config(state=NORMAL)
    log_widget.insert(END, f"[{ts}]  {message}\n")
    log_widget.see(END)
    log_widget.config(state=DISABLED)
    status_var.set(message[:90])

def clear_log(log_widget):
    log_widget.config(state=NORMAL)
    log_widget.delete(1.0, END)
    log_widget.config(state=DISABLED)

def make_log_widget(parent):
    frame = Frame(parent, bg=COLORS["entry_bg"], bd=0)
    txt = Text(frame, height=10, wrap=WORD, state=DISABLED,
               bg=COLORS["entry_bg"], fg=COLORS["text_dim"],
               font=FONT_MONO, relief="flat", bd=0,
               insertbackground=COLORS["accent"],
               selectbackground=COLORS["highlight"],
               padx=8, pady=6)
    sb = ttk.Scrollbar(frame, command=txt.yview)
    txt.config(yscrollcommand=sb.set)
    sb.pack(side=RIGHT, fill=Y)
    txt.pack(side=LEFT, fill=BOTH, expand=True)
    return frame, txt

# ─── UI Helpers ───────────────────────────────────────────────────────────────
def section_label(parent, text):
    Label(parent, text=text.upper(),
          bg=COLORS["bg"], fg=COLORS["accent"],
          font=("Segoe UI", 7, "bold"), padx=2).pack(
        anchor=W, padx=16, pady=(14, 2))
    Frame(parent, bg=COLORS["border"], height=1).pack(fill=X, padx=12, pady=(0, 4))

def styled_entry(parent, placeholder=""):
    e = ttk.Entry(parent, font=FONT_BODY)
    e.pack(fill=X, padx=14, pady=(0, 6))
    if placeholder:
        e.insert(0, placeholder)
        e.config(foreground=COLORS["text_muted"])
        def _in(ev):
            if e.get() == placeholder:
                e.delete(0, END)
                e.config(foreground=COLORS["text"])
        def _out(ev):
            if not e.get():
                e.insert(0, placeholder)
                e.config(foreground=COLORS["text_muted"])
        e.bind("<FocusIn>",  _in)
        e.bind("<FocusOut>", _out)
    return e

# ──────────────────────────────────────────────────────────────────────────────
#  BUSINESS LOGIC
# ──────────────────────────────────────────────────────────────────────────────
def select_directory(log_widget):
    global root_directory
    root_directory = filedialog.askdirectory(title="Select Music Directory")
    if root_directory:
        log_message(log_widget, f"Scanning: {root_directory}")
        scan_music_files(root_directory, log_widget)
    else:
        log_message(log_widget, "No directory selected.")

def scan_music_files(directory, log_widget):
    global music_files
    music_files = []
    if not directory or not os.path.exists(directory):
        log_message(log_widget, "Invalid directory.")
        return
    for ext in ['.mp3', '.flac', '.wav', '.m4a', '.ogg', '.aac']:
        music_files.extend(
            glob.glob(os.path.join(directory, '**', f'*{ext}'), recursive=True))
    if music_files:
        log_message(log_widget, f"Found {len(music_files)} music file(s).")
        update_song_list()
    else:
        log_message(log_widget, "No music files found.")

def update_song_list():
    song_listbox.delete(0, END)
    for i, file in enumerate(music_files):
        song_listbox.insert(END, f"  {os.path.basename(file)}")
        row_bg = COLORS["surface"] if i % 2 == 0 else COLORS["surface2"]
        song_listbox.itemconfig(i, bg=row_bg, fg=COLORS["text"])
    track_count_var.set(f"{len(music_files)} tracks")

def calculate_hash(file_path, chunk_size=8192):
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def find_duplicates(log_widget):
    if not music_files:
        log_message(log_widget, "No music files loaded. Scan a directory first.")
        return
    log_message(log_widget, f"Checking {len(music_files)} files…")
    hashes, duplicates = {}, []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(calculate_hash, f): f for f in music_files}
        for future in as_completed(futures):
            fp = futures[future]
            try:
                fh = future.result()
                if fh in hashes:
                    duplicates.append((fp, hashes[fh]))
                else:
                    hashes[fh] = fp
            except Exception as e:
                log_message(log_widget, f"Hash error: {e}")
    if duplicates:
        log_message(log_widget, f"Found {len(duplicates)} duplicate(s).")
        if messagebox.askyesno("Remove Duplicates",
                               f"Found {len(duplicates)} duplicate file(s).\n"
                               "Permanently delete them?"):
            for dup, _ in duplicates:
                try:
                    os.remove(dup)
                    log_message(log_widget, f"Deleted: {os.path.basename(dup)}")
                except Exception as e:
                    log_message(log_widget, f"Error: {e}")
            scan_music_files(root_directory, log_widget)
    else:
        log_message(log_widget, "No duplicates found. ✓")

def delete_empty_folders(log_widget):
    if not root_directory:
        log_message(log_widget, "Scan a directory first.")
        return
    removed = []
    for folder, subs, files in os.walk(root_directory, topdown=False):
        if not subs and not files:
            try:
                os.rmdir(folder)
                removed.append(folder)
            except Exception as e:
                log_message(log_widget, f"Could not remove: {e}")
    log_message(log_widget,
                f"Deleted {len(removed)} empty folder(s)." if removed
                else "No empty folders found. ✓")

def export_to_csv(log_widget):
    if not music_files:
        log_message(log_widget, "No files to export.")
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save Song List")
    if path:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["#", "File Name", "File Path"])
            for i, file in enumerate(music_files, 1):
                writer.writerow([i, os.path.basename(file), file])
        log_message(log_widget,
                    f"Exported {len(music_files)} tracks → {os.path.basename(path)}")

def play_music(file_path):
    global current_song
    if not os.path.exists(file_path):
        messagebox.showwarning("File Not Found", f"Cannot locate:\n{file_path}")
        return
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        current_song = file_path
        name = os.path.basename(file_path)
        now_playing_var.set(name)
        status_var.set(f"Playing: {name}")
    except Exception as e:
        messagebox.showerror("Playback Error", str(e))

def play_selected_song(event=None):
    sel = song_listbox.curselection()
    if sel:
        global current_index
        current_index = sel[0]
        play_music(music_files[current_index])

def pause_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        status_var.set("Paused")
    else:
        pygame.mixer.music.unpause()
        status_var.set(f"Resumed: {os.path.basename(current_song) if current_song else ''}")

def stop_music():
    pygame.mixer.music.stop()
    now_playing_var.set("No track selected")
    status_var.set("Stopped")

def next_song():
    global current_index
    if not music_files: return
    current_index = (current_index + 1) % len(music_files)
    song_listbox.selection_clear(0, END)
    song_listbox.selection_set(current_index)
    song_listbox.see(current_index)
    play_music(music_files[current_index])

def prev_song():
    global current_index
    if not music_files: return
    current_index = (current_index - 1) % len(music_files)
    song_listbox.selection_clear(0, END)
    song_listbox.selection_set(current_index)
    song_listbox.see(current_index)
    play_music(music_files[current_index])

def set_volume(val):
    pygame.mixer.music.set_volume(float(val) / 100.0)

def search_for_song(log_widget, query_entry):
    if not root_directory:
        log_message(log_widget, "Scan a directory first.")
        return
    q = query_entry.get().strip()
    if not q:
        log_message(log_widget, "Enter a search term.")
        return
    found = []
    for ext in ['.mp3', '.flac', '.wav', '.m4a', '.ogg', '.aac']:
        found.extend(glob.glob(
            os.path.join(root_directory, '**', f'*{q}*{ext}'), recursive=True))
    if found:
        log_message(log_widget, f"Found {len(found)} result(s) for '{q}':")
        for f in found:
            log_message(log_widget, f"  → {os.path.basename(f)}")
    else:
        log_message(log_widget, f"No matches for '{q}'.")

def advanced_search(log_widget, artist_entry, genre_entry):
    if not music_files:
        log_message(log_widget, "No files loaded. Scan a directory first.")
        return
    artist = artist_entry.get().strip()
    genre  = genre_entry.get().strip()
    results = []
    for file in music_files:
        try:
            audio = ID3(file)
            a = audio.getall('TPE1')[0].text[0] if audio.getall('TPE1') else ""
            g = audio.getall('TCON')[0].text[0] if audio.getall('TCON') else ""
            if ((not artist or artist.lower() in a.lower()) and
                    (not genre  or genre.lower()  in g.lower())):
                results.append(file)
        except Exception:
            pass
    if results:
        log_message(log_widget, f"Advanced search: {len(results)} result(s).")
        for r in results:
            log_message(log_widget, f"  → {os.path.basename(r)}")
    else:
        log_message(log_widget, "No matches found.")

def create_playlist(log_widget, name_entry, pl_listbox):
    name = name_entry.get().strip()
    if not name:
        messagebox.showwarning("Playlist", "Enter a playlist name.")
        return
    if not music_files:
        messagebox.showwarning("Playlist", "No tracks loaded.")
        return
    playlists[name] = music_files.copy()
    log_message(log_widget, f"Playlist '{name}' created — {len(music_files)} tracks.")
    name_entry.delete(0, END)
    refresh_playlist_list(pl_listbox)

def load_playlist(log_widget, pl_listbox):
    sel = pl_listbox.curselection()
    if not sel: return
    name = pl_listbox.get(sel[0]).strip()
    if name in playlists:
        global music_files
        music_files = playlists[name]
        update_song_list()
        log_message(log_widget, f"Loaded '{name}' — {len(music_files)} tracks.")

def delete_playlist(log_widget, pl_listbox):
    sel = pl_listbox.curselection()
    if not sel: return
    name = pl_listbox.get(sel[0]).strip()
    if name in playlists and messagebox.askyesno("Delete", f"Delete playlist '{name}'?"):
        del playlists[name]
        refresh_playlist_list(pl_listbox)
        log_message(log_widget, f"Deleted playlist '{name}'.")

def save_playlists(log_widget):
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        initialfile="playlists.json",
        title="Save Playlists")
    if path:
        with open(path, "w") as f:
            json.dump(playlists, f, indent=2)
        log_message(log_widget,
                    f"Saved {len(playlists)} playlist(s) → {os.path.basename(path)}")

def load_playlists_from_file(log_widget, pl_listbox):
    global playlists
    path = filedialog.askopenfilename(
        filetypes=[("JSON Files", "*.json")],
        title="Load Playlists")
    if path:
        try:
            with open(path, "r") as f:
                playlists = json.load(f)
            refresh_playlist_list(pl_listbox)
            log_message(log_widget, f"Loaded {len(playlists)} playlist(s).")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

def refresh_playlist_list(pl_listbox):
    pl_listbox.delete(0, END)
    for i, name in enumerate(playlists):
        pl_listbox.insert(END, f"  {name}")
        row_bg = COLORS["surface"] if i % 2 == 0 else COLORS["surface2"]
        pl_listbox.itemconfig(i, bg=row_bg, fg=COLORS["text"])

def auto_load_playlists():
    global playlists
    if os.path.exists("playlists.json"):
        try:
            with open("playlists.json", "r") as f:
                playlists = json.load(f)
        except Exception:
            pass

def get_id3_tags():
    for f in music_files:
        try:
            audio = ID3(f)
            tags = {}
            for tag in audio.keys():
                frames = audio.getall(tag)
                if frames and hasattr(frames[0], 'text') and frames[0].text:
                    tags[tag] = frames[0].text[0]
            if tags:
                return tags
        except Exception:
            pass
    return {}

def organize_music_by_id3(log_widget):
    id3_tags = get_id3_tags()
    text_tags = {k: v for k, v in id3_tags.items() if v and v != "Unknown"}
    if not text_tags:
        log_message(log_widget, "No ID3 tags found in scanned files.")
        return
    win = Toplevel(root)
    win.title("Organize by ID3 Tags")
    win.geometry("400x300")
    win.configure(bg=COLORS["bg"])
    win.grab_set()
    Frame(win, bg=COLORS["accent"], height=3).pack(fill=X)
    Label(win, text="Organize Music by ID3 Tags",
          bg=COLORS["bg"], fg=COLORS["accent2"], font=FONT_HEADER).pack(pady=(14, 4))
    Frame(win, bg=COLORS["border"], height=1).pack(fill=X, padx=20, pady=4)
    Label(win, text="Primary folder tag:",
          bg=COLORS["bg"], fg=COLORS["text_dim"], font=FONT_SMALL).pack(anchor=W, padx=20, pady=(8, 2))
    primary_var = StringVar(value=next(iter(text_tags)))
    ttk.OptionMenu(win, primary_var, primary_var.get(), *text_tags.keys()).pack(fill=X, padx=20, pady=2)
    Label(win, text="Subfolder tag:",
          bg=COLORS["bg"], fg=COLORS["text_dim"], font=FONT_SMALL).pack(anchor=W, padx=20, pady=(8, 2))
    sub_var = StringVar(value=next(iter(text_tags)))
    ttk.OptionMenu(win, sub_var, sub_var.get(), *text_tags.keys()).pack(fill=X, padx=20, pady=2)
    Frame(win, bg=COLORS["border"], height=1).pack(fill=X, padx=20, pady=10)
    ttk.Button(win, text="Sort & Move Files", style="Accent.TButton",
               command=lambda: sort_music(primary_var.get(), sub_var.get(), log_widget, win)).pack(pady=4)

def sort_music(primary, sub, log_widget, win):
    folder = filedialog.askdirectory(title="Select Destination Folder")
    if not folder: return
    moved = errors = 0
    for file in music_files:
        try:
            audio = ID3(file)
            p = audio.getall(primary)[0].text[0] if audio.getall(primary) else "Unknown"
            s = audio.getall(sub)[0].text[0]     if audio.getall(sub)     else "Unknown"
            new_dir = os.path.join(folder, p, s)
            os.makedirs(new_dir, exist_ok=True)
            os.rename(file, os.path.join(new_dir, os.path.basename(file)))
            moved += 1
        except Exception as e:
            log_message(log_widget, f"Error: {e}")
            errors += 1
    log_message(log_widget, f"Done — moved {moved} file(s), {errors} error(s).")
    win.destroy()

# ─── Keyboard Shortcuts ───────────────────────────────────────────────────────
root.bind('<Control-o>', lambda e: select_directory(file_log))
root.bind('<Control-p>', lambda e: play_selected_song())
root.bind('<space>',     lambda e: pause_music())
root.bind('<Right>',     lambda e: next_song())
root.bind('<Left>',      lambda e: prev_song())

# ══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK
# ══════════════════════════════════════════════════════════════════════════════
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# ── TAB 1: File Ops ───────────────────────────────────────────────────────────
tab_file = ttk.Frame(notebook)
notebook.add(tab_file, text="  File Ops  ")
left_file = Frame(tab_file, bg=COLORS["bg"], width=230)
left_file.pack(side=LEFT, fill=Y); left_file.pack_propagate(False)
Frame(tab_file, bg=COLORS["border"], width=1).pack(side=LEFT, fill=Y)
right_file = Frame(tab_file, bg=COLORS["surface"])
right_file.pack(side=LEFT, fill=BOTH, expand=True)

section_label(left_file, "Directory")
ttk.Button(left_file, text="⊕  Scan Directory  (Ctrl+O)",
           style="Accent.TButton",
           command=lambda: select_directory(file_log)).pack(fill=X, padx=12, pady=3)
section_label(left_file, "Tools")
for lbl, cmd in [
    ("⧉  Find & Remove Duplicates", lambda: find_duplicates(file_log)),
    ("⌫  Delete Empty Folders",     lambda: delete_empty_folders(file_log)),
    ("↗  Export Library to CSV",    lambda: export_to_csv(file_log)),
]:
    ttk.Button(left_file, text=lbl, style="Ghost.TButton", command=cmd).pack(
        fill=X, padx=12, pady=2)
section_label(left_file, "Log")
ttk.Button(left_file, text="✕  Clear Log", style="Ghost.TButton",
           command=lambda: clear_log(file_log)).pack(fill=X, padx=12, pady=2)

Label(right_file, text="Activity Log", bg=COLORS["surface"], fg=COLORS["text_dim"],
      font=FONT_SMALL, padx=12, pady=6).pack(anchor=W)
Frame(right_file, bg=COLORS["border"], height=1).pack(fill=X)
log_frame, file_log = make_log_widget(right_file)
log_frame.pack(fill=BOTH, expand=True, padx=6, pady=6)

# ── TAB 2: Playback ───────────────────────────────────────────────────────────
tab_play = ttk.Frame(notebook)
notebook.add(tab_play, text="  Playback  ")

list_hdr = Frame(tab_play, bg=COLORS["surface2"], height=34)
list_hdr.pack(fill=X); list_hdr.pack_propagate(False)
Label(list_hdr, text="LIBRARY", bg=COLORS["surface2"], fg=COLORS["accent"],
      font=("Segoe UI", 7, "bold"), padx=14).pack(side=LEFT, pady=8)
track_count_var = StringVar(value="0 tracks")
Label(list_hdr, textvariable=track_count_var, bg=COLORS["surface2"],
      fg=COLORS["text_muted"], font=FONT_SMALL, padx=10).pack(side=RIGHT, pady=8)

lb_frame = Frame(tab_play, bg=COLORS["surface"])
lb_frame.pack(fill=BOTH, expand=True, padx=4, pady=4)
song_listbox = Listbox(lb_frame, font=("Segoe UI", 10),
    bg=COLORS["surface"], fg=COLORS["text"],
    selectbackground=COLORS["highlight"], selectforeground=COLORS["accent2"],
    relief="flat", bd=0, activestyle="none", cursor="hand2")
lb_sb = ttk.Scrollbar(lb_frame, command=song_listbox.yview)
song_listbox.config(yscrollcommand=lb_sb.set)
lb_sb.pack(side=RIGHT, fill=Y)
song_listbox.pack(side=LEFT, fill=BOTH, expand=True)
song_listbox.bind("<Double-Button-1>", play_selected_song)

Frame(tab_play, bg=COLORS["accent"], height=2).pack(fill=X)

ctrl = Frame(tab_play, bg=COLORS["header_bg"], height=120)
ctrl.pack(fill=X, side=BOTTOM); ctrl.pack_propagate(False)

transport = Frame(ctrl, bg=COLORS["header_bg"])
transport.pack(pady=(14, 4))
icon_btn(transport, "⏮", prev_song,         size=38).pack(side=LEFT, padx=5)
icon_btn(transport, "▶", play_selected_song, size=50, accent=True).pack(side=LEFT, padx=5)
icon_btn(transport, "⏸", pause_music,        size=38).pack(side=LEFT, padx=5)
icon_btn(transport, "⏹", stop_music,         size=38).pack(side=LEFT, padx=5)
icon_btn(transport, "⏭", next_song,          size=38).pack(side=LEFT, padx=5)

vol_row = Frame(ctrl, bg=COLORS["header_bg"])
vol_row.pack(fill=X, padx=30, pady=(2, 10))
Label(vol_row, text="🔊", bg=COLORS["header_bg"],
      fg=COLORS["text_muted"], font=FONT_BODY).pack(side=LEFT, padx=(0, 6))
vol_scale = ttk.Scale(vol_row, from_=0, to=100, command=set_volume)
vol_scale.set(70); vol_scale.pack(side=LEFT, fill=X, expand=True)
set_volume(70)

# ── TAB 3: Search ─────────────────────────────────────────────────────────────
tab_search = ttk.Frame(notebook)
notebook.add(tab_search, text="  Search  ")
left_search = Frame(tab_search, bg=COLORS["bg"], width=240)
left_search.pack(side=LEFT, fill=Y); left_search.pack_propagate(False)
Frame(tab_search, bg=COLORS["border"], width=1).pack(side=LEFT, fill=Y)
right_search = Frame(tab_search, bg=COLORS["surface"])
right_search.pack(side=LEFT, fill=BOTH, expand=True)

section_label(left_search, "Quick Search")
song_search_entry = styled_entry(left_search, placeholder="Song name…")
ttk.Button(left_search, text="⌕  Search", style="Accent.TButton",
           command=lambda: search_for_song(search_log, song_search_entry)).pack(
    fill=X, padx=12, pady=(0, 8))
section_label(left_search, "Advanced — Search by Tag")
Label(left_search, text="Artist", bg=COLORS["bg"], fg=COLORS["text_dim"],
      font=FONT_SMALL, padx=14).pack(anchor=W)
artist_entry = styled_entry(left_search, placeholder="Artist name…")
Label(left_search, text="Genre", bg=COLORS["bg"], fg=COLORS["text_dim"],
      font=FONT_SMALL, padx=14).pack(anchor=W)
genre_entry = styled_entry(left_search, placeholder="Genre…")
ttk.Button(left_search, text="⌕  Advanced Search", style="Ghost.TButton",
           command=lambda: advanced_search(search_log, artist_entry, genre_entry)).pack(
    fill=X, padx=12, pady=(0, 4))
ttk.Button(left_search, text="✕  Clear Results", style="Ghost.TButton",
           command=lambda: clear_log(search_log)).pack(fill=X, padx=12, pady=2)

Label(right_search, text="Search Results", bg=COLORS["surface"],
      fg=COLORS["text_dim"], font=FONT_SMALL, padx=12, pady=6).pack(anchor=W)
Frame(right_search, bg=COLORS["border"], height=1).pack(fill=X)
search_log_frame, search_log = make_log_widget(right_search)
search_log_frame.pack(fill=BOTH, expand=True, padx=6, pady=6)

# ── TAB 4: Playlists ──────────────────────────────────────────────────────────
tab_pl = ttk.Frame(notebook)
notebook.add(tab_pl, text="  Playlists  ")
left_pl = Frame(tab_pl, bg=COLORS["bg"], width=240)
left_pl.pack(side=LEFT, fill=Y); left_pl.pack_propagate(False)
Frame(tab_pl, bg=COLORS["border"], width=1).pack(side=LEFT, fill=Y)
right_pl = Frame(tab_pl, bg=COLORS["surface"])
right_pl.pack(side=LEFT, fill=BOTH, expand=True)

pl_hdr = Frame(right_pl, bg=COLORS["surface2"], height=34)
pl_hdr.pack(fill=X); pl_hdr.pack_propagate(False)
Label(pl_hdr, text="SAVED PLAYLISTS", bg=COLORS["surface2"], fg=COLORS["accent"],
      font=("Segoe UI", 7, "bold"), padx=14).pack(side=LEFT, pady=8)

pl_lb_frame = Frame(right_pl, bg=COLORS["surface"])
pl_lb_frame.pack(fill=BOTH, expand=True, padx=6, pady=6)
pl_listbox = Listbox(pl_lb_frame, font=FONT_BODY,
    bg=COLORS["entry_bg"], fg=COLORS["text"],
    selectbackground=COLORS["highlight"], selectforeground=COLORS["accent2"],
    relief="flat", bd=0, activestyle="none")
pl_sb = ttk.Scrollbar(pl_lb_frame, command=pl_listbox.yview)
pl_listbox.config(yscrollcommand=pl_sb.set)
pl_sb.pack(side=RIGHT, fill=Y); pl_listbox.pack(fill=BOTH, expand=True)

Frame(right_pl, bg=COLORS["border"], height=1).pack(fill=X)
pl_log_frame, pl_log = make_log_widget(right_pl)
pl_log_frame.configure(height=80); pl_log_frame.pack(fill=X, padx=6, pady=4)
pl_log_frame.pack_propagate(False)

section_label(left_pl, "Create Playlist")
Label(left_pl, text="Name", bg=COLORS["bg"], fg=COLORS["text_dim"],
      font=FONT_SMALL, padx=14).pack(anchor=W)
playlist_name_entry = styled_entry(left_pl, placeholder="Playlist name…")
ttk.Button(left_pl, text="＋  Create from Library", style="Accent.TButton",
           command=lambda: create_playlist(pl_log, playlist_name_entry, pl_listbox)).pack(
    fill=X, padx=12, pady=(0, 6))
section_label(left_pl, "Manage")
ttk.Button(left_pl, text="▶  Load Selected",   style="Ghost.TButton",
           command=lambda: load_playlist(pl_log, pl_listbox)).pack(fill=X, padx=12, pady=2)
ttk.Button(left_pl, text="✕  Delete Selected", style="Danger.TButton",
           command=lambda: delete_playlist(pl_log, pl_listbox)).pack(fill=X, padx=12, pady=2)
section_label(left_pl, "Import / Export")
ttk.Button(left_pl, text="↗  Save to File",   style="Ghost.TButton",
           command=lambda: save_playlists(pl_log)).pack(fill=X, padx=12, pady=2)
ttk.Button(left_pl, text="↙  Load from File", style="Ghost.TButton",
           command=lambda: load_playlists_from_file(pl_log, pl_listbox)).pack(
    fill=X, padx=12, pady=2)

# ── TAB 5: Organize ───────────────────────────────────────────────────────────
tab_org = ttk.Frame(notebook)
notebook.add(tab_org, text="  Organize  ")
left_org = Frame(tab_org, bg=COLORS["bg"], width=240)
left_org.pack(side=LEFT, fill=Y); left_org.pack_propagate(False)
Frame(tab_org, bg=COLORS["border"], width=1).pack(side=LEFT, fill=Y)
right_org = Frame(tab_org, bg=COLORS["surface"])
right_org.pack(side=LEFT, fill=BOTH, expand=True)

section_label(left_org, "Sort by Metadata")
Label(left_org,
      text="Move files into subfolders\nautomatically using ID3 tags\n(Artist, Album, Genre, etc.)",
      bg=COLORS["bg"], fg=COLORS["text_dim"],
      font=FONT_SMALL, padx=14, justify=LEFT, wraplength=200).pack(anchor=W, pady=6)
ttk.Button(left_org, text="⊞  Organize by ID3 Tags", style="Accent.TButton",
           command=lambda: organize_music_by_id3(org_log)).pack(fill=X, padx=12, pady=4)

Label(right_org, text="Organize Log", bg=COLORS["surface"],
      fg=COLORS["text_dim"], font=FONT_SMALL, padx=12, pady=6).pack(anchor=W)
Frame(right_org, bg=COLORS["border"], height=1).pack(fill=X)
org_log_frame, org_log = make_log_widget(right_org)
org_log_frame.pack(fill=BOTH, expand=True, padx=6, pady=6)

# ── TAB 6: Settings ───────────────────────────────────────────────────────────
tab_settings = ttk.Frame(notebook)
notebook.add(tab_settings, text="  Settings  ")
s_inner = Frame(tab_settings, bg=COLORS["bg"])
s_inner.pack(fill=BOTH, expand=True, padx=30, pady=16)

section_label(s_inner, "Keyboard Shortcuts")
for key, desc in [
    ("Ctrl + O",     "Open / scan directory"),
    ("Ctrl + P",     "Play selected track"),
    ("Space",        "Pause / resume playback"),
    ("→  Right",     "Skip to next track"),
    ("←  Left",      "Go to previous track"),
    ("Double-click", "Play track from library list"),
]:
    row = Frame(s_inner, bg=COLORS["bg"])
    row.pack(fill=X, padx=12, pady=2)
    Label(row, text=key, bg=COLORS["surface2"], fg=COLORS["accent2"],
          font=FONT_MONO, width=16, anchor=CENTER, padx=4, pady=3).pack(side=LEFT)
    Label(row, text=f"  {desc}", bg=COLORS["bg"],
          fg=COLORS["text_dim"], font=FONT_SMALL).pack(side=LEFT)

section_label(s_inner, "About")

# ── Logo + title card ─────────────────────────────────────────────────────────
about_card = Frame(s_inner, bg=COLORS["surface2"])
about_card.pack(fill=X, padx=12, pady=(4, 0))

_about_logo_ref = None
try:
    _ico2 = Image.open(resource_path("HarmonyHaven.ico")).convert("RGBA")
    _ico2 = _ico2.resize((64, 64), Image.LANCZOS)
    _about_logo_ref = ImageTk.PhotoImage(_ico2)
    Label(about_card, image=_about_logo_ref,
          bg=COLORS["surface2"], padx=14, pady=14).pack(side=LEFT)
except Exception:
    pass

Frame(about_card, bg=COLORS["border"], width=1).pack(side=LEFT, fill=Y, pady=10)
about_title_block = Frame(about_card, bg=COLORS["surface2"])
about_title_block.pack(side=LEFT, padx=14, pady=14)
Label(about_title_block, text="HarmonyHaven  v2.0",
      bg=COLORS["surface2"], fg=COLORS["accent2"], font=FONT_HEADER).pack(anchor=W)
Label(about_title_block, text="Created by Alejandro X. Solis",
      bg=COLORS["surface2"], fg=COLORS["text"], font=FONT_BODY).pack(anchor=W)
Label(about_title_block, text="TechFusion Repairs LLC",
      bg=COLORS["surface2"], fg=COLORS["text_dim"], font=FONT_SMALL).pack(anchor=W)
Label(about_title_block, text="© 2024  ·  MIT License  ·  All Rights Reserved",
      bg=COLORS["surface2"], fg=COLORS["text_muted"],
      font=FONT_SMALL).pack(anchor=W, pady=(4, 0))

# ── Description card ──────────────────────────────────────────────────────────
desc_card = Frame(s_inner, bg=COLORS["surface"], bd=0)
desc_card.pack(fill=X, padx=12, pady=(2, 4))
Frame(desc_card, bg=COLORS["accent"], height=2).pack(fill=X)
desc_inner = Frame(desc_card, bg=COLORS["surface"])
desc_inner.pack(fill=X, padx=16, pady=12)

Label(desc_inner, text="About This Software",
      bg=COLORS["surface"], fg=COLORS["accent"],
      font=("Segoe UI", 8, "bold")).pack(anchor=W, pady=(0, 6))

description = (
    "HarmonyHaven is a free, open-source music library manager and player built for "
    "music lovers who want full control over their local collection. Scan any folder "
    "on your PC to instantly load your entire library, play tracks with a clean "
    "transport interface, and keep your files organized with powerful tools.\n\n"
    "Key features include duplicate detection using MD5 hashing, automatic file "
    "organization by ID3 tags (Artist, Album, Genre), playlist creation and management, "
    "advanced search by song name or metadata, and CSV export for your full library. "
    "The built-in SQLite database keeps your library indexed for fast lookups even "
    "across thousands of files.\n\n"
    "HarmonyHaven is developed and maintained by Alejandro X. Solis at TechFusion "
    "Repairs LLC and is released free of charge under the MIT License."
)
Label(desc_inner, text=description,
      bg=COLORS["surface"], fg=COLORS["text_dim"],
      font=FONT_SMALL, justify=LEFT, wraplength=680).pack(anchor=W)

# ── Features quick-list ───────────────────────────────────────────────────────
features_frame = Frame(s_inner, bg=COLORS["surface"])
features_frame.pack(fill=X, padx=12, pady=(0, 4))

col1 = Frame(features_frame, bg=COLORS["surface"])
col1.pack(side=LEFT, fill=X, expand=True)
col2 = Frame(features_frame, bg=COLORS["surface"])
col2.pack(side=LEFT, fill=X, expand=True)

for i, feat in enumerate([
    "♪  Music playback (MP3, FLAC, WAV, M4A, OGG, AAC)",
    "⧉  Duplicate detection via MD5 hashing",
    "⊞  Auto-organize by ID3 tags",
    "⌕  Quick & advanced search",
    "📋  Playlist create, save & load",
    "↗  CSV library export",
    "🗄  SQLite library database",
    "⌫  Empty folder cleanup",
]):
    parent = col1 if i % 2 == 0 else col2
    Label(parent, text=feat,
          bg=COLORS["surface"], fg=COLORS["text_dim"],
          font=FONT_SMALL, anchor=W, padx=4, pady=2).pack(anchor=W)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 7 — CONTACT
# ══════════════════════════════════════════════════════════════════════════════
tab_contact = ttk.Frame(notebook)
notebook.add(tab_contact, text="  Contact  ")

# Scrollable canvas so content never gets clipped
contact_canvas = Canvas(tab_contact, bg=COLORS["bg"], highlightthickness=0)
contact_canvas.pack(fill=BOTH, expand=True)
contact_inner = Frame(contact_canvas, bg=COLORS["bg"])
contact_canvas.create_window((0, 0), window=contact_inner, anchor=NW)
contact_inner.bind("<Configure>",
    lambda e: contact_canvas.configure(scrollregion=contact_canvas.bbox("all")))

# ── Hero strip ────────────────────────────────────────────────────────────────
hero = Frame(contact_inner, bg=COLORS["surface2"])
hero.pack(fill=X)
Frame(hero, bg=COLORS["accent"], height=3).pack(fill=X)
hero_body = Frame(hero, bg=COLORS["surface2"])
hero_body.pack(fill=X, padx=30, pady=20)

Label(hero_body, text="Get in Touch",
      bg=COLORS["surface2"], fg=COLORS["accent2"],
      font=("Segoe UI", 16, "bold")).pack(anchor=W)
Label(hero_body,
      text="We're here to help. Reach out for support, feature requests, or just to say hello.",
      bg=COLORS["surface2"], fg=COLORS["text_dim"],
      font=FONT_BODY, wraplength=700, justify=LEFT).pack(anchor=W, pady=(4, 0))
Label(hero_body,
      text="We aim to respond to all inquiries within 24–48 hours.",
      bg=COLORS["surface2"], fg=COLORS["success"],
      font=("Segoe UI", 9, "italic")).pack(anchor=W, pady=(6, 0))

Frame(contact_inner, bg=COLORS["border"], height=1).pack(fill=X)

# ── Two-column layout ─────────────────────────────────────────────────────────
cols = Frame(contact_inner, bg=COLORS["bg"])
cols.pack(fill=BOTH, expand=True, padx=20, pady=20)

left_col  = Frame(cols, bg=COLORS["bg"])
left_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
right_col = Frame(cols, bg=COLORS["bg"])
right_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))

# ── Helper: contact info card ─────────────────────────────────────────────────
def contact_card(parent, heading, items):
    """items = list of (icon, label, value, is_link, url)"""
    import webbrowser
    card = Frame(parent, bg=COLORS["surface"])
    card.pack(fill=X, pady=(0, 12))
    Frame(card, bg=COLORS["accent"], height=2).pack(fill=X)
    inner = Frame(card, bg=COLORS["surface"])
    inner.pack(fill=X, padx=16, pady=12)
    Label(inner, text=heading.upper(),
          bg=COLORS["surface"], fg=COLORS["accent"],
          font=("Segoe UI", 7, "bold")).pack(anchor=W, pady=(0, 8))
    for icon, label, value, is_link, url in items:
        row = Frame(inner, bg=COLORS["surface"])
        row.pack(fill=X, pady=3)
        Label(row, text=icon, bg=COLORS["surface"],
              fg=COLORS["accent2"], font=("Segoe UI", 12), width=2).pack(side=LEFT)
        Label(row, text=f"  {label}",
              bg=COLORS["surface"], fg=COLORS["text_dim"],
              font=FONT_SMALL, width=10, anchor=W).pack(side=LEFT)
        if is_link:
            lnk = Label(row, text=value,
                        bg=COLORS["surface"], fg=COLORS["accent"],
                        font=FONT_SMALL, cursor="hand2", anchor=W)
            lnk.pack(side=LEFT, fill=X)
            lnk.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
            lnk.bind("<Enter>", lambda e, w=lnk: w.config(fg=COLORS["accent2"],
                                                           font=("Segoe UI", 8, "underline")))
            lnk.bind("<Leave>", lambda e, w=lnk: w.config(fg=COLORS["accent"],
                                                           font=FONT_SMALL))
        else:
            Label(row, text=value,
                  bg=COLORS["surface"], fg=COLORS["text"],
                  font=FONT_SMALL, anchor=W).pack(side=LEFT)

# ── Left column cards ─────────────────────────────────────────────────────────
contact_card(left_col, "Email", [
    ("✉", "Primary",   "TechFusionRepairs@gmail.com",
     True,  "mailto:TechFusionRepairs@gmail.com"),
    ("✉", "Alternate", "TechFusionRepairsLLC@gmail.com",
     True,  "mailto:TechFusionRepairsLLC@gmail.com"),
])

contact_card(left_col, "Messaging", [
    ("💬", "WhatsApp", "(940) 808-5105",
     True, "https://wa.me/19408085105"),
])

# ── Right column cards ────────────────────────────────────────────────────────
contact_card(right_col, "Online", [
    ("🌐", "Website",
     "alejandroxsolis93.wixsite.com/techfusionrepairsllc",
     True, "https://alejandroxsolis93.wixsite.com/techfusionrepairsllc"),
    ("💻", "GitHub",
     "github.com/TechFusionRepairs",
     True, "https://github.com/TechFusionRepairs"),
])

# ── Donate card (full width) ──────────────────────────────────────────────────
import webbrowser

donate_card = Frame(contact_inner, bg=COLORS["surface"])
donate_card.pack(fill=X, padx=20, pady=(0, 20))
Frame(donate_card, bg=COLORS["warning"], height=2).pack(fill=X)
donate_inner = Frame(donate_card, bg=COLORS["surface"])
donate_inner.pack(fill=X, padx=16, pady=16)

donate_top = Frame(donate_inner, bg=COLORS["surface"])
donate_top.pack(fill=X)
Label(donate_top, text="☕  Support the Project",
      bg=COLORS["surface"], fg=COLORS["accent2"],
      font=("Segoe UI", 11, "bold")).pack(side=LEFT)

Label(donate_inner,
      text="HarmonyHaven is completely free and always will be. Donations are not required, "
           "but they are deeply appreciated — they help cover development time, hosting, and "
           "keep new features coming. Every contribution, no matter the size, means a lot.",
      bg=COLORS["surface"], fg=COLORS["text_dim"],
      font=FONT_SMALL, wraplength=760, justify=LEFT).pack(anchor=W, pady=(8, 12))

paypal_btn = Canvas(donate_inner, width=220, height=38,
                    bg=COLORS["surface"], highlightthickness=0, cursor="hand2")
paypal_btn.pack(anchor=W)
PAYPAL_URL = "https://www.paypal.com/donate/?hosted_button_id=CESA5GQALY386"

def _draw_paypal(col):
    paypal_btn.delete("all")
    r = 8
    w, h = 220, 38
    paypal_btn.create_arc(0, 0, 2*r, 2*r, start=90,  extent=90,  fill=col, outline=col)
    paypal_btn.create_arc(w-2*r, 0, w, 2*r, start=0,   extent=90,  fill=col, outline=col)
    paypal_btn.create_arc(0, h-2*r, 2*r, h, start=180, extent=90,  fill=col, outline=col)
    paypal_btn.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=col, outline=col)
    paypal_btn.create_rectangle(r, 0, w-r, h, fill=col, outline=col)
    paypal_btn.create_rectangle(0, r, w, h-r, fill=col, outline=col)
    paypal_btn.create_text(w//2, h//2, text="💙  Donate via PayPal",
                           fill=COLORS["bg"], font=("Segoe UI", 10, "bold"))

_PAYPAL_NORMAL = "#009cde"
_PAYPAL_HOVER  = "#0070ba"
_draw_paypal(_PAYPAL_NORMAL)
paypal_btn.bind("<Enter>",    lambda e: _draw_paypal(_PAYPAL_HOVER))
paypal_btn.bind("<Leave>",    lambda e: _draw_paypal(_PAYPAL_NORMAL))
paypal_btn.bind("<Button-1>", lambda e: webbrowser.open(PAYPAL_URL))

Label(donate_inner, text=PAYPAL_URL,
      bg=COLORS["surface"], fg=COLORS["text_muted"],
      font=("Segoe UI", 7), cursor="hand2").pack(anchor=W, pady=(6, 0))

# ──────────────────────────────────────────────────────────────────────────────
#  INIT
# ──────────────────────────────────────────────────────────────────────────────
auto_load_playlists()
refresh_playlist_list(pl_listbox)
root.mainloop()


# Created by Alejandro X. Solis Owner of TechFusion Repairs LLC
# MIT License
# All Rights Reserved.
# See LICENSE file for more details.
# © 2024 TechFusion Repairs LLC. All rights reserved.