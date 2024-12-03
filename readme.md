# Fuel Route Optimizer API

## Overview
This API calculates the optimal route between a start and finish location within the USA. It identifies cost-effective fuel stops based on current fuel prices and returns an estimated total fuel cost.

## Features
- Calculate driving route using Google Directions API.
- Identify optimal fuel stops based on price.
- Estimate total fuel cost based on vehicle range and fuel efficiency.

## Requirements
- **Django 3.2.23**: Framework for building the API.
- **Google Directions**: API used for calculating routes.

## Installation
1. Clone this repository:
2. pip install -r requirements.txt
3. python manage.py runserver


## API Usage
- **Endpoint**: `/api/optimized-fuel-stops?start=NewYork&finish=Chicago`
- **Method**: GET
- **Parameters**:
- `start`: Starting location (e.g., "New York, NY").
- `finish`: Destination location (e.g., "Chicago, IL").

## Example Response
```json
{
	"optimal_stops": [
		"7-ELEVEN #40084",
		"SUNOCO",
		"SUNOCO",
		"CARLSTADT VALERO",
		"Power Gas & Truck Stop",
		"US GAS & DIESEL",
		"46 GAS AND TRUCK STOP",
		"DELTA",
		"BOLLA MARKET",
		"Fuel 4",
		"QuickChek #189",
		"THIND TRAVEL PLAZA",
		"RAYMOND TRUCK STOP",
		"SUNOCO",
		"ENRITE",
		"KWIK TRIP #872",
		"ORCHARD STOP BP",
		"7 ELEVEN #40122",
		"7-ELEVEN #39329",
		"SPRING STREET SERVICE STATION",
		"Edison Fuel Stop",
		"GASWAY",
		"DEANS LANE VALERO",
		"BP",
		"SOUTH BRUNSWICK VALERO",
		"CITGO",
		"KW RASTALL OIL",
		"BOUND BROOK BP"
	],
	"total_cost": 905.8533328
}
