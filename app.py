import streamlit as st
import json
import random
from groq import Groq
import os
import webbrowser

# Load environment variables or set up Groq client
groq_api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

# Load news data
@st.cache_data
def load_news_data(file_path='all_merged.json'):
    with open(file_path, 'r') as f:
        return json.load(f)

# Personalize news title and summary
def personalize_content(article, user_preferences):
    try:
        response = client.chat.completions.create(
            model=st.secrets["MODEL_ID"],
            messages=[
                {"role": "system", "content": "Reframe news with political nuance. Output strict JSON."},
                {"role": "user", "content": """Rewrite this news content in JSON:
{
    "title": "",
    "summary": ""
}""" + f"""

Political Perspective: {user_preferences}
Original Title: {article['title']}
Original Summary: {article['summary']}

Focus on political alignment and concise messaging."""}
            ],
            response_format={"type": "json_object"},
            temperature=0.6,
            max_tokens=150
        )
        
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        st.error(f"Personalization error: {e}")
        return {"title": article['title'], "summary": article['summary']}

def main():
    st.set_page_config(layout="wide")
    st.title("🗳️ Political News Tinder")

    # Initialize session state
    if 'news_data' not in st.session_state:
        st.session_state.news_data = load_news_data()
    
    # Sidebar for preferences
    st.sidebar.header("🧭 Political Compass")
    user_preferences = st.sidebar.text_area(
        "Describe your political perspective", 
        key="user_interests"
    )

    # Refresh news on interests change
    if st.session_state.get('last_interests') != user_preferences:
        st.session_state.current_articles = [
            article for article in st.session_state.news_data 
            if user_preferences.lower() in article['title'].lower() or 
               (article.get('keywords') and any(user_preferences.lower() in str(k).lower() for k in article['keywords']))
        ][:3] or random.sample(st.session_state.news_data, 3)
        st.session_state.last_interests = user_preferences

    # Initialize session state for tracking
    if 'current_articles' not in st.session_state:
        st.session_state.current_articles = random.sample(st.session_state.news_data, 3)
    if 'liked_article_urls' not in st.session_state:
        st.session_state.liked_article_urls = set()

    # Refresh button
    if st.button("🔄 Refresh News"):
        st.session_state.current_articles = random.sample(st.session_state.news_data, 3)

    # Personalize and display news
    cols = st.columns(3)
    
    for i, article in enumerate(st.session_state.current_articles):
        with cols[i]:
            # Personalize title and summary
            personalized_content = personalize_content(article, user_preferences)
            
            st.image(article['image'] or 'https://via.placeholder.com/400x300.png?text=No+Image', use_container_width=True)
            st.write(f"**{personalized_content['title']}**")
            st.write(personalized_content['summary'])
            
            col1, col2 = st.columns(2)
            with col1:
                # Disable like button if article already liked
                like_disabled = article['url'] in st.session_state.liked_article_urls
                like_button = st.button(
                    "👍 Like", 
                    key=f"like_{i}", 
                    disabled=like_disabled
                )
                if like_button:
                    st.session_state.liked_article_urls.add(article['url'])
            
            with col2:
                if st.button("📖 Read", key=f"read_{i}"):
                    webbrowser.open(article['url'])

if __name__ == "__main__":
    main()