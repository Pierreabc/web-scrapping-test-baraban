import requests
from bs4 import BeautifulSoup
import pandas as pd

# URLs de base du site web
base_url = "https://quotes.toscrape.com/page/{}/"
login_url = "https://quotes.toscrape.com/login"
tag_url = "https://quotes.toscrape.com/tag/books/page/{}/"

# Fonction pour extraire les citations d'une page
def extract_quotes_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = soup.find_all('div', class_='quote')
    
    quote_data = []
    for quote in quotes:
        text = quote.find('span', class_='text').get_text()
        tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]
        quote_data.append({'text': text, 'tags': tags})
    return quote_data

# Récupérer les 5 premières pages de citations et filtrer par les 4 premiers tags
relevant_tags = ['love', 'inspirational', 'life', 'humor']
all_quotes = []

for page in range(1, 6):
    url = base_url.format(page)
    all_quotes.extend(extract_quotes_from_page(url))

filtered_quotes = [quote for quote in all_quotes if any(tag in relevant_tags for tag in quote['tags'])]

# Écrire les résultats dans un fichier CSV
df = pd.DataFrame(filtered_quotes)
df.to_csv('results.csv', index=False, encoding='utf-8')

print("Première partie terminée. Les résultats ont été sauvegardés dans 'results.csv'.")

# Fonction pour se connecter et obtenir le cookie de session
def login_and_get_cookie():
    session = requests.Session()
    # Récupérer la page de login pour obtenir le token CSRF initial
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    initial_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    # Utiliser le token initial pour se connecter
    login_data = {
        'csrf_token': initial_token,
        'username': 'test',
        'password': 'test'
    }
    login_response = session.post(login_url, data=login_data)
    
    # Vérifier si la connexion est réussie en cherchant le bouton de déconnexion
    if "Logout" not in login_response.text:
        raise Exception("Login failed")

    # Récupérer le cookie de session après connexion réussie
    cookie = session.cookies.get_dict()
    
    return session, cookie

# Fonction pour extraire les citations d'une page avec un tag spécifique
def extract_quotes_from_tag_page(session, page_number):
    url = tag_url.format(page_number)
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = soup.find_all('div', class_='quote')
    
    quote_data = []
    for quote in quotes:
        text = quote.find('span', class_='text').get_text()
        tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]
        quote_data.append({'text': text, 'tags': tags})
    return quote_data

# Se connecter et obtenir le cookie après login
session, cookies = login_and_get_cookie()

# Inscrire le cookie dans results.csv
with open('results.csv', 'a', encoding='utf-8') as file:
    file.write(f'Cookies,{cookies}\n')

# Extraire les citations des 2 premières pages avec le tag 'books'
book_quotes = []
for page in range(1, 3):
    book_quotes.extend(extract_quotes_from_tag_page(session, page))

# Charger les citations existantes dans results.csv pour éviter les doublons
existing_quotes = pd.read_csv('results.csv')

# Convertir les nouvelles citations en DataFrame
book_quotes_df = pd.DataFrame(book_quotes)

# Concaténer les nouvelles citations avec les citations existantes et supprimer les doublons
merged_df = pd.concat([existing_quotes, book_quotes_df]).drop_duplicates(subset='text', keep='first')

# Écrire les résultats dans un fichier CSV
merged_df.to_csv('results.csv', index=False, encoding='utf-8')

print("Deuxième partie terminée. Les résultats ont été sauvegardés dans 'results.csv'.")
