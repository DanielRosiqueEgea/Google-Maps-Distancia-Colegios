import pandas as pd
from pandas import ExcelWriter, ExcelFile
import sys

def load_all_args_1() -> list: 
    i=0
    excel_files = []
    for arg in sys.argv:
        if i==0:continue
        excel_files.append(arg)
        i+=1
    return excel_files
def load_all_args_2() -> list:
    n = len(sys.argv)
    excel_files = []

    for i in range(1,n):
        excel_files.append(sys.argv[i])

    return excel_files

def load_excel_file(excel_file:str) -> pd.DataFrame:
    df = pd.read_excel(excel_file, sheet_name=0)

    col_colegio = pd.DataFrame({'Colegio':df.iloc[:,0]})
    col_localidad = pd.DataFrame({'Localidad':df.iloc[:,1]})
    
    df = col_colegio.join(col_localidad)
    print(df.count())
    return df

df = pd.DataFrame(columns=['Colegio','Localidad'])

if len(sys.argv) <=1:
    excel_file = 'Google Maps Distancia Colegios\\Lista_Colegios.xlsx'
else:
    excel_files= load_all_args_2()
print(len(excel_files))
frames = [load_excel_file(f) for f in excel_files]
df = pd.concat(frames)

print(df.count())

