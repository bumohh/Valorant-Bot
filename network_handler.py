import requests
import logging

def fetchDataForUser(region,name,tag) -> requests.Response.json:
    logging.debug("starting fetchdataforuser function")
    endpoint = f"https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{name}/{tag}"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            raise ValueError(data["error"])
        
        return data
        
    except requests.exceptions.RequestException as e:
        raise ValueError("Error connecting to API: " + str(e))
    except ValueError as e:
        raise ValueError(str(e))


