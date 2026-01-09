import pyautogui
import time

print("Fare pozisyon takibi başladı...")
print("Durdurmak için Ctrl+C yapın\n")

try:
    while True:
        # Farenin şu anki pozisyonunu al
        x, y = pyautogui.position()
        
        # Ekrana yazdır (aynı satırda güncelleme)
        print(f"X: {x:4d}, Y: {y:4d}", end='\r')
        
        # 1 saniye bekle
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n\nProgram durduruldu.")
