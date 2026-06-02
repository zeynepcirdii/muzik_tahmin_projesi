import pandas as pd
import os


anket_dosya_adi = r'Hava Durumu (Yanıtlar) - Form Yanıtları 1.csv'

spotify_dosya_adi = r'ANKET.csv'

# Dosya kontrolü
if not os.path.exists(spotify_dosya_adi):
    print(f"❌ HATA: Spotify dosyası bulunamadı! İsmini doğru yazdığından emin ol: {spotify_dosya_adi}")
    exit()


try:
    df_anket = pd.read_csv(anket_dosya_adi, encoding='cp1254')
except:
    df_anket = pd.read_csv(anket_dosya_adi, encoding='latin-1')

# Spotify verisini oku (Genelde utf-8 olur)
df_spotify = pd.read_csv(spotify_dosya_adi)

print("✅ Dosyalar başarıyla okundu!")
print(f"📊 Anket Yanıtı: {len(df_anket)} satır | Spotify Verisi: {len(df_spotify)} satır")


df_final = pd.concat([df_anket.reset_index(drop=True), df_spotify.reset_index(drop=True)], axis=1)


hava_sutunu = df_anket.columns[1] 

try:
    bpm_col = [col for col in df_spotify.columns if 'bpm' in col.lower() or 'tempo' in col.lower()][0]
    valence_col = [col for col in df_spotify.columns if 'valen' in col.lower()][0]
    energy_col = [col for col in df_spotify.columns if 'energ' in col.lower()][0]
    
    df_final[bpm_col] = pd.to_numeric(df_final[bpm_col], errors='coerce')
    df_final[valence_col] = pd.to_numeric(df_final[valence_col], errors='coerce')
    df_final[energy_col] = pd.to_numeric(df_final[energy_col], errors='coerce')


    rapor = df_final.groupby(hava_sutunu)[[bpm_col, valence_col, energy_col]].mean().round(3)
    
    print("\n" + "="*60)
    print("🎯 GERÇEK SPOTIFY VERİLERİYLE ANKARA HAVA/MÜZİK ANALİZİ")
    print("="*60)
    print(rapor)
    print("="*60)
    
except IndexError:
    print("❌ HATA: Spotify dosyasının içinde BPM, Valence veya Energy sütunları bulunamadı.")
    print("Lütfen indirdiğin CSV dosyasını açıp sütun isimlerini kontrol et.")

kayit_yolu = r'sondurum.csv'

df_final.to_csv(kayit_yolu, index=False)

print(f"✅ Tüm verilerin birleştiği nihai dosya şuraya kaydedildi: {kayit_yolu}")