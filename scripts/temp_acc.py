import pandas as pd

df = pd.read_csv('C:/Users/Drubo/Documents/Project/Publication/Project_HydroSAR-Bangladesh/SAR Analysis GMM/data/Sample_Points/Final_Binary_Field_Validation_2025.csv')

def get_metrics(df_sub):
    tp = len(df_sub[(df_sub['Field_Truth'] == 1) & (df_sub['class'] == 1)])
    tn = len(df_sub[(df_sub['Field_Truth'] == 0) & (df_sub['class'] == 0)])
    fp = len(df_sub[(df_sub['Field_Truth'] == 0) & (df_sub['class'] == 1)])
    fn = len(df_sub[(df_sub['Field_Truth'] == 1) & (df_sub['class'] == 0)])
    
    total = tp + tn + fp + fn
    oa = ((tp + tn) / total) * 100 if total > 0 else 0
    pa = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
    ua = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
    
    pe_water = ((tp + fn) / total) * ((tp + fp) / total) if total > 0 else 0
    pe_land = ((tn + fp) / total) * ((tn + fn) / total) if total > 0 else 0
    pe = pe_water + pe_land
    po = oa / 100.0
    kappa = (po - pe) / (1 - pe) if pe < 1 else 0
    
    return oa, kappa, pa, ua

seasons = {
    'Jan-Mar': [1, 2, 3],
    'Apr-Jun': [4, 5, 6],
    'Jul-Sep': [7, 8, 9],
    'Oct-Dec': [10, 11, 12]
}

print('Season | OA | Kappa | PA | UA')
for s_name, months in seasons.items():
    sub = df[df['Month'].isin(months)]
    if len(sub) > 0:
        oa, kappa, pa, ua = get_metrics(sub)
        print("{} | {:.2f} | {:.4f} | {:.2f} | {:.2f}".format(s_name, oa, kappa, pa, ua))
