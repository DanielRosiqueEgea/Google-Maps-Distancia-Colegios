import requests
from Api_keys import distance_matrix_key


def get_lati_longi(api_key, address):

    url = 'https://maps.googleapis.com/maps/api/geocode/json'   

    params = {
        "address": address,
        "key": api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if data["status"] == "OK":

            location = data["results"][0]["geometry"]["location"]

            lat = location["lat"]

            lng = location["lng"]

            return lat, lng

        else:

            print(f"Error: {data['error_message']}")

            return 0, 0

    else:

        print("Failed to make the request.")

        return 0, 0


def get_dist_dur(api_key, start, end):

    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    params = {

        "origins": start,

        "destinations": end,

        "key": api_key

    }


    try:
        response = requests.get(base_url, params=params)



        if response.status_code == 200:

            data = response.json()

            if data["status"] == "OK":
                if data["rows"][0]["elements"][0]["status"] == "NOT_FOUND":
                    return None, None
                distance = data["rows"][0]["elements"][0]["distance"]["text"]

                duration = data["rows"][0]["elements"][0]["duration"]["text"]

                return distance, duration

            else:

                print("Request failed.")

                return None, None

        else:

            print("Failed to make the request.")

            return None, None

    except Exception as e:

        print(f"Error: {e}")

        return None, None
