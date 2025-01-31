import scrapy
import newspaper

class NewsSpider(scrapy.Spider):
    name = 'news'
    start_urls = [
        # Global Tech & Business
        "https://techcrunch.com",
        "https://www.theverge.com",
        "https://www.wired.com",
        "https://www.bloomberg.com",
        "https://www.reuters.com",
        # Startups
        "https://news.ycombinator.com",
        "https://venturebeat.com",
        # Geopolitics
        "https://www.ft.com",
        "https://www.economist.com",
        "https://www.aljazeera.com",
        # Sports
        "https://www.espn.com",
        "https://www.theathletic.com"
    ]

    def parse(self, response):
        # Extract URLs from the response and yield Scrapy Requests
        for href in response.css('a::attr(href)'):
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        # Use Newspaper4k to parse the article
        article = newspaper.article(response.url, language='en', input_html=response.text)
        article.parse()
        article.nlp()

        # Extracted information
        data = {}
        if response.url:
            data['url'] = response.url
        if article.title:
            data['title'] = article.title
        if article.authors:
            data['authors'] = article.authors
        if article.text:
            data['raw_text'] = article.text
        if article.publish_date:
            data['publish_date'] = article.publish_date.isoformat()
        if article.keywords:
            data['keywords'] = article.keywords
        if article.summary:
            data['summary'] = article.summary
        if article.top_image:
            data['top_image'] = article.top_image
        yield data
