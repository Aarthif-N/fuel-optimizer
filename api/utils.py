import time
import pandas as pd
import requests
from fuel_optimizer.settings import GOOGLE_API_KEY
from scipy.spatial import KDTree
import numpy as np
import polyline


def filter_stops_along_route(df, route, buffer_miles=10, second=False, cheapest_stop_index=0):
    """
    Filter stops within a buffer (in miles) of the route using spatial indexing.

    Args:
    - df (DataFrame): DataFrame with 'Latitude' and 'Longitude' columns.
    - route (list): List of route coordinates [(lat, lon), ...].
    - buffer_miles (float): Maximum distance from the route to include a stop.

    Returns:
    - DataFrame: Filtered DataFrame with stops near the route.
    """
    
    if second and cheapest_stop_index is not None:
        filtered_df = df[~df["OPIS Truckstop ID"].isin(cheapest_stop_index)]
    else:
        filtered_df = df

   
    stop_coords = np.radians(filtered_df[["Latitude", "Longitude"]].values)
    tree = KDTree(stop_coords)
    route_coords = np.radians([(lat, lon) for lat, lon in route])

    
    buffer_radians = buffer_miles / 3963.0  # Earth radius in miles
    indices = set()
    for coord in route_coords:
        nearby_stops = tree.query_ball_point(coord, buffer_radians)
        for idx in nearby_stops:
            distance = np.linalg.norm(stop_coords[idx] - coord)
            if distance != 0:
                indices.add(idx)

    indices = list(indices)


    return filtered_df.iloc[indices].drop_duplicates()



def get_optimal_stops(df, route, total_distance, range_miles=500, mpg=10):
    """
    Determine the optimal fuel stops along the route and calculate total fuel cost.

    Args:
    - df (DataFrame): DataFrame with 'Latitude', 'Longitude', and 'Retail Price'.
    - route (list): List of route coordinates [(lat, lon), ...].
    - total_distance (float): Total distance of the journey in miles.
    - range_miles (float): Maximum distance the vehicle can travel on a full tank.
    - mpg (float): Vehicle's miles per gallon.

    Returns:
    - (list, float): List of optimal stops and total fuel cost.
    """
    optimal_stops = []
    total_cost = 0.0 
    remaining_distance = total_distance 
    second = False
    cheapest_stop_indexes = []

    current_location = route[0]

    while remaining_distance > 0:
        nearby_stops = filter_stops_along_route(df, [current_location], buffer_miles=10, second=second, cheapest_stop_index=cheapest_stop_indexes)

        if nearby_stops.empty:
            return pd.DataFrame(optimal_stops), total_cost

        cheapest_stop = nearby_stops.loc[nearby_stops["Retail Price"].idxmin()]
        optimal_stops.append(cheapest_stop)

       
        fuel_needed = 10
        cost = fuel_needed * cheapest_stop["Retail Price"]
        total_cost += cost

    
        remaining_distance -= fuel_needed * mpg
        current_location = (cheapest_stop["Latitude"], cheapest_stop["Longitude"])
        second= True
        cheapest_stop_index = cheapest_stop.values[0]
        cheapest_stop_indexes.append(cheapest_stop_index)

    return pd.DataFrame(optimal_stops), total_cost


def geocode_location(location):
    return get_lat_lon_from_address(location)


def get_lat_lon_from_address(address):
    """
    Get latitude and longitude for a given address using Google Maps Geocoding API.

    Args:
    - address (str): Address to geocode.
    - api_key (str): Your Google Maps API key.

    Returns:
    - tuple: (latitude, longitude) as floats if found, else (None, None).
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
    return None, None


def add_lat_lon_to_fuel_data(
    rate_limit_per_minute=60, default_lat=0.0, default_lon=0.0
):
    """
    Add latitude and longitude to the fuel data CSV, handling rate limits and default values.

    Args:
    - file_path (str): Path to the CSV file.
    - api_key (str): API key for the geocoding service.
    - rate_limit_per_minute (int): Maximum API requests allowed per minute.
    - default_lat (float): Default latitude for missing values.
    - default_lon (float): Default longitude for missing values.
    """
    df = pd.read_csv("../fuel-prices-for-be-assessment.csv")
    df["Full Address"] = df["Address"].str.strip('"') + ", " + df["City"].str.strip('"')
    latitudes = []
    longitudes = []


    for i, address in enumerate(df["Full Address"]):
        if i > 0 and i % rate_limit_per_minute == 0:
            print("Rate limit reached. Sleeping for 60 seconds...")
            time.sleep(5) 

        lat, lon = get_lat_lon_from_address(address)
        if lat is None or lon is None:
            print(f"Failed to geocode: {address}. Using default values.")
            lat, lon = (
                default_lat,
                default_lon,
            ) 
        print("lat", lat, "lon", lon, "address", address)
        latitudes.append(lat)
        longitudes.append(lon)

    df["Latitude"] = latitudes
    df["Longitude"] = longitudes

    output_path = "fuel_data_with_lat_lon.csv"
    df.to_csv(output_path, index=False)
    print(f"Updated fuel data saved to {output_path}")

    return df


def get_route(start, finish):
    """
    Fetch the route between start and finish points using Google Maps Directions API.

    Args:
    - start (dict): Starting point as {"lat": latitude, "lon": longitude}.
    - finish (dict): Ending point as {"lat": latitude, "lon": longitude}.
    - api_key (str): Google Maps API key.

    Returns:
    - list: List of coordinates [(lat, lon), ...] representing the route geometry.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{start['lat']},{start['lon']}",
        "destination": f"{finish['lat']},{finish['lon']}",
        "key": GOOGLE_API_KEY,
        "mode": "driving",
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["routes"]:
            polyline = data["routes"][0]["overview_polyline"]["points"]
            route_coords = decode_polyline(polyline)

            total_distance_meters = data["routes"][0]["legs"][0]["distance"]["value"]
            total_distance_miles = total_distance_meters * 0.000621371

            return route_coords, total_distance_miles

    else:
        print(f"Error fetching route: {response.text}")
    return []


def decode_polyline(polyline_str):
    """
    Decode a polyline string into a list of latitude and longitude pairs.

    Args:
    - polyline_str (str): Encoded polyline string.

    Returns:
    - list: Decoded polyline as a list of (latitude, longitude) tuples.
    """
    return polyline.decode(polyline_str)
