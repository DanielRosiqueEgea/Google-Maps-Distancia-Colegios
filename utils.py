import re
from datetime import timedelta
import pandas as pd
import sys
from maps import get_dist_dur
from Api_keys import distance_matrix_key
from tqdm import tqdm
import logging

def parse_duration(duration_str:str):
    # Define regex patterns
    """
    Parse a duration string and return a timedelta object.

    The duration string can contain numbers followed by units of time, such as 'minutes', 'mins', 'hours', 'h', etc.

    Examples of valid strings:

    - '58’'
    - '1h'
    - '31 mins'
    - '2 hours'
    - '1 hour 30 minutes'

    Returns a timedelta object representing the total duration in minutes.

    Parameters
    ----------
    duration_str : str
        The string to be parsed.

    Returns
    -------
    timedelta
        The total duration as a timedelta object.
    """
    patterns = [
        (r'(\d+)\s*’', 'minutes'),              # Example: 58’, 1’
        (r'(\d+)\s*minutos?', 'minutes'),       # Example: 10 minutos
        (r'(\d+)\s*mins?', 'minutes'),          # Example: 31 mins
        (r'(\d+)\s*h|hour|hours', 'hours'),             # Example: 1h
        # (r'(\d+)\s*hour', 'hours'),             # Example: 1 hour
       
    ]
    
    # Initialize total minutes
    total_minutes = 0
    
    for pattern, time_unit in patterns:
        matches = re.findall(pattern, duration_str, re.IGNORECASE)
        for match in matches:
            value = int(match)
            if time_unit == 'minutes':
                total_minutes += value
            elif time_unit == 'hours':
                total_minutes += value * 60
    
    # Return the total duration as a timedelta object
    return timedelta(minutes=total_minutes)

def parse_distance(distance_str:str):

    """
    Parse a distance string to its value in meters.

    Parameters
    ----------
    distance_str : str
        The string to be parsed.

    Returns
    -------
    float
        The distance in meters.

    Examples
    --------
    >>> parse_distance('300 km')
    300000.0
    >>> parse_distance('500 m')
    500.0
    """
    

    split_dist = re.match('(\d+\.*\d*)\s*([a-zA-Z]+)', distance_str)
    
    if split_dist is None:
        # si no se puede parsear, lo tomamos como  km
        return float(distance_str)*1000
    
    value = split_dist.group(1) # 300
    unit = split_dist.group(2)
    
    if unit == 'km':
        return float(value)*1000
    if unit == 'm':
        return float(value)

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

    # col_colegio = pd.DataFrame({'Colegio':df.iloc[:,0]})
    # col_localidad = pd.DataFrame({'Localidad':df.iloc[:,1]})
    
    # df = col_colegio.join(col_localidad)
    return df


def check_error(new_value, original_value, error_margin = 0.10):
    global logger
    if original_value == 0.0:
        if logger is not None:
            logger.error(f'Original value {original_value} is 0.0')
        return 1
    error = abs(new_value - original_value) / original_value 
    if logger is not None:
        logger.debug(f'Error: {error}')
    return 0 if error <= error_margin else 1




def test_everythig():
    """
    Function to test the get_dist_dur function against a list of known data.

    It loads the data from a excel file, then for each row in the dataframe
    it gets the distance and time from the start to the end using the
    get_dist_dur function. It then parses the time and distance and checks
    if the error is within a certain margin.
    
    The results are then printed to the console.
    
    This function needs an excel file with known data to test against.
    ***Just for debugging purposes***

    Parameters:
    None

    Returns:
    None
    """

    global logger 
    # console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    # logger.basicConfig(level=logging.DEBUG)
    logger.info("Iniciando testeo de distancia y tiempo")

    start = "C. de Alcalá, 21, Centro, 28014 Madrid"

    basecity = "Madrid"
    api_key = distance_matrix_key
    excel_file = 'Google Maps Distancia Colegios/Data/Lista_Colegios.xlsx'
    df = pd.read_excel(excel_file, sheet_name=0)

    error_margin = 0.20
    distance_errors = 0
    time_errors = 0

    progbar = tqdm(total=len(df), desc="Procesando Colegios", ncols=100,position=0,leave=False)

    # Para cada fila del dataframe se comprueban las distancias y tiempo
    for i, j in df.iterrows():
        progbar.update(1)
        end = f'{j["Colegio"]} {j["Localidad"]} {basecity}' 
        logger.debug(f'Procesando: {end}')
        #print(end)
        original_time = j['Tiempo']
        original_distance= j['Distancia']
        #print(f'Origial:\n\tDistancia: {original_distance}\tTiempo: {original_time}')
        logger.debug(f'Origial:\n\tDistancia: {original_distance}\tTiempo: {original_time}')

        #Se parsea el tiempo y la distancia
        parsed_original_time = parse_duration(str(original_time))
        parsed_original_distance = parse_distance(str(original_distance))
        
        #print(f'\tParsed:\tDistancia: {parsed_original_distance}\tTiempo: {parsed_original_time}')
        logger.debug(f'\tParsed:\tDistancia: {parsed_original_distance}\tTiempo: {parsed_original_time}')

        distance, duration = get_dist_dur(api_key, start, end)
        if distance is None or duration is None:
            # print("Error With this pair: ", start, end)
            logger.debug("Error With this pair: ", start, end)
            continue
        #print(f'New:\n\tDistancia: {distance}\tTiempo: {duration}')
        logger.debug(f'New:\n\tDistancia: {distance}\tTiempo: {duration}')
        
        parsed_duration = parse_duration(duration)
        parsed_distance = parse_distance(distance)

        #print(f'\tParsed:\tDistancia: {parsed_distance}\tTiempo: {parsed_duration}')
        logger.debug(f'\tParsed:\tDistancia: {parsed_distance}\tTiempo: {parsed_duration}')
        distance_errors += check_error(parsed_distance,parsed_original_distance,error_margin)
        time_errors += check_error(parsed_duration.total_seconds(), parsed_original_time.total_seconds(), error_margin)

    print(f"Distance_errors: {distance_errors}")
    print(f"time_errors: {time_errors}")
    progbar.close()

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    test_everythig()