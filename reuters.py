import newspaper

cnn_paper = newspaper.build('http://cnn.com', memoize_articles=False, fetch_images=True, language='en')
print(cnn_paper.category_urls())
# ['https://cnn.com', 'https://money.cnn.com', 'https://arabic.cnn.com', 'https://cnnespanol.cnn.com', 'http://edition.cnn.com', 'https://edition.cnn.com', 'https://us.cnn.com', 'https://www.cnn.com']
article_urls = [article.url for article in cnn_paper.articles]
print(article_urls[:3])
# ['https://arabic.cnn.com/middle-east/article/2023/10/30/number-of-hostages-held-in-gaza-now-up-to-239-idf-spokesperson', 'https://arabic.cnn.com/middle-east/video/2023/10/30/v146619-sotu-sullivan-hostage-negotiations', 'https://arabic.cnn.com/middle-east/article/2023/10/29/norwegian-pm-israel-gaza']

article = cnn_paper.articles[0]
article.download()
article.parse()
article.nlp()
print(article.summary)
