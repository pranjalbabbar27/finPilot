import numpy as np
import pandas as pd


def demo():
    rng = np.random.default_rng(7)
    rows = []
    for mo in (8, 9, 10):
        D = lambda d: pd.Timestamp(2026, mo, d)
        rows += [(D(1), "SALARY ACME TECH PVT LTD", 85000), (D(5), "UPI-RENT-LANDLORD", -25000),
                 (D(7), "HDFC EMI LOAN 4421", -6000), (D(12), "NETFLIX.COM", -499 if mo < 10 else -649),
                 (D(14), "SPOTIFY INDIA", -119), (D(9), "HOTSTAR SUBSCRIPTION", -299),
                 (D(3), "CULT FIT GYM", -1500 if mo < 10 else -1600),
                 (D(15), "BSES ELECTRICITY", -int(rng.integers(1400, 2200))), (D(18), "AIRTEL BROADBAND", -999)]
        for _ in range(6 if mo < 10 else 11):
            rows.append((D(int(rng.integers(1, 22))), f"SWIGGY*{rng.integers(100, 999)}",
                         -int(rng.integers(250, 600 if mo < 10 else 900))))
        for _ in range(3):
            rows.append((D(int(rng.integers(1, 22))), f"ZOMATO ORDER {rng.integers(100, 999)}", -int(rng.integers(250, 700))))
        for _ in range(4):
            rows.append((D(int(rng.integers(1, 22))), "BLINKIT GROCERY", -int(rng.integers(300, 1200))))
        for _ in range(5):
            rows.append((D(int(rng.integers(1, 22))), f"UBER TRIP {rng.integers(100, 999)}", -int(rng.integers(150, 450))))
        for _ in range(2):
            rows.append((D(int(rng.integers(1, 22))), "AMZN MKTP IN*2X9", -int(rng.integers(500, 3000))))
        for _ in range(2):
            rows.append((D(int(rng.integers(1, 22))), "STARBUCKS CAFE", -int(rng.integers(300, 700))))
    rows += [(pd.Timestamp(2026, 10, 16), "SWIGGY*555", -520), (pd.Timestamp(2026, 10, 16), "SWIGGY*555", -520),
             (pd.Timestamp(2026, 10, 20), "CROMA ELECTRONICS", -18000)]
    return pd.DataFrame(rows, columns=["date", "description", "amount"])
