import numpy as np
import sounddevice as sd
import subprocess
import time
import os
import sys
import ctypes
import threading

# ============================================================
#  USTAWIENIA - możesz dostosować
# ============================================================
CZULOSC = 0.7          # Próg głośności klasnięcia (0.1 = bardzo czułe, 0.9 = mało czułe)
PODWOJNE_KLASNIECIE = True   # True = wymaga dwóch klasnięć, False = jedno klasnięcie
CZAS_MIEDZY = 1      # Max czas (sekundy) między dwoma klasnięciami
# ============================================================

SAMPLE_RATE = 44100
CHUNK = 1024
SW_RESTORE = 9

def _znajdz_uchwyt_okna(fraza_tytulu, timeout=8.0):
    """Szuka widocznego okna po fragmencie tytułu (bez względu na wielkość liter)."""
    user32 = ctypes.windll.user32
    fraza = fraza_tytulu.lower()
    start = time.time()

    while time.time() - start < timeout:
        znalezione = []

        @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def enum_windows(hwnd, lparam):
            if user32.IsWindowVisible(hwnd):
                buf = ctypes.create_unicode_buffer(512)
                user32.GetWindowTextW(hwnd, buf, 512)
                tytul = buf.value.strip().lower()
                if tytul and fraza in tytul:
                    znalezione.append(hwnd)
            return True

        user32.EnumWindows(enum_windows, 0)
        if znalezione:
            return znalezione[0]
        time.sleep(0.2)

    return None

def _pobierz_tytul_okna(hwnd):
    """Pobiera tytuł okna dla podanego uchwytu."""
    if not hwnd:
        return ""
    user32 = ctypes.windll.user32
    buf = ctypes.create_unicode_buffer(512)
    user32.GetWindowTextW(hwnd, buf, 512)
    return buf.value.strip()

def czekaj_na_start_piosenki_spotify(czas_startu_proby, timeout=18.0):
    """Czeka aż Spotify zacznie odtwarzać utwór; fallback to minimalny czas rozruchu."""
    fraza_utworu = "should i stay or should i go"
    tytuly_ogolne = {"spotify", "spotify free", "spotify premium"}
    start = time.time()
    minimalny_czas_rozruchu = 4.0

    while time.time() - start < timeout:
        hwnd_spotify = _znajdz_uchwyt_okna("spotify", timeout=0.4)
        tytul = _pobierz_tytul_okna(hwnd_spotify).lower()

        # Twardy warunek: rozpoznana nazwa docelowego utworu.
        if fraza_utworu in tytul:
            print("✅ Spotify zaczęło grać docelową piosenkę.")
            return True

        # Miękki warunek awaryjny: w tytule pojawił się format 'artysta - utwór',
        # czyli nie jest to już tylko ekran startowy Spotify.
        if tytul and tytul not in tytuly_ogolne and " - " in tytul:
            print("✅ Spotify wygląda na odtwarzanie piosenki.")
            return True

        # W nowych wersjach Spotify tytuł okna bywa statyczny,
        # więc po krótkim, bezpiecznym czasie przechodzimy dalej.
        if time.time() - czas_startu_proby >= minimalny_czas_rozruchu and hwnd_spotify:
            print("✅ Spotify jest otwarte i miało czas zacząć odtwarzanie.")
            return True

        time.sleep(0.35)

    print("⏱️ Spotify nie potwierdziło startu piosenki w czasie, lecę dalej.")
    return False

def ustaw_okna_na_pol_ekranu():
    """Ustawia Claude po lewej i Spotify po prawej stronie ekranu."""
    user32 = ctypes.windll.user32
    szer = user32.GetSystemMetrics(0)
    wys = user32.GetSystemMetrics(1)
    polowa = szer // 2

    hwnd_claude = _znajdz_uchwyt_okna("claude")
    hwnd_spotify = _znajdz_uchwyt_okna("spotify")

    if hwnd_claude:
        user32.ShowWindow(hwnd_claude, SW_RESTORE)
        user32.MoveWindow(hwnd_claude, 0, 0, polowa, wys, True)
    else:
        print("⚠️ Nie znalazłem okna Claude do ustawienia.")

    if hwnd_spotify:
        user32.ShowWindow(hwnd_spotify, SW_RESTORE)
        user32.MoveWindow(hwnd_spotify, polowa, 0, szer - polowa, wys, True)
    else:
        print("⚠️ Nie znalazłem okna Spotify do ustawienia.")

def otworz_claude():
    subprocess.Popen(["cmd", "/c", "start", "", "claude:"], shell=True)

def otworz_spotify_i_utwor():
    """Otwiera Spotify i odpala utwór 'Should I Stay or Should I Go'."""
    # URI utworu The Clash - Should I Stay or Should I Go
    track_uri = "spotify:track:39shmbIHICJ2Wxnk1fPSdz"
    fallback_search_uri = "spotify:search:should%20i%20stay%20or%20should%20i%20go"

    try:
        print("🎵 Otwieram Spotify...")
        subprocess.Popen(["cmd", "/c", "start", "", "spotify:"], shell=True)
        time.sleep(1.2)

        print("▶️ Odtwarzam: Should I Stay or Should I Go")
        subprocess.Popen(["cmd", "/c", "start", "", track_uri], shell=True)
        return time.time()
    except Exception:
        print("⚠️ Nie udało się odpalić konkretnego utworu, otwieram wyszukiwanie Spotify...")
        subprocess.Popen(["cmd", "/c", "start", "", fallback_search_uri], shell=True)
        return time.time()

def uruchom_i_uloz_okna():
    """Uruchamia aplikacje i układa ich okna obok siebie."""
    czas_startu_proby = otworz_spotify_i_utwor()
    czekaj_na_start_piosenki_spotify(czas_startu_proby)
    otworz_claude()
    ustaw_okna_na_pol_ekranu()

def wykryj_klasniecie(indata, threshold):
    """Zwraca True jeśli głośność przekracza próg"""
    volume = np.max(np.abs(indata))
    return volume > threshold

def main():
    print("=" * 50)
    print("  👏 Detektor Klasnięcia → Claude + Spotify")
    print("=" * 50)
    
    if PODWOJNE_KLASNIECIE:
        print(f"  Tryb: PODWÓJNE klasnięcie (max {CZAS_MIEDZY}s między nimi)")
    else:
        print(f"  Tryb: POJEDYNCZE klasnięcie")
    
    print(f"  Czułość: {CZULOSC}")
    print(f"  Naciśnij Ctrl+C aby zakończyć")
    print("=" * 50)
    print("\n🎤 Nasłuchuję... klasnij!\n")

    ostatnie_klasniecie = 0
    licznik = 0

    def callback(indata, frames, time_info, status):
        nonlocal ostatnie_klasniecie, licznik
        
        if wykryj_klasniecie(indata, CZULOSC):
            teraz = time.time()
            odstep = teraz - ostatnie_klasniecie
            
            
            ostatnie_klasniecie = teraz
            licznik += 1
            print(f"  👏 Klasnięcie #{licznik} wykryte!")

            
            
            if licznik >= 2 and odstep <= CZAS_MIEDZY:
                print("\n🚀 Podwójne klasnięcie! Uruchamiam Claude + Spotify!\n")
                threading.Thread(target=uruchom_i_uloz_okna, daemon=True).start()
                licznik = 0
            elif odstep > CZAS_MIEDZY:
                # Za wolno - reset licznika
                licznik = 1

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            blocksize=CHUNK,
            callback=callback
        ):
            while True:
                time.sleep(0.1)
                # Reset licznika po długim czasie bez klasnięcia
                if PODWOJNE_KLASNIECIE and licznik == 1:
                    if time.time() - ostatnie_klasniecie > CZAS_MIEDZY:
                        licznik = 0

    except KeyboardInterrupt:
        print("\n\n👋 Zatrzymano. Do zobaczenia!")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        if "PortAudio" in str(e) or "No Default Input" in str(e):
            print("   Upewnij się że mikrofon jest podłączony i działa.")
        sys.exit(1)

if __name__ == "__main__":
    main()
