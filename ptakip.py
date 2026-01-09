import requests
from bs4 import BeautifulSoup
import os
import sys
import time

# --- GÜVENLİK VE AYARLAR ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not TELEGRAM_TOKEN:
    print("HATA: Token bulunamadı! GitHub Secrets ayarlarını kontrol et.")
    sys.exit()

# AYARLAR
TAKIP_EDILECEK_URL = "https://www.google.com" # Buraya müşterinin sitesini yaz
DURUM_DOSYASI = "son_durum.txt"
KONTROL_ARALIGI = 30 # 30 saniyede bir kontrol
CALISMA_SURESI = 280 # 4 dakika 40 saniye açık kal

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mesaj}
    try:
        requests.post(url, data=data)
    except:
        pass

def kontrol_et_ve_bildir():
    # 1. Siteye bağlan
    try:
        response = requests.get(TAKIP_EDILECEK_URL)
        soup = BeautifulSoup(response.content, "html.parser")
        yeni_icerik = soup.get_text().strip()
    except Exception as e:
        print(f"Site hatası: {e}")
        return

    # 2. Eski durumu oku
    eski_icerik = ""
    if os.path.exists(DURUM_DOSYASI):
        with open(DURUM_DOSYASI, "r", encoding="utf-8") as f:
            eski_icerik = f.read().strip()
    
    # 3. Karşılaştır
    if yeni_icerik != eski_icerik:
        if eski_icerik == "":
            # --- RESMİ AÇILIŞ MESAJI ---
            print("Sistem başlatıldı, bildirim gönderiliyor...")
            telegram_mesaj_gonder(f"✅ Sistem Başarıyla Başlatıldı.\n\nİzlenen Adres: {TAKIP_EDILECEK_URL}\n\nWeb sitesi izleme servisi aktif durumdadır. İçerik değişikliği olması durumunda tarafınıza anlık bildirim iletilecektir.")
        else:
            # --- RESMİ DEĞİŞİKLİK MESAJI ---
            print("🚨 DEĞİŞİKLİK TESPİT EDİLDİ!")
            telegram_mesaj_gonder(f"⚠️ Bilgilendirme: Web Sitesi Güncellendi\n\nTakip edilen web sayfasında içerik değişikliği tespit edilmiştir.\n\nBağlantı: {TAKIP_EDILECEK_URL}")

        # 4. Kaydet
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f:
            f.write(yeni_icerik)
    else:
        print("Değişiklik yok.")

def main():
    baslangic_zamani = time.time()
    print(f"Sistem izleme modunda... ({CALISMA_SURESI} saniye)")
    
    while True:
        gecen_sure = time.time() - baslangic_zamani
        if gecen_sure > CALISMA_SURESI:
            print("Süre doldu, oturum yenileniyor...")
            break
            
        kontrol_et_ve_bildir()
        time.sleep(KONTROL_ARALIGI)

if __name__ == "__main__":
    main()
