"""
DATA SOURCES:
 1. Pest & Disease Control Measures -> KEPHIS E-Pest Portal (http://197.248.126.4:8095/epestportal/)
 2. Market Data -> KAMIS (https://amis.co.ke/site/market)
 3. Weather Data -> Kenya Meteorological Department(https://meteo.go.ke/forecast/7-days-forecast)(https://meteo.go.ke/forecast/monthly-forecast)
"""

import os
import json

def load_data(data_folder):
    questions = []
    answers = []
    
    # Walk through all files and directories within data_folder
    for root, _, files in os.walk(data_folder):
        for filename in files:
            if filename.endswith('.json'):  # Ensure it's a JSON file
                filepath = os.path.join(root, filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # Assuming each JSON file has a structure similar to your previous example
                    for item in data:
                        questions.append(item['question'])
                        answers.append(item['answer'])
    
    return questions, answers
