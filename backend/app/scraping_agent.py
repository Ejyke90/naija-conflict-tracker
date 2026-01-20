import requests
from bs4 import BeautifulSoup
import re

def scrape_news(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')  # Adjust selector based on site
    data = []
    for article in articles:
        title = article.find('h2').text if article.find('h2') else ''
        content = article.find('p').text if article.find('p') else ''
        data.append({'title': title, 'content': content})
    return data

# Example usage for Nigerian news sources
def main():
    urls = ['https://punchng.com', 'https://www.vanguardngr.com']  # Add more as needed
    for url in urls:
        scraped_data = scrape_news(url)
        # Save or process data further, e.g., pass to ETL
        print(scraped_data)

if __name__ == '__main__':
    main()
