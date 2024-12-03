from .utils import (
    geocode_location,
    get_optimal_stops,
    get_route
)
import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings


@api_view(['GET'])
def optimize_fuel(request):
    start = request.GET.get('start')
    finish = request.GET.get('finish')
    
    start_lat, start_lon = geocode_location(start)
    finish_lat, finish_lon = geocode_location(finish)

    start_cord = {
        'lat': start_lat,
        'lon': start_lon
    }
    finish_cord = {
        'lat': finish_lat,
        'lon': finish_lon
    }
    
    route, total_distance = get_route(start_cord, finish_cord)
    df = pd.read_csv(f"{settings.BASE_DIR}/fuel_prices/fuel-prices-for-be-assessment.csv")

   
    optimal_stops, total_cost = get_optimal_stops(df, route, total_distance)


    return Response({
        'optimal_stops': optimal_stops["Truckstop Name"].tolist(),
        'total_cost': total_cost
    })
