import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key from environment variables
API_KEY = os.getenv('WEATHER_API_KEY')

# Load county data from JSON file
with open(os.path.join('counties.json'), 'r') as f:
    counties_data = json.load(f)

# Create a function to fetch weather data for a given latitude and longitude
def get_weather_data(lat, lon):
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    response = requests.get(weather_url)
    response.raise_for_status()
    return response.json()

# Initialize a list to store question/answer pairs
qa_pairs = []

# Loop through each county and fetch weather data
for county in counties_data:
    county_name = county['name']
    lat = county['latitude']
    lon = county['longitude']
    
    # Fetch weather data
    weather_data = get_weather_data(lat, lon)
    
    # Extract weather details
    temp = weather_data['main']['temp']
    temp_min = weather_data['main']['temp_min']
    temp_max = weather_data['main']['temp_max']
    weather_description = weather_data['weather'][0]['description']
    dt = weather_data['dt']
    
    # Convert Unix timestamp to human-readable date
    date = datetime.utcfromtimestamp(dt).strftime('%d-%m-%Y')
    
    # Format question and answer
    question = f"What is the temperature/weather today({date}) in {county_name}?"
    answer = (
        f"The weather today ({date}) in {county_name} will see a low of {temp_min}°C and a high of {temp_max}°C, "
        f"with {weather_description}. The average temperature is {temp}°C. "
        f"Morning temperature is {temp}°C, evening temperature is {temp}°C, and night temperature is {temp}°C."
    )
    
    # Add to qa_pairs list
    qa_pairs.append({"question": question, "answer": answer})

# Define the output file path
output_file_path = os.path.join('data','data_en', 'weather', 'weather_day.json')

# Ensure the directory exists
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# Save question/answer pairs to the specified JSON file
with open(output_file_path, 'w') as f:
    json.dump(qa_pairs, f, indent=4)

print(f"Question/answer pairs saved to {output_file_path}")
