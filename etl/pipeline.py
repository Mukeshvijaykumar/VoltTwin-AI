from extract import Extract
from transform import Transform
from load import Load


extract = Extract()
transform = Transform()
loader = Load()

# Extract
weather = extract.read_weather()
grid = extract.read_grid()

# Transform
weather = transform.clean_weather(weather)
grid = transform.clean_grid(grid)

# Load
loader.save(weather, "weather_clean.csv")
loader.save(grid, "grid_clean.csv")

print("\nETL Pipeline Completed Successfully.")