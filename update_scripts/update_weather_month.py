from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
import time
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF

start_time = time.time()

json_file = 'data/data_en/weather/weather_month.json'

# Open and read the JSON file
with open(json_file, 'r') as f:
    data = json.load(f)

# List to store 'q' values
q_values = []

# Iterate through each dictionary in the list
for item in data:
    # Access the value of 'q' key and append to q_values list
    q_values.append(item['question'])

questions = str(q_values)


load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

gemini_model=genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config={"response_mime_type": "application/json"},
  system_instruction="""
You will be provided with Monthly weather forcast document for the upcoming month weather in Kenya. Your job is to write the answers for each question using the provided information only by the user.
IMPORTANT : Only use the information provided in the official monthly weather forcast document provided by the user to answer each question. DO NOT COME UP WITH YOUR OWN INFORMATION TO ANSWER THE QUESTION.

IMPORTANT : Answer in FULL proper sentences when writing the answer, specifying the week, repeating the county/town names in the answer whenever possible.
Example of how to write q/a pairs:
{
    "question": "What is the rainfall forecast for North-western Kenya (Turkana and Samburu Counties) this month?",
    "answer": "For the month of November 2029, North-western Kenya (Turkana and Samburu Counties) can expect morning rains as well as afternoon and night showers and thunderstorms over few places,..."
}

Here are the questions:

"""
+questions+
"""
Use this JSON schema:
    qa = {"question": str,"answer":str}
  Return a `list[qa]`
"""
)


url = "https://meteo.go.ke/forecast/monthly-forecast"

# Fetch the HTML content
response = requests.get(url)
html_content = response.text

# Parse HTML using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Find the specific <a> tag with class "document-download"
download_link = soup.find("a", class_="document-download")

if download_link:
    # Extract the URL from the href attribute
    href = download_link.get("href")
    
    # The href attribute might be relative, so we need to prepend the base URL
    base_url = "https://meteo.go.ke"
    full_url = base_url + href
    
    # Fetch the PDF content directly from the URL
    pdf_response = requests.get(full_url)
    
    if pdf_response.status_code == 200:
        # Use PyMuPDF to extract text from the PDF
        pdf_content = pdf_response.content
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        
        # Extract text from each page
        extracted_text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            extracted_text += page.get_text()

        print(f"Text content has been written")
    else:
        print(f"Failed to retrieve PDF. HTTP Status code: {pdf_response.status_code}")
else:
    print("Download link not found on the page.")


response = gemini_model.generate_content(extracted_text)

# Load the JSON response into a Python object
json_data = json.loads(response.text)

# Write the formatted JSON to a file with proper indentation
with open(json_file, 'w') as file:
    json.dump(json_data, file, indent=2)

end_time = time.time()


print(f"Time taken to update:{end_time - start_time:0.2f}")
