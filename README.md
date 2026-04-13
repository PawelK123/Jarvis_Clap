# 👏 jarvis-clap

> *"Just a small idea... F.R.I.D.A.Y., hit it."*

Launch **Claude** and **Spotify** with a double clap — no keyboard, no mouse, just your hands.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ What it does

jarvis-clap listens to your microphone in the background. When it detects **two claps in quick succession**, it:

1. 🎵 Opens **Spotify** and plays *Should I Stay or Should I Go* by The Clash
2. 🤖 Opens the **Claude** desktop app
3. 🖥️ Snaps both windows **side by side** on your screen

---

## 🚀 Getting started

### Requirements

- Windows 10/11
- Python 3.8+
- [Spotify](https://www.spotify.com/download/) desktop app
- [Claude](https://claude.ai/download) desktop app
- A microphone

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/jarvis-clap.git
cd jarvis-clap
pip install -r requirements.txt
```

> **Note:** `sounddevice` requires [PortAudio](http://www.portaudio.com/). On most systems it installs automatically with the pip package.

### Run

```bash
python jarvis_clap.py
```

Or double-click `uruchom.bat`.

---

## ⚙️ Configuration

At the top of `jarvis_clap.py` you can tweak:

| Variable | Default | Description |
|---|---|---|
| `CZULOSC` | `0.7` | Clap detection threshold (0.1 = very sensitive, 0.9 = less sensitive) |
| `PODWOJNE_KLASNIECIE` | `True` | `True` = requires double clap, `False` = single clap |
| `CZAS_MIEDZY` | `1` | Max time (seconds) between two claps |

---


## ⚠️ Platform support

**Windows only.** Window management relies on the Win32 API (`ctypes.windll`). macOS and Linux are not supported.

---

## 💡 Inspiration

In the Iron Man and Avengers films, Tony Stark never touches a keyboard. He walks into his lab, says a word or makes a gesture — and J.A.R.V.I.S. (Just A Rather Very Intelligent System) instantly springs to life: music starts playing, screens light up, systems initialize. Everything responds to him immediately, effortlessly, like the technology is an extension of his hands.
That idea stuck. Why should launching your tools require finding the keyboard, moving the mouse, clicking through windows? jarvis-clap is a small tribute to that vision — two claps, and your environment is ready. No Iron Man suit required.

---

