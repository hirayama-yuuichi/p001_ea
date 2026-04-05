# 時刻のsin/cos変換

時刻をそのまま数値（0〜23）で入れると「23時と0時が全然違う値」になってしまう問題がある。
sin/cosに変換することで「23時と0時は近い時間」とAIに正しく伝えられる。

## コード例
```python
df["hour_sin"] = np.sin(2 * np.pi * df.hour / 24)
df["hour_cos"] = np.cos(2 * np.pi * df.hour / 24)
```

## 応用
曜日にも同じ変換が使える。
```python
df["dow_sin"] = np.sin(2 * np.pi * df.dayofweek / 7)
df["dow_cos"] = np.cos(2 * np.pi * df.dayofweek / 7)
```
