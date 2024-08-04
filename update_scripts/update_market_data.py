import requests
from bs4 import BeautifulSoup
import time
import json

def fetch_product_data(product_number):
    url = f'https://amis.co.ke/site/market?product={product_number}&per_page=10#'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://amis.co.ke/',
    }

    session = requests.Session()
    response = session.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve data for product {product_number}")
        return None

    return response.text

def parse_product_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table_container = soup.find('div', class_='table-responsive')
    
    if not table_container:
        print("Table container not found")
        return []

    table = table_container.find('table')
    if not table:
        print("Table not found")
        return []

    tbody = table.find('tbody')
    if not tbody:
        print("Table body not found")
        return []

    rows = tbody.find_all('tr')

    product_data = []
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 9:
            continue  # Skip rows that don't have enough columns

        commodity = cols[0].text.strip()
        classification = cols[1].text.strip()
        market = cols[4].text.strip()
        wholesale_price = cols[5].text.strip().replace('/Kg', '')
        retail_price = cols[6].text.strip().replace('/Kg', '')
        supply_volume = cols[7].text.strip()
        county = cols[8].text.strip()
        date = cols[9].text.strip()

        product_data.append({
            'commodity': commodity,
            'classification': classification,
            'market': market,
            'wholesale_price': wholesale_price,
            'retail_price': retail_price,
            'supply_volume': supply_volume,
            'county': county,
            'date': date
        })
    
    return product_data

def format_product_data(product):
    # Creating formatted sentences
    classification_info = f" ({product['classification']})" if product['classification'] and product['classification'] != "-" else ""
    wholesale_info = f"The wholesale price is {product['wholesale_price']} KSh per kilogram" if product['wholesale_price'] and product['wholesale_price'] != "-" else "wholesale price is not available"
    supply_info = f"The supply volume is {product['supply_volume']} kilograms" if product['supply_volume'] and product['supply_volume'] != "-" else "Supply volume information is not available"
    
    question = f"What are the current retail and wholesale prices for {product['commodity'].lower()} in {product['market']}, and what is the supply volume available?"
    answer = (f"The retail price of {product['commodity']}{classification_info} in {product['market']} is {product['retail_price']} KSh per kilogram. "
              f"{wholesale_info}. {supply_info}. Location: {product['county']}. Date: {product['date']}.\n")
    
    return {'question': question, 'answer': answer}

def main():
    start_time = time.time()
    
    valid_tables_found = 0
    product_number = 1
    max_tables_to_find = 200  # Set the number of valid tables you want to find
    max_product_number = 272  # Set a limit to prevent infinite loop

    qna_data = []

    while valid_tables_found < max_tables_to_find and product_number <= max_product_number:
        html_content = fetch_product_data(product_number)
        
        if html_content:
            product_data = parse_product_data(html_content)
            if product_data:
                for product in product_data:
                    formatted_data = format_product_data(product)
                    qna_data.append(formatted_data)
                valid_tables_found += 1
                print(f"Valid table found for product {product_number}")
            else:
                print(f"No table data found for product {product_number}")
        else:
            print(f"Failed to retrieve data for product {product_number}")

        product_number += 1
    
    with open("data/data_en/market_data.json", 'w') as file:
        json.dump(qna_data, file, indent=4)
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time taken: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
