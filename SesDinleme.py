import sounddevice as sd
import soundfile as sf
import numpy as np
import speech_recognition as sr
import os

def record_and_play():
    """
    2 saniye boyunca mikrofona dinle ve kaydı hoparlörden çal
    """
    duration = 2  # saniye
    sample_rate = 44100  # Hz
    
    print("Dinlemeye başlanıyor... (2 saniye)")
    
    # Ses kaydı yap
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()  # Kaydı bitir
    
    print("Kaydı çalıyorum...")
    
    # Kaydı geri çal
    sd.play(recording, samplerate=sample_rate)
    sd.wait()  # Oynatmayı bitiri
    
    print("İşlem tamamlandı!")
    
    return recording

def record_and_transcribe():
    """
    Ses kaydı yaparak Google Speech Recognition ile Türkçe metne çevir
    """
    duration = 5  # saniye
    sample_rate = 16000  # 16000 Hz ideal
    
    print("Dinlemeye başlanıyor... (5 saniye)")
    
    # Ses kaydı yap
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    
    # Kaydı geçici dosyaya kaydet
    temp_file = "temp_recording.wav"
    sf.write(temp_file, recording, sample_rate)
    
    print("Metne çeviriliyor...")
    
    try:
        # Google Speech Recognition kullan
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_file) as source:
            audio = recognizer.record(source)
        
        # Türkçe dilinde tanı (language="tr")
        text = recognizer.recognize_google(audio, language="tr")
        print(f"Tanınan metin: {text}")
        
    except sr.UnknownValueError:
        text = "Ses anlaşılamadı"
        print(f"Hata: {text}")
    except sr.RequestError as e:
        text = f"API hatası: {e}"
        print(f"Hata: {text}")
    finally:
        # Geçici dosyayı sil
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    return text

if __name__ == "__main__":
    record_and_play()
