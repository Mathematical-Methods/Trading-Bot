import requests
from bs4 import BeautifulSoup

def get_sp100_symbols():
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'parse',
        'page': 'S&P 100',
        'format': 'json',
        'prop': 'text'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check for HTTP errors
        
        data = response.json()
        if 'parse' not in data or 'text' not in data['parse']:
            raise ValueError("Unexpected JSON structure")
        
        html_content = data['parse']['text']['*']
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the "Components" header (h2 or h3)
        components_header = soup.find(lambda tag: tag.name in ['h2', 'h3'] and 'Components' in tag.text)
        if not components_header:
            raise ValueError("Components section not found")
        
        # Find the next table after the header
        table = components_header.find_next('table', {'class': 'wikitable'})
        if not table:
            raise ValueError("Components table not found")
        
        rows = table.find_all('tr')[1:]  # Skip header
        symbols = [row.find_all('td')[0].text.strip() for row in rows if row.find_all('td')]
        return symbols
    
    except (requests.RequestException, ValueError) as e:
        print(f"Error: {e}")
        return []

# Fetch and print the S&P 100 symbols
symbols = get_sp100_symbols()
if symbols:
    print(f"Retrieved {len(symbols)} S&P 100 symbols:")
    print(symbols)
else:
    print("Failed to retrieve S&P 100 symbols.")