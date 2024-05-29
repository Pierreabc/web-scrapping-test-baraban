import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL de base du site web
base_url = "https://quotes.toscrape.com/page/{}/"
login_url = "https://quotes.toscrape.com/login"
tag_url = "https://quotes.toscrape.com/tag/books/page/{}/"

# Fonction pour se connecter et obtenir le token
def login_and_get_token():
    session = requests.Session()
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    token = soup.find('input', {'name': 'csrf_token'})['value']
    
    login_data = {
        'csrf_token': token,
        'username': 'test',
        'password': 'test'
    }
    login_response = session.post(login_url, data=login_data)
    return session, token

# Fonction pour extraire les citations d'une page
def extract_quotes_from_page(session, url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = soup.find_all('div', class_='quote')
    
    quote_data = []
    for quote in quotes:
        text = quote.find('span', class_='text').get_text()
        author = quote.find('small', class_='author').get_text()
        tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]
        quote_data.append({'text': text, 'author': author, 'tags': tags})
    return quote_data

# Se connecter et obtenir le token
session, token = login_and_get_token()

# Inscrire le token dans results.csv
with open('results.csv', 'a', encoding='utf-8') as file:
    file.write(f'Token,{token}\n')

# Extraire les citations des 2 premières pages avec le tag 'books'
book_quotes = []
for page in range(1, 3):
    url = tag_url.format(page)
    book_quotes.extend(extract_quotes_from_page(session, url))

# Charger les citations existantes dans results.csv pour éviter les doublons
existing_quotes = pd.read_csv('results.csv')

# Convertir les nouvelles citations en DataFrame
book_quotes_df = pd.DataFrame(book_quotes)

# Concaténer les nouvelles citations avec les citations existantes et supprimer les doublons
merged_df = pd.concat([existing_quotes, book_quotes_df]).drop_duplicates(subset='text', keep='first')

# Écrire les résultats dans un fichier CSV
merged_df.to_csv('results.csv', index=False, encoding='utf-8')

print("Scraping et mise à jour du fichier CSV terminés.")
