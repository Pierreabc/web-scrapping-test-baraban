import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL de base du site web
base_url = "https://quotes.toscrape.com/page/{}/"

# Fonction pour extraire les citations d'une page
def extract_quotes_from_page(page_number):
    url = base_url.format(page_number)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = soup.find_all('div', class_='quote')
    
    quote_data = []
    for quote in quotes:
        text = quote.find('span', class_='text').get_text()
        author = quote.find('small', class_='author').get_text()
        tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]
        quote_data.append({'text': text, 'author': author, 'tags': tags})
    return quote_data

# Extraire les citations des 5 premières pages
all_quotes = []
for page in range(1, 6):
    all_quotes.extend(extract_quotes_from_page(page))

# Filtrer les citations selon les 4 premiers tags
relevant_tags = ['love', 'inspirational', 'life', 'humor']
filtered_quotes = []
for quote in all_quotes:
    if any(tag in relevant_tags for tag in quote['tags']):
        filtered_quotes.append(quote)

# Écrire les résultats dans un fichier CSV
df = pd.DataFrame(filtered_quotes)
df.to_csv('results.csv', index=False, encoding='utf-8')

print("Scraping terminé. Les résultats ont été sauvegardés dans 'results.csv'.")
