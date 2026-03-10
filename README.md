<div align="center">

<img src="HarmonyHaven.ico" alt="HarmonyHaven Logo" width="120"/>

# HarmonyHaven

**v2.0  ·  TechFusion Repairs LLC**

*An all-in-one music library manager and player for your desktop*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)](https://github.com/TechFusionRepairs/HarmonyHaven/releases)
[![Version](https://img.shields.io/badge/Version-2.0.0-brightgreen)](https://github.com/TechFusionRepairs/HarmonyHaven/releases/tag/v2.0.0)

[Download EXE](https://github.com/TechFusionRepairs/HarmonyHaven/releases) · [Report a Bug](https://github.com/TechFusionRepairs/HarmonyHaven/issues) · [Request a Feature](https://github.com/TechFusionRepairs/HarmonyHaven/issues)

</div>

---

## What is HarmonyHaven?

HarmonyHaven is a free, open-source desktop application built for music lovers who want full control over their local collection. Whether you have hundreds or thousands of files scattered across your hard drive, HarmonyHaven helps you scan, organize, deduplicate, search, and play your music — all from one clean interface.

Developed and maintained by **Alejandro X. Solis**, CEO of **TechFusion Repairs LLC**, HarmonyHaven is released free of charge and built with Python, Tkinter, pygame, and SQLite.

---

## What's New in v2.0

- **Redesigned UI** — full dark theme matched to the HarmonyHaven logo colors (deep navy, sky blue, light cyan)
- **Logo displayed** in the header bar and About section
- **Improved playback** — pause/resume toggle fixed, next/prev syncs the library list, volume applies on startup
- **Contact tab** — clickable email, WhatsApp, website, and PayPal donate links
- **Database layer rewrite** — faster bulk inserts, advanced search, path update after file moves, and safe connection handling
- **Playlist delete button** added
- **Export to CSV** now uses a Save As dialog
- **Additional formats** — `.ogg` and `.aac` support added
- See the full [Release Notes](RELEASE_NOTES_v2.0.md) for the complete changelog

---

## Features

| Feature | Description |
|---|---|
| 🎵 **Music Playback** | Play, pause, stop, skip — supports MP3, FLAC, WAV, M4A, OGG, AAC |
| 📂 **Directory Scanner** | Recursively scans any folder and loads your full library instantly |
| ⧉ **Duplicate Finder** | Detects exact duplicate files using MD5 hashing and removes them safely |
| ⊞ **ID3 Organizer** | Auto-moves files into subfolders by Artist, Album, Genre, Year, or any ID3 tag |
| 🔍 **Search** | Quick search by filename or advanced search by Artist and Genre metadata |
| 📋 **Playlists** | Create, save, load, and delete playlists — stored as portable JSON files |
| 🗄 **SQLite Database** | Indexes your library for fast lookups across thousands of files |
| ↗ **CSV Export** | Export your full track list to a spreadsheet-ready CSV file |
| ⌫ **Folder Cleanup** | Deletes empty folders left behind after organizing or removing duplicates |
| 💬 **Contact & Support** | Built-in contact tab with clickable links and PayPal donation support |

---

## Screenshots

> _Screenshots coming soon — run the app to see the full dark theme UI._

---

## Installation

### Option A — Download the EXE (Recommended, Windows only)

No Python required. Just download and run.

1. Go to the [Releases page](https://github.com/TechFusionRepairs/HarmonyHaven/releases)
2. Download `HarmonyHaven.exe` from the latest release
3. Place it anywhere on your PC and double-click to launch

> **Note:** Windows SmartScreen may show a warning the first time. Click **More info → Run anyway**. This is a known false positive with PyInstaller-built apps.

---

### Option B — Run from Source

**Requirements:** Python 3.8 or higher

**1. Clone the repository**
```bash
git clone https://github.com/TechFusionRepairs/HarmonyHaven.git
cd HarmonyHaven
```

**2. Install dependencies**
```bash
pip install pygame mutagen Pillow
```

**3. Run the app**
```bash
python HarmonyHaven.py
```

> Make sure `HarmonyHaven.ico` is in the same folder as `HarmonyHaven.py` before running.

---

### Option C — Build the EXE yourself

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon="HarmonyHaven.ico" --add-data="HarmonyHaven.ico;." --name="HarmonyHaven" HarmonyHaven.py
```

Your EXE will appear in the `dist/` folder. See [HarmonyHaven_BuildGuide.docx](HarmonyHaven_BuildGuide.docx) for the full walkthrough including common errors and fixes.

---

## How to Use

### Scanning Your Music Library
1. Open the **File Ops** tab
2. Click **Scan Directory** and choose your music folder
3. HarmonyHaven will recursively find all supported audio files and load them into the library

### Playing Music
1. Switch to the **Playback** tab
2. Select a track from the list (or double-click to play immediately)
3. Use the transport controls — ⏮ ▶ ⏸ ⏹ ⏭ — and the volume slider

### Finding & Removing Duplicates
1. Scan a directory first
2. In the **File Ops** tab, click **Find & Remove Duplicates**
3. HarmonyHaven compares MD5 hashes — exact duplicates are confirmed before deletion

### Organizing by ID3 Tags
1. Scan a directory
2. Go to the **Organize** tab → click **Organize by ID3 Tags**
3. Choose a primary folder tag (e.g. Artist) and a subfolder tag (e.g. Album)
4. Select a destination folder — files are moved automatically

### Searching
- **Quick Search** (Search tab): search by filename
- **Advanced Search**: filter by Artist and/or Genre using ID3 metadata

### Playlists
- Create a playlist from your current library with a name
- Load any saved playlist to switch your active library
- Save playlists to a `.json` file and reload them anytime

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `Ctrl + O` | Open / scan directory |
| `Ctrl + P` | Play selected track |
| `Space` | Pause / resume |
| `→` Right | Next track |
| `←` Left | Previous track |
| `Double-click` | Play track from library list |

---

## Project Structure

```
HarmonyHaven/
├── HarmonyHaven.py          # Main application
├── database_manager.py      # SQLite library database layer
├── HarmonyHaven.ico         # App icon (required at runtime)
├── playlists.json           # Saved playlists (created on first save)
├── harmonyhaven_music.db    # SQLite database (created on first scan)
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `pygame` | Audio playback engine |
| `mutagen` | ID3 tag reading |
| `Pillow` | Image handling for the logo |
| `tkinter` | GUI framework (included with Python) |
| `sqlite3` | Library database (included with Python) |

Install all at once:
```bash
pip install pygame mutagen Pillow
```

---

## Contributing

Contributions are welcome! Here's how to get involved:

1. **Open an issue** for bugs or feature requests — please check existing issues first
2. **Fork** the repository
3. **Create a branch** — `git checkout -b feature/your-feature-name`
4. **Make your changes** and test them
5. **Commit** — `git commit -m "Add: your feature description"`
6. **Push** — `git push origin feature/your-feature-name`
7. **Open a Pull Request** with a clear description of what you changed and why

For major changes, please open an issue first to discuss the approach.

---

## License

HarmonyHaven is released under the [MIT License](LICENSE).

```
MIT License — © 2024 TechFusion Repairs LLC
Permission is granted to use, copy, modify, and distribute this software
for any purpose, with or without charge, provided the copyright notice
and this permission notice appear in all copies.
```

---

## Support the Project

HarmonyHaven is completely free and always will be. If it saves you time or you just want to say thanks, donations are deeply appreciated — they help fund development time and keep new features coming.

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-009cde?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=CESA5GQALY386)

---

## Contact

**Developer:** Alejandro X. Solis  
**Company:** TechFusion Repairs LLC  
**Email:** [TechFusionRepairs@gmail.com](mailto:TechFusionRepairs@gmail.com) · [TechFusionRepairsLLC@gmail.com](mailto:TechFusionRepairsLLC@gmail.com)  
**WhatsApp:** [(940) 808-5105](https://wa.me/19408085105)  
**Website:** [alejandroxsolis93.wixsite.com/techfusionrepairsllc](https://alejandroxsolis93.wixsite.com/techfusionrepairsllc)  

> We aim to respond to all inquiries within 24–48 hours.

---

<div align="center">

© 2024 TechFusion Repairs LLC · All Rights Reserved · MIT License

</div>
