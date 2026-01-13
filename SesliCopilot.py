import tkinter as tk
from tkinter import ttk, scrolledtext
from pynput import keyboard
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import numpy as np
import os
import pyautogui
import time
import pyperclip
import threading

# Koordinatlar (Copilot Chat)
mesaj_yazma_alani = (1099, 654)
mesaj_gonder_buton = (1333, 691)

# Kayıt durumu
kaydediliyor = False
ses_verisi = []
sample_rate = 16000

class SesliCopilotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ Sesli Copilot")
        self.root.geometry("350x500")
        self.root.configure(bg="#1e1e1e")
        
        # Animasyon için
        self.mikrofon_yanik = True
        self.animasyon_aktif = False
        self.animasyon_adim = 0
        
        # Başlık
        baslik = tk.Label(
            root, 
            text="🎙️ Sesli Copilot", 
            font=("Arial", 14, "bold"),
            bg="#1e1e1e",
            fg="#00d4ff"
        )
        baslik.pack(pady=8)
        
        # Durum göstergesi
        self.durum_frame = tk.Frame(root, bg="#1e1e1e")
        self.durum_frame.pack(pady=5)
        
        self.durum_label = tk.Label(
            self.durum_frame,
            text="⚪ Beklemede",
            font=("Arial", 10, "bold"),
            bg="#1e1e1e",
            fg="#888888"
        )
        self.durum_label.pack()
        
        # Mikrofon animasyon canvas'ı
        self.canvas = tk.Canvas(
            root,
            width=150,
            height=150,
            bg="#1e1e1e",
            highlightthickness=0
        )
        self.canvas.pack(pady=5)
        
        # Mikrofon simgesi (merkez daire)
        self.mikrofon_daire = self.canvas.create_oval(
            60, 60, 90, 90,
            fill="#404040",
            outline="#00d4ff",
            width=2
        )
        
        # Animasyon daireleri (3 katman)
        self.animasyon_daireleri = []
        for i in range(3):
            daire = self.canvas.create_oval(
                75, 75, 75, 75,
                fill="",
                outline="",
                width=2
            )
            self.animasyon_daireleri.append(daire)
        
        # Algılanan metin alanı
        tk.Label(
            root,
            text="📝 Algılanan Metin:",
            font=("Arial", 9, "bold"),
            bg="#1e1e1e",
            fg="#00d4ff"
        ).pack(pady=(8, 3))
        
        self.metin_alani = scrolledtext.ScrolledText(
            root,
            width=38,
            height=4,
            font=("Arial", 9),
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="#00d4ff",
            wrap=tk.WORD
        )
        self.metin_alani.pack(padx=10, pady=3)
        
        # Log alanı
        tk.Label(
            root,
            text="📋 Sistem Logu:",
            font=("Arial", 9, "bold"),
            bg="#1e1e1e",
            fg="#00d4ff"
        ).pack(pady=(8, 3))
        
        self.log_alani = scrolledtext.ScrolledText(
            root,
            width=38,
            height=5,
            font=("Consolas", 7),
            bg="#0d0d0d",
            fg="#00ff00",
            insertbackground="#00d4ff",
            wrap=tk.WORD
        )
        self.log_alani.pack(padx=10, pady=3)
        
        self.log("✅ Program başlatıldı")
        self.log("⌨️  END tuşuna basarak kayıt başlatabilirsiniz")
        
        # Ses akışını başlat
        self.ses_stream = sd.InputStream(
            callback=self.ses_callback, 
            channels=1, 
            samplerate=sample_rate
        )
        self.ses_stream.start()
        
        # Global klavye dinleyicisini başlat (non-blocking)
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
    
    def log(self, mesaj):
        """Log alanına mesaj ekle"""
        self.log_alani.insert(tk.END, f"{mesaj}\n")
        self.log_alani.see(tk.END)
    
    def mikrofon_animasyon(self):
        """Google tarzı mikrofon dalgalanma animasyonu"""
        if self.animasyon_aktif:
            self.animasyon_adim += 1
            
            # Her daire için farklı fazda genişleme
            for i, daire in enumerate(self.animasyon_daireleri):
                # Faz farkı ekle
                faz = (self.animasyon_adim + i * 10) % 60
                
                # Sinüs dalgası ile smooth büyüme
                olcek = 1 + (np.sin(faz * 0.1) * 0.5 + 0.5) * (i + 1) * 10
                
                # Opacity hesapla (dışa doğru soluyor)
                opacity = int(255 * (1 - olcek / 50))
                if opacity < 0:
                    opacity = 0
                
                # Renk (kırmızıdan başlayıp soluyor)
                renk = f"#{255:02x}{opacity//3:02x}{opacity//3:02x}"
                
                # Daireyi güncelle
                x1 = 75 - olcek
                y1 = 75 - olcek
                x2 = 75 + olcek
                y2 = 75 + olcek
                
                self.canvas.coords(daire, x1, y1, x2, y2)
                self.canvas.itemconfig(daire, outline=renk, width=2)
            
            # Merkez daireyi pulse yap
            pulse = 1 + np.sin(self.animasyon_adim * 0.15) * 0.1
            x1 = 75 - 15 * pulse
            y1 = 75 - 15 * pulse
            x2 = 75 + 15 * pulse
            y2 = 75 + 15 * pulse
            self.canvas.coords(self.mikrofon_daire, x1, y1, x2, y2)
            self.canvas.itemconfig(self.mikrofon_daire, fill="#ff0000", outline="#ff4444")
            
            # Durum etiketi
            self.durum_label.config(text="🎙️ KAYIT DEVAM EDİYOR", fg="#ff0000")
            
            # 50ms sonra tekrar çağır (smooth animasyon)
            self.root.after(50, self.mikrofon_animasyon)
        else:
            # Animasyon durdu, sıfırla
            for daire in self.animasyon_daireleri:
                self.canvas.itemconfig(daire, outline="", width=0)
            self.canvas.coords(self.mikrofon_daire, 60, 60, 90, 90)
            self.canvas.itemconfig(self.mikrofon_daire, fill="#404040", outline="#00d4ff")
    
    def copilot_mesaj_gonder(self, metin):
        """Copilot Chat'e mesaj gönderir"""
        self.log(f"📤 Copilot'a gönderiliyor: {metin}")
        
        # Mesaj yazma alanına 2 kez tıkla
        pyautogui.click(*mesaj_yazma_alani)
        time.sleep(0.1)
        pyautogui.click(*mesaj_yazma_alani)
        time.sleep(0.1)
        
        # Mesajı panoya kopyala ve yapıştır
        pyperclip.copy(metin)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        
        # Gönder butonuna tıkla
        pyautogui.click(*mesaj_gonder_buton)
        self.log("✅ Mesaj gönderildi!")
    
    def ses_kaydet(self):
        """Kayıt başlat/durdur"""
        global kaydediliyor, ses_verisi
        
        if not kaydediliyor:
            # Kayıt başlat
            kaydediliyor = True
            ses_verisi = []
            self.animasyon_aktif = True
            self.mikrofon_yanik = True
            self.mikrofon_animasyon()  # Animasyonu başlat
            self.log("🎤 Kayıt başladı... (END'e tekrar basın)")
            
        else:
            # Kayıt durdur
            kaydediliyor = False
            self.animasyon_aktif = False  # Animasyonu durdur
            self.durum_label.config(text="⚙️ İşleniyor...", fg="#ffaa00")
            self.log("⏹️  Kayıt durdu, işleniyor...")
            
            # İşlemi ayrı thread'de yap (UI donmasın)
            threading.Thread(target=self.isleme_yap, daemon=True).start()
    
    def isleme_yap(self):
        """Ses işleme ve gönderme"""
        global ses_verisi
        
        if len(ses_verisi) > 0:
            # Ses verisini birleştir ve kaydet
            audio_data = np.concatenate(ses_verisi, axis=0)
            temp_file = "temp_audio.wav"
            sf.write(temp_file, audio_data, sample_rate)
            
            # Google Speech Recognition ile metne çevir
            self.log("🔄 Ses metne çevriliyor...")
            try:
                recognizer = sr.Recognizer()
                with sr.AudioFile(temp_file) as source:
                    audio = recognizer.record(source)
                
                metin = recognizer.recognize_google(audio, language="tr")
                
                # Metin alanına yaz
                self.metin_alani.delete(1.0, tk.END)
                self.metin_alani.insert(1.0, metin)
                
                self.log(f"📝 Algılanan: {metin}")
                
                # "kabul" kontrolü - CTRL + Enter tuşuna bas
                if "kabul" in metin.lower():
                    self.log("✅ 'Kabul' algılandı - CTRL+Enter basılıyor")
                    pyautogui.hotkey('ctrl', 'enter')
                    self.durum_label.config(text="✅ CTRL+Enter basıldı", fg="#00ff00")
                # "dur" kontrolü - CTRL + Backspace tuşuna bas
                elif "dur" in metin.lower():
                    self.log("⛔ 'Dur' algılandı - CTRL+Backspace basılıyor")
                    pyautogui.hotkey('ctrl', 'backspace')
                    self.durum_label.config(text="⛔ CTRL+Backspace basıldı", fg="#ff8800")
                else:
                    # Copilot'a gönder
                    self.copilot_mesaj_gonder(metin)
                    self.durum_label.config(text="✅ Tamamlandı", fg="#00ff00")
                
            except sr.UnknownValueError:
                self.log("❌ Ses anlaşılamadı")
                self.durum_label.config(text="❌ Hata", fg="#ff0000")
            except sr.RequestError as e:
                self.log(f"❌ API hatası: {e}")
                self.durum_label.config(text="❌ Hata", fg="#ff0000")
            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                # 2 saniye sonra durumu sıfırla
                self.root.after(2000, lambda: self.durum_label.config(
                    text="⚪ Beklemede", fg="#888888"
                ))
        else:
            self.log("❌ Ses kaydı bulunamadı")
            self.durum_label.config(text="⚪ Beklemede", fg="#888888")
        
        ses_verisi = []
    
    def ses_callback(self, indata, frames, time_info, status):
        """Ses kaydı callback"""
        if kaydediliyor:
            ses_verisi.append(indata.copy())
    
    def on_press(self, key):
        """Klavye tuşu kontrolü - Global olarak çalışır"""
        try:
            if key == keyboard.Key.end:
                self.ses_kaydet()
        except AttributeError:
            pass
    
    def kapat(self):
        """Programı kapat"""
        self.ses_stream.stop()
        self.ses_stream.close()
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SesliCopilotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.kapat)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.kapat()
