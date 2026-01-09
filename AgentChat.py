import pyautogui
import time
import pyperclip

string = "benim masaüstümde kaç adet uygulama var"

# Koordinatlar
mesaj_yazma_alani = (1099, 654)
mesaj_gonder_buton = (1333, 691)
iptal_buton = (1333, 691)

# Belirli bir piksele çift tıklama ve veri yazma
def tikla_ve_yaz(x, y, metin):
    """
    Belirtilen koordinata çift tıklayıp metin yazar
    
    Args:
        x: X koordinatı (piksel)
        y: Y koordinatı (piksel)
        metin: Yazılacak metin
    """
    # Güvenlik için 2 saniye bekle
    time.sleep(2)
    
    # Belirtilen koordinata git ve çift tıkla
    pyautogui.click(x, y, clicks=2, interval=0.25)
    
    # Biraz bekle
    time.sleep(0.5)
    
    # Metni yaz
    pyautogui.write(metin)

def mesaj_gonder(metin):
    """
    Mesaj yazma alanına tıklayıp mesajı yazar ve gönder butonuna basar
    
    Args:
        metin: Gönderilecek mesaj
    """
    # Mesaj yazma alanına 2 kez tıkla (odaklanma için)
    pyautogui.click(*mesaj_yazma_alani)
    time.sleep(0.1)
    pyautogui.click(*mesaj_yazma_alani)
    time.sleep(0.1)
    
    # Mesajı panoya kopyala ve yapıştır (Türkçe karakter desteği için)
    pyperclip.copy(metin)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)
    
    # Gönder butonuna tıkla
    pyautogui.click(*mesaj_gonder_buton)

# Kullanım örneği:
# tikla_ve_yaz(*mesaj_yazma_alani, string)
mesaj_gonder(string)

