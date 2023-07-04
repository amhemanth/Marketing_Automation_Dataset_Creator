import requests
from newspaper import Article

def GetArticle(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }

    article_urls = url

    session = requests.Session()

    try:
        response = session.get(article_urls, headers=headers, timeout=10)

        if response.status_code == 200:
            article = Article(article_urls)
            article.download()
            article.parse()
            return article.text
        else:
            print(f"Failed to fetch article at {article_urls}")
    except Exception as e:
        print(f"Error occurred while fetching article at {article_urls}: {e}")