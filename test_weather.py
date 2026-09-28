from services.weather_service import WeatherService


weather_service = WeatherService()

weather = weather_service.get_weather()

print("REAL-TIME WEATHER")
print(weather)