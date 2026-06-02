from flask import Flask, request, render_template
import pandas as pd
import numpy as np
import math

app = Flask(__name__)

try:
    df = pd.read_csv('sondurum.csv', encoding='utf-8')
except:
    df = pd.read_csv('sondurum.csv', encoding='latin1')

def turkce_karakter_duzelt(metin):
    if not isinstance(metin, str):
        return metin
    duzeltmeler = {
        'Ä±': 'ı', 'ÅŸ': 'ş', 'Åž': 'Ş', 'Ã¼': 'ü', 'Ãœ': 'Ü',
        'Ã§': 'ç', 'Ã‡': 'Ç', 'Ã¶': 'ö', 'Ã–': 'Ö', 'ÄŸ': 'ğ',
        'Äž': 'Ğ', 'Ä°': 'İ', 'Ã¢': 'â', 'Ã®': 'î'
    }
    for bozuk, dogru in duzeltmeler.items():
        metin = metin.replace(bozuk, dogru)
    return metin

for col in ['hava durumu', 'giyim', 'Song', 'Artist']:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: turkce_karakter_duzelt(str(x)) if pd.notnull(x) else x)

giyim_secenekleri = df['giyim'].dropna().unique().tolist()

def sarki_oner(kullanici_hava, kullanici_duygu, kullanici_giyim):
    weather_mask = df['hava durumu'].astype(str).str.contains(kullanici_hava, case=False, na=False)
    filtered_df = df[weather_mask]
    
    if filtered_df.empty:
        filtered_df = df
        
    giyim_mask = filtered_df['giyim'].astype(str) == kullanici_giyim
    giyim_filtered_df = filtered_df[giyim_mask]
    
    if not giyim_filtered_df.empty:
        filtered_df = giyim_filtered_df
        
    mood_df = filtered_df[(filtered_df['duygu durumu'] >= kullanici_duygu - 1) & 
                          (filtered_df['duygu durumu'] <= kullanici_duygu + 1)]
                          
    if mood_df.empty:
        mood_df = filtered_df
        
    beklenen_valence = kullanici_duygu * 10 
    hedef_enerji = mood_df['Energy'].mean()
    hedef_valence = (mood_df['Valence'].mean() + beklenen_valence) / 2
    
    if math.isnan(hedef_enerji): hedef_enerji = df['Energy'].mean()
    if math.isnan(hedef_valence): hedef_valence = beklenen_valence
    
    df['Fark'] = np.sqrt((df['Energy'] - hedef_enerji)**2 + (df['Valence'] - hedef_valence)**2)
    
    en_iyi_sarki = df.loc[df['Fark'].idxmin()]
    
    return {
        'sarki': en_iyi_sarki['Song'],
        'sanatci': en_iyi_sarki['Artist'],
        'enerji': round(en_iyi_sarki['Energy'], 2),
        'valence': round(en_iyi_sarki['Valence'], 2),
        'hedef_enerji': round(hedef_enerji, 2),
        'hedef_valence': round(hedef_valence, 2)
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    oneri = None
    secili_hava = "Güneşli"
    secili_duygu = ""
    secili_giyim = ""
    
    if request.method == 'POST':
        secili_hava = request.form.get('hava_durumu')
        secili_duygu = request.form.get('duygu_durumu')
        secili_giyim = request.form.get('giyim_rengi')
        
        oneri = sarki_oner(secili_hava, int(secili_duygu), secili_giyim)
        
    return render_template('index.html', 
                           oneri=oneri, 
                           secili_hava=secili_hava, 
                           secili_duygu=secili_duygu, 
                           secili_giyim=secili_giyim,
                           giyim_secenekleri=giyim_secenekleri) 

if __name__ == '__main__':
    app.run(debug=True)