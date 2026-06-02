import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

dosya_yolu = "sondurum.csv" 
if not os.path.exists(dosya_yolu):
    print("❌ HATA: Dosya bulunamadı!")
    exit()

try:
    df = pd.read_csv(dosya_yolu, encoding='utf-8')
except:
    df = pd.read_csv(dosya_yolu, encoding='cp1254')

df.columns = df.columns.str.strip()


hava_col = 'hava durumu'
renk_col = 'giyim'
enerji_col = 'duygu durumu'
valence_col = 'Valence'

df[enerji_col] = pd.to_numeric(df[enerji_col], errors='coerce')
df.dropna(subset=[hava_col, renk_col, enerji_col, valence_col], inplace=True)


def temizle_hava(x):
    x_lower = str(x).lower()
    
    if 'murlu' in x_lower or 'yag' in x_lower: 
        return 'Yağmurlu'
    
    elif 'kapal' in x_lower or 'gri' in x_lower: 
        return 'Kapalı'
    
    elif 'bulut' in x_lower: 
        return 'Parçalı Bulutlu'
    
    else: 
        return 'Güneşli'

def temizle_renk(x):
    x = str(x).lower()
    if 'siyah' in x or 'koyu' in x: return 'Koyu Tonlar'
    elif 'beyaz' in x or 'açık' in x or 'aÃ§Ä±k' in x: return 'Açık Tonlar'
    elif 'toprak' in x: return 'Toprak Tonları'
    elif 'soğuk' in x or 'soÄŸuk' in x: return 'Soğuk Tonlar'
    elif 'sıcak' in x or 'sÄ±cak' in x: return 'Sıcak Tonlar'
    elif 'pastel' in x: return 'Pastel Tonlar'
    elif 'canlı' in x or 'neon' in x or 'canlÄ±' in x: return 'Canlı Renkler'
    else: return x.split('(')[0].strip()

df[hava_col] = df[hava_col].apply(temizle_hava)
df[renk_col] = df[renk_col].apply(temizle_renk)


sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 3, figsize=(20, 7)) 

# GRAFİK 1: Hava Durumu -> İç Enerjiye (Duygu Durumu) Etkisi
sns.barplot(data=df, x=hava_col, y=enerji_col, ax=axes[0], palette='YlOrRd', errorbar=None)
axes[0].set_title('1. Havanın Psikolojiye Etkisi', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Ortalama İç Enerji (1-10)', fontsize=12)
axes[0].set_xlabel('Hava Durumu', fontsize=12)
axes[0].tick_params(axis='x', rotation=0) 

for p in axes[0].patches:
    axes[0].annotate(f"{p.get_height():.1f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', fontsize=11, color='black', xytext=(0, 8), textcoords='offset points')

# GRAFİK 2: Hava Durumu -> Giyim Rengine Etkisi (Yüzdelik)
renk_hava_cross = pd.crosstab(df[hava_col], df[renk_col], normalize='index') * 100
sns.heatmap(renk_hava_cross, annot=True, fmt=".1f", cmap="Blues", ax=axes[1], cbar=False, annot_kws={"size": 11})
axes[1].set_title('2. Havanın Renk Tercihine Etkisi (%)', fontsize=14, fontweight='bold')
axes[1].set_ylabel('Hava Durumu', fontsize=12)
axes[1].set_xlabel('Kıyafet Renk Paleti', fontsize=12)
axes[1].tick_params(axis='x', rotation=15) 
axes[1].tick_params(axis='y', rotation=0)

# GRAFİK 3: Hava Durumu -> Müzik Seçimine Etkisi
sns.barplot(data=df, x=hava_col, y=valence_col, ax=axes[2], palette='viridis', errorbar=None)
axes[2].set_title('3. Havanın Müzik Moduna Etkisi', fontsize=14, fontweight='bold')
axes[2].set_ylabel('Ortalama Müzikal Mutluluk (Valence)', fontsize=12)
axes[2].set_xlabel('Hava Durumu', fontsize=12)
axes[2].tick_params(axis='x', rotation=0) 

for p in axes[2].patches:
    axes[2].annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', fontsize=11, color='black', xytext=(0, 8), textcoords='offset points')

plt.tight_layout()
plt.show()