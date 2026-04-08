import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs('data', exist_ok=True)

# retail_stores_simulated.csv
stores = pd.DataFrame({
    'store_id':   [f'ST{str(i).zfill(4)}' for i in range(1,51)],
    'market':     np.random.choice(['DE','AT','PL','CZ','SK','HU'], 50, p=[0.45,0.12,0.18,0.10,0.08,0.07]),
    'lat':        np.round(np.random.normal(51, 3, 50), 4),
    'lon':        np.round(np.random.normal(12, 4, 50), 4),
    'archetype':  np.random.choice(['Urban Hub','Suburban','Rural','Outlet'], 50),
    'city_pop':   (np.random.lognormal(10, 1.5, 50)).astype(int),
    'store_size_m2': np.random.choice([800,1200,1800,2500,3500], 50),
    'weekly_revenue_eur': np.round(np.random.lognormal(8.5, 0.8, 50), 0),
})
stores.to_csv('data/retail_stores_simulated.csv', index=False)
print('retail_stores_simulated.csv ✓')

# sales_history_simulated.csv
weeks = pd.date_range('2023-01-02','2024-12-30', freq='W')[:52]
rows = []
for store in stores['store_id'][:20]:
    for w in weeks:
        for cat in ['fashion','lingerie','home_textiles','hard_goods']:
            rows.append({
                'store_id': store,
                'week_start': w.date(),
                'category': cat,
                'units_sold': max(0, int(np.random.lognormal(3.5,0.7))),
                'revenue_eur': round(max(0, np.random.lognormal(6.2,0.8)), 2),
                'promo_flag': np.random.choice([0,1], p=[0.78,0.22]),
                'data_source': np.random.choice(['ERP_v2','ERP_v1','API'], p=[0.70,0.15,0.15]),
            })
pd.DataFrame(rows).to_csv('data/sales_history_simulated.csv', index=False)
print('sales_history_simulated.csv ✓')

# weather_signals_simulated.csv
weather_rows = []
for w in weeks:
    for mkt in ['DE','AT','PL','CZ','SK','HU']:
        woy = w.isocalendar().week
        temp = 10 + 15*np.sin(2*np.pi*(woy-10)/52) + np.random.normal(0,3)
        weather_rows.append({
            'week_start': w.date(),
            'market': mkt,
            'avg_temp_c': round(temp, 1),
            'rainfall_mm': round(max(0, np.random.normal(40,20)), 1),
            'sunshine_hrs': round(max(0, 5+4*np.sin(2*np.pi*(woy-10)/52)+np.random.normal(0,1)), 1),
        })
pd.DataFrame(weather_rows).to_csv('data/weather_signals_simulated.csv', index=False)
print('weather_signals_simulated.csv ✓')
