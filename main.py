from SesDinleme import record_and_play, record_and_transcribe

def main():
    print("Hello World")
    print("commit kontrol")
    print("\nSes kaydına başlanıyor...")
    # record_and_play()
    
    # Ses kaydı yaparak Türkçe metne çevir
    print("\n--- Whisper ile Türkçe Metin Tanıma ---")
    transcribed_text = record_and_transcribe()
    print(f"Sonuç: {transcribed_text}")

if __name__ == "__main__":
    main()
