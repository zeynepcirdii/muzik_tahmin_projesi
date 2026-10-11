import sys

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import RepeatedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

CSV_YOLU = "sondurum.csv"
KATEGORIK = ["hava durumu", "giyim"]
SAYISAL = ["duygu durumu"]
HEDEFLER = ["Energy", "Valence"]

BOZUK = {
    "Ä±": "ı", "ÅŸ": "ş", "Åž": "Ş", "Ã¼": "ü", "Ãœ": "Ü", "Ã§": "ç",
    "Ã‡": "Ç", "Ã¶": "ö", "Ã–": "Ö", "ÄŸ": "ğ", "Äž": "Ğ", "Ä°": "İ",
}


def duzelt(metin):
    if not isinstance(metin, str):
        return metin
    for b, d in BOZUK.items():
        metin = metin.replace(b, d)
    return metin.strip()

def oku(yol):
    for enc in ("utf-8", "cp1254", "latin-1"):
        try:
            return pd.read_csv(yol, encoding=enc)
        except UnicodeDecodeError:
            continue
    sys.exit("CSV okunamadi.")

df = oku(CSV_YOLU)
df.columns = [c.strip() for c in df.columns]

gerekli = KATEGORIK + SAYISAL + HEDEFLER
eksik = [c for c in gerekli if c not in df.columns]
if eksik:
    print("Su sutunlar bulunamadi:", eksik)
    print("Dosyadaki sutunlar:", list(df.columns))
    sys.exit("Dosyanin ustundeki KATEGORIK / SAYISAL / HEDEFLER listelerini duzenle.")

for c in KATEGORIK:
    df[c] = df[c].apply(duzelt)
for c in SAYISAL + HEDEFLER:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.dropna(subset=gerekli).reset_index(drop=True)
print(f"Analize giren satir sayisi: {len(df)}\n")

X = df[KATEGORIK + SAYISAL]
cv = RepeatedKFold(n_splits=5, n_repeats=5, random_state=42)


def model_kur(regressor):
    on_isleme = ColumnTransformer(
        [("kat", OneHotEncoder(handle_unknown="ignore"), KATEGORIK)],
        remainder="passthrough",
    )
    return Pipeline([("on", on_isleme), ("model", regressor)])


for hedef in HEDEFLER:
    y = df[hedef]
    rf = model_kur(RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42))
    taban = model_kur(DummyRegressor(strategy="mean"))

    r2_model = cross_val_score(rf, X, y, cv=cv, scoring="r2")
    r2_taban = cross_val_score(taban, X, y, cv=cv, scoring="r2")

    onem = []
    for egitim, test in cv.split(X):
        rf.fit(X.iloc[egitim], y.iloc[egitim])
        p = permutation_importance(
            rf, X.iloc[test], y.iloc[test], n_repeats=20, random_state=0, scoring="r2"
        )
        onem.append(p.importances_mean)
    onem = np.array(onem)

    tablo = pd.DataFrame(
        {"ozellik": X.columns, "onem_ort": onem.mean(axis=0), "onem_std": onem.std(axis=0)}
    ).sort_values("onem_ort", ascending=False)

    print("=" * 60)
    print(f"Hedef: {hedef}")
    print(f"Model R2 (capraz dogrulama): {r2_model.mean():.3f} (+/- {r2_model.std():.3f})")
    print(f"Taban R2 (sadece ortalama):   {r2_taban.mean():.3f}")
    if r2_model.mean() <= r2_taban.mean() + 0.02:
        print("UYARI: Model, ortalamayi tahmin etmekten belirgin sekilde iyi degil.")
        print("       Onem skorlarini 'kesin sonuc' degil 'zayif egilim' olarak yorumla.")
    print(tablo.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print()

    tablo.to_csv(f"onem_{hedef}.csv", index=False)
    plt.figure(figsize=(6, 3.5))
    plt.barh(tablo["ozellik"][::-1], tablo["onem_ort"][::-1], xerr=tablo["onem_std"][::-1])
    plt.xlabel("Permutasyon onemi (R2 dusmesi)")
    plt.title(f"{hedef} icin ozellik onemi")
    plt.tight_layout()
    plt.savefig(f"onem_{hedef}.png", dpi=150)
    plt.close()

print("Cikti dosyalari: onem_Energy.csv/png, onem_Valence.csv/png")