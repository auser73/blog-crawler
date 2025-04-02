from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from googlesearch import search

app = Flask(__name__)

def get_blog_text(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = "\n".join(p.get_text(strip=True) for p in paragraphs)
        return content[:3000]  # 최대 3000자
    except:
        return None

@app.route('/crawl', methods=['POST'])
def crawl():
    data = request.json
    keyword = data.get("keyword")
    
    query = f"site:blog.naver.com {keyword}"
    results = list(search(query, num_results=3))
    
    for url in results:
        content = get_blog_text(url)
        if content and len(content) > 500:
            return jsonify({
                "status": "success",
                "title": keyword,
                "content": content,
                "source_url": url
            })
    
    return jsonify({"status": "fail", "message": "No valid content found."})

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
