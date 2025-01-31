import json
import logging
import newspaper
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_source(paper, name):
    results = []
    logger.info(f"Processing articles from {name}...")
    
    for article in tqdm(paper.articles, desc=f"Processing {name} articles"):
        try:
            article.download()
            article.parse()
            article.nlp()
            result = {
                "title": article.title,
                "image": article.top_image,
                "url": article.url,
                "summary": article.summary,
                "publishDate": article.publish_date.isoformat() if article.publish_date else None,
                "authors": article.authors,
                "raw_text": article.text,
                "keywords": article.keywords,
            }
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing article {article.url}: {str(e)}")
            continue

    with open(f"{name}_data.json", "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved {len(results)} articles from {name} to {name}_data.json")
    
    return results

if __name__ == "__main__":
    sources = {
        "cnn": "http://cnn.com",
        "slate": "http://slate.com",
        "reuters": "http://reuters.com",
        "thehindu": "http://thehindu.com",
        "economictimes": "http://economictimes.indiatimes.com",
        "ndtv": "http://ndtv.com",
        "timesofindia": "http://timesofindia.indiatimes.com",
        "news18": "http://news18.com",
        "firstpost": "http://firstpost.com",
        "indianexpress": "http://indianexpress.com",
        "scroll": "http://scroll.in",
        "thewire": "http://thewire.in",

    }
    
    # Build all papers
    papers = []
    names = []
    for name, url in sources.items():
        try:
            paper = newspaper.build(url)
            papers.append(paper)
            names.append(name)
        except Exception as e:
            logger.error(f"Error building {name}: {str(e)}")

    # Process each source
    results = {}
    for paper, name in zip(papers, names):
        try:
            results[name] = process_source(paper, name)
        except Exception as e:
            logger.error(f"Error processing {name}: {str(e)}")
            results[name] = []

    logger.info("All processing completed!")
