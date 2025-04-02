
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from googlesearch import search
import os

app = Flask(__name__)

def get_blog_text(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        content_tags = soup.select("p, div, article, section")
        content = ' '.join([tag.get_text(strip=True) for tag in content_tags])
        return content if len(content) > 300 else None
    except Exception as e:
        return None

@app.route('/crawl', methods=['POST'])
def crawl():
    data = request.get_json()
    keyword = data.get("keyword", "")
    if not keyword:
        return jsonify({"status": "fail", "message": "No keyword provided."})

    # 네이버 블로그 포함 (제외 조건 없음)
    query = f"{keyword}"

    try:
        results = list(search(query, num_results=5))
        for url in results:
            content = get_blog_text(url)
            if content:
                return jsonify({
                    "status": "success",
                    "title": keyword,
                    "content": content,
                    "source_url": url
                })
        return jsonify({"status": "fail", "message": "No valid content found."})
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
