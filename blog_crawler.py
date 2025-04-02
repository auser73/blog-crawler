from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import os

app = Flask(__name__)

def get_blog_text(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        # 본문 영역으로 추정되는 요소 우선 탐색
        content = (
            soup.find("article") or
            soup.find("div", {"id": "main-content"}) or
            soup.find("div", {"class": "entry-content"}) or
            soup.find("div", {"class": "post-body"}) or
            soup.find("div", {"class": "article"})
        )

        if content:
            paragraphs = content.find_all("p")
            text = "\n".join(p.get_text(strip=True) for p in paragraphs)
            return text[:10000] if len(text) > 0 else None  # 내용이 있으면 최대 10000자까지 반환
        else:
            return None
    except Exception as e:
        print("Error fetching text:", e)
        return None


@app.route('/crawl', methods=["POST"])
def crawl():
    data = request.json
    keyword = data.get("keyword")

    query = f"{keyword}"
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
