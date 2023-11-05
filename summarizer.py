import re
import feedparser
from bs4 import BeautifulSoup
from dateutil.parser import parse
import cohere
import requests
import sqlite3
import article_parser
from datetime import datetime
from flask import Flask, render_template, request, redirect
import sqlite3
import markdown2

def read_opml_file():
    with open("news-links.opml", "r", encoding='utf-8') as opml_file:
        feed_urls = [outline.get("xmlUrl") for outline in BeautifulSoup(opml_file.read(), "xml").find_all("outline") if outline.get("xmlUrl")]
    return feed_urls

def ai_summarizer(user_text):
    # Get Your own key from Cohere Website 
    cohere_api_key = "YOU_API_KEY"
    co = cohere.Client(cohere_api_key)
    main_post = "Summarize the given Information in points in Markdown format only, its an Order."
    text = main_post + " " + user_text

    if text:
        summary = co.generate(model='command', prompt=text, max_tokens=400)
        # print(summary.generations[0].text)
        return summary.generations[0].text
    else:
        print("wait")

def sqlite_data(post):
    conn = sqlite3.connect('summarizer-data.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS rss_feed
                    (date TEXT, title TEXT, full_content TEXT, summarized_content TEXT, link TEXT, author TEXT)''')

    # Check if a record with the same title and link already exists in the database
    cursor.execute("SELECT * FROM rss_feed WHERE title = ? AND link = ?",
                   (post['title'], post['link']))
    existing_record = cursor.fetchone()

    if existing_record:
        print("Duplicate data. Not saved.")
    else:
        cursor.execute("INSERT INTO rss_feed VALUES (?, ?, ?, ?, ?, ?)",
                       (post['published'], post['title'], post['full_content'], post['summarized_content'], post['link'], post['author']))
        conn.commit()
        print("Data Saved Succesfully.")
        print("------------------------------------------------------------")

    conn.close()

def sort_data_by_date(data_list):
    sorted_data = sorted(data_list, key=lambda x: x['date'], reverse=True)
    return sorted_data

def remove_blank_lines(text):
    return re.sub(r'^\s*\n', '', text, flags=re.MULTILINE)

def article_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        html = response.text
        title, content = article_parser.parse(url=url, html=html, output='markdown', timeout=5)
        return content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the article: {e}")
        return ""

def parse_rss_feed(url):
    print("Trying to fetch rss feeds.")
    feed = feedparser.parse(url)
    posts = []

    for post in feed.entries:
        post_url = post.link
        print(post_url)

        # Check if the post already exists in the database by title and link
        existing_post = check_existing_post(post.title, post_url)

        if existing_post:
            print("Post already exists. Skipping.")
            print("------------------------------------------------------------")
            posts.append(existing_post)
        else:
            full_content = article_info(post_url)
            full_content = remove_blank_lines(full_content)
            summarized_content = ai_summarizer(full_content)
            if 'published' in post:
                published_date = parse(post.published)
            else:
                # Handle the case where 'published' date is missing
                published_date = None
            
            if 'author' in post:
                author = post.author
            else:
                # Handle the case where author information is missing
                author = "Not mentioned" 

            post_data = {
                'title': post.title,
                'author': author,
                'published': published_date,
                'link': post_url,
                'full_content': full_content,
                'summarized_content': summarized_content

            }

            posts.append(post_data)
            sqlite_data(post_data)

    return posts

def check_existing_post(title, link):
    conn = sqlite3.connect('summarizer-data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS rss_feed
                    (date TEXT, title TEXT, full_content TEXT, summarized_content TEXT, link TEXT, author TEXT)''')
    cursor.execute("SELECT * FROM rss_feed WHERE title = ? AND link = ?", (title, link))
    existing_record = cursor.fetchone()
    
    conn.close()
    
    if existing_record:
        return {
            'title': existing_record[1],
            'author': existing_record[5],
            'published': existing_record[0],
            'link': existing_record[4],
            'full_content': existing_record[2]
        }
    else:
        return None

app = Flask(__name__)

# Function to fetch data from the database
def get_data(sort_order):
    data_list = []
    sorted_data_by_date = []  

    try:
        conn = sqlite3.connect('summarizer-data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rss_feed')
        data = cursor.fetchall()

        for row in data:
            full_content = markdown2.markdown(row[2], extras=["markdown-urls"])
            summarized_content = markdown2.markdown(row[3], extras=["markdown-urls"])
            date_time = datetime.fromisoformat(row[0])
            date_iso = date_time.isoformat()

            data_dict = {
                'date': date_iso,
                'title': row[1],
                'full_content': full_content,
                'summarized_content': summarized_content,
                'link': row[4],
                'author': row[5]
            }

            data_list.append(data_dict)

        if sort_order == 'desc':
            sorted_data_by_date = sorted(data_list, key=lambda x: x['date'], reverse=True)
        else:  # sort_order == 'asc':
            sorted_data_by_date = sorted(data_list, key=lambda x: x['date'], reverse=False)

        conn.close()
    except sqlite3.OperationalError as e:
        print("Database file not found. Running without it.")

    return sorted_data_by_date

def format_datetime(dateTimeString):
    date = datetime.fromisoformat(dateTimeString)  # Parse the ISO 8601 date string
    formatted_date = date.strftime("%A, %B %d, %Y %I:%M %p")
    return formatted_date

@app.route('/', methods=['GET', 'POST'])
def index():
    sort_order = 'desc'
    if request.method == 'POST':
        sort_order = request.form.get('sortorder')
    data = get_data(sort_order)
    
    return render_template('index.html', data=data, formatDateTime=format_datetime)

@app.route('/summarize', methods=['GET'])
def main():
    urls = read_opml_file()
    for url in urls:
        print("Processing URL:", url)
        parse_rss_feed(url)

    return redirect("/") 
    
if __name__ == '__main__':
    app.run(debug=True)


