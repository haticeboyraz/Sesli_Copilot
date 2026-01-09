from pynput import keyboard
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import numpy as np
import os

# Kayıt durumu
kaydediliyor = False
ses_verisi = []
sample_rate = 16000

def ses_kaydet():
    """F9 ile kayıt başlat/durdur ve metne çevir"""
    global kaydediliyor, ses_verisi
    
    if not kaydediliyor:
        # Kayıt başlat
        kaydediliyor = True
        ses_verisi = []
        print("\n🎤 Kayıt başladı... (END'e tekrar basarak durdurun)")
        
    else:
        # Kayıt durdur
        kaydediliyor = False
        print("⏹️  Kayıt durdu, işleniyor...")
        
        if len(ses_verisi) > 0:
            # Ses verisini birleştir ve kaydet
            audio_data = np.concatenate(ses_verisi, axis=0)
            temp_file = "temp_audio.wav"
            sf.write(temp_file, audio_data, sample_rate)
            
            # Google Speech Recognition ile metne çevir
            print("🔄 Ses metne çevriliyor...")
            try:
                recognizer = sr.Recognizer()
                with sr.AudioFile(temp_file) as source:
                    audio = recognizer.record(source)
                
                metin = recognizer.recognize_google(audio, language="tr")
                print(f"\n📝 Algılanan Metin: {metin}\n")
                
            except sr.UnknownValueError:
                print("❌ Ses anlaşılamadı")
            except sr.RequestError as e:
                print(f"❌ API hatası: {e}")
            finally:
                # Geçici dosyayı sil
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        else:
            print("❌ Ses kaydı bulunamadı")
        
        ses_verisi = []

def ses_callback(indata, frames, time_info, status):
    """Ses kaydı callback fonksiyonu"""
    if kaydediliyor:
        ses_verisi.append(indata.copy())

def on_press(key):
    """Klavye tuşuna basıldığında çalışır"""
    try:
        # END tuşu kontrolü
        if key == keyboard.Key.end:
            ses_kaydet()
    except AttributeError:
        pass

def main():
    print("=" * 50)
    print("🎙️  SESLİ METİN DÖNÜŞTÜRÜCÜ - Hazır!")
    print("=" * 50)
    print("\n📌 Kullanım:")
    print("  • END'e bas → Konuşmaya başla")
    print("  • END'e tekrar bas → Kaydı durdur ve metne çevir")
    print("  • CTRL+C → Programı kapat\n")
    print("=" * 50)
    
    # Ses akışını başlat
    with sd.InputStream(callback=ses_callback, channels=1, samplerate=sample_rate):
        # Klavye dinleyicisini başlat
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

if __name__ == "__main__":
    main()
