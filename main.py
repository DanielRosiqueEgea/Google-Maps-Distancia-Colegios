import pandas as pd
from pandas import ExcelWriter, ExcelFile
import sys
from maps import get_dist_dur
from Api_keys import distance_matrix_key
from utils import *
from tqdm import tqdm
import logging

df = pd.DataFrame(columns=['Colegio','Localidad'])

# Cargamos las rutas a los ficheros excel
if len(sys.argv) <=1:
    excel_files = ['Google Maps Distancia Colegios/Data/PlazasSinCubrir.xlsx']
else:
    excel_files= load_all_args_2()
print(len(excel_files))

frames = [load_excel_file(f) for f in excel_files]
df = pd.concat(frames)

print(df.count())



starts = ["Centro, 28013 Madrid", "C. de Alcalá, 21, Centro, 28014 Madrid"]
names = ['Origen', 'Origen 2']
basecity = "Madrid" #Modify to your area or none to get less acurate results

logger = logging.getLogger(__name__) 
file_handler = logging.FileHandler("Google Maps Distancia Colegios/logs/app.log", mode="a", encoding="utf-8")
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
# logger.basicConfig(level=logging.DEBUG)
logger.info("Iniciando testeo de distancia y tiempo")

api_key = distance_matrix_key

df= df.iloc[::-1]


progbar = tqdm(total=len(df), desc="Procesando Colegios", ncols=100,position=0,leave=False)

# Para cada fila del dataframe se comprueban las distancias y tiempo
for i, j in df.iterrows():
    progbar.update(1)
    end = f'{j["Centro"]} {j["Localidad"]} {basecity}' 
    logger.debug(f'Procesando: {end}')
   
    for idx,start in enumerate(starts):
        distance, duration = get_dist_dur(api_key, start, end)
        if distance is None or duration is None:
            # print("Error With this pair: ", start, end)
            logger.debug("Error With this pair: ", start, end)
            continue
    
        logger.debug(f'New:\n\tDistancia: {distance}\tTiempo: {duration}')

        df.at[i, f'Distancia a {names[idx]}'] = distance
        df.at[i, f'Tiempo a {names[idx]}'] = duration

df.to_excel('Google Maps Distancia Colegios/Data/PlazasSinCubrir_dist.xlsx', index=False)

progbar.close()

