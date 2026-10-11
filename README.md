# Bağlam Duyarlı Müzik Öneri Sistemi

Hava durumu, duygu durumu ve giyim rengine göre şarkı öneren, Flask tabanlı bir web uygulaması ve bu uygulamanın dayandığı anket analizi.

Geleneksel müzik platformları öneri yaparken genellikle geçmiş dinleme verisine bakar. Bu proje ise kullanıcının o anki bağlamını (hava, ruh hâli, giyim rengi) temel alıyor. Çalışmanın tamamı repodaki makalede anlatılıyor: *Atmosferik Koşulların Çok Boyutlu Etkisi: Bağlam Duyarlı Müzik Öneri Sistemi*.

## Nasıl çalışıyor?

1. **Veri toplama:** Google Forms ile üniversite öğrencilerinden 70 katılımcılı bir anket yapıldı. Katılımcılar hava durumu algısını, 1-10 arası içsel enerji puanını, giydikleri rengi ve o sırada dinledikleri şarkıyı bildirdi.
2. **Zenginleştirme:** Şarkıların Energy ve Valence (pozitiflik) değerleri Spotify verileriyle eşleştirildi.
3. **Ön işleme:** Pandas ile eksik veriler temizlendi, Türkçe karakter bozulmaları düzeltildi ve veriler birleştirilerek `sondurum.csv` oluşturuldu.
4. **Öneri:** Kullanıcının seçtiği hava, duygu ve giyim bilgisine göre veri filtrelenir, hedef Energy/Valence değerleri hesaplanır ve bu hedefe Öklid mesafesiyle en yakın şarkı önerilir.
5. **Özellik önemi analizi:** Hava, giyim ve duygu durumunun şarkı Energy ve Valence değerleri üzerindeki etkisi Random Forest ve permütasyon önemi ile ölçülür (`feature_importance.py`).

Öklid mesafesi:

```
Fark = sqrt((E_hedef - E_şarkı)² + (V_hedef - V_şarkı)²)
```

## Dosyalar

| Dosya | Açıklama |
| --- | --- |
| `app.py` | Flask uygulaması ve öneri algoritması |
| `templates/index.html` | Web arayüzü |
| `anketle_sarki_eslestirme.py` | Anket yanıtlarını Spotify verisiyle birleştirir, `sondurum.csv` üretir |
| `grafik.py` | Anket sonuçlarının grafikleri |
| `feature_importance.py` | Özellik önemi analizi |
| `ANKET.csv` | Şarkıların Spotify ses özellikleri |
| `Hava Durumu (Yanıtlar) - Form Yanıtları 1.csv` | Anket yanıtları |
| `sondurum.csv` | Birleştirilmiş nihai veri seti |
| `onem_Energy.*`, `onem_Valence.*` | Özellik önemi analizi çıktıları |
| `Atmosferik Koşulların ... .pdf` | Çalışmanın makalesi |

## Kurulum ve çalıştırma

Python 3.9 veya üzeri gerekir.

```bash
pip install flask pandas numpy scikit-learn matplotlib
```

Web uygulamasını başlatmak için:

```bash
python app.py
```

Tarayıcıda `http://127.0.0.1:5000` adresini aç, hava durumunu, duygu durumunu ve giyim rengini seç.

Özellik önemi analizini çalıştırmak için:

```bash
python feature_importance.py
```

## Sonuçlar

Anket verisinde (70 katılımcı) hava durumu, giyim rengi ve duygu durumunun şarkıların Energy ve Valence değerleri üzerindeki etkisi Random Forest ve XGBoost ile test edildi (5 katlı, 5 tekrarlı çapraz doğrulama, permütasyon önemi).

| Hedef | Model | R² (çapraz doğrulama) | Taban R² (sadece ortalama) |
| --- | --- | --- | --- |
| Energy | Random Forest | -0.267 | -0.058 |
| Energy | XGBoost | -0.684 | -0.058 |
| Valence | Random Forest | -0.073 | -0.050 |
| Valence | XGBoost | -0.479 | -0.050 |

Dört modelin R² değeri de yalnızca ortalamayı tahmin eden taban modelden düşük çıktı. Yani bu veriyle hava, giyim ve duygu durumu girdilerinin şarkı özelliklerini güvenilir biçimde tahmin ettiği gösterilemedi. Önem skorlarının standart sapması ortalamalarından büyük olduğu için sıralamalar (örneğin Valence için giyim rengi) kesin bulgu değil, zayıf bir eğilim olarak okunmalıdır. Daha güvenilir sonuçlar için daha büyük bir veri seti gerekir.

## Sınırlılıklar

- Veri seti 70 katılımcıdan oluşuyor; sonuçlar genel geçer bir kanıt değil, ön çalışma niteliğinde.
- Öneri algoritması bir makine öğrenmesi modeli değil, kural ve mesafe tabanlı bir yaklaşımdır.
- Anket yanıtları kişisel algıya dayanıyor (örneğin hava durumunu herkes farklı adlandırabiliyor).

## Teknolojiler

Python, Flask, Pandas, NumPy, scikit-learn, Matplotlib, HTML/CSS

## Geliştirici

Zeynep Cırdı, Ankara Üniversitesi Bilgisayar Mühendisliği
