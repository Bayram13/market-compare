from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_bazarstore(product_name):
    url = f"https://bazarstore.az/search?q={product_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for item in soup.select(".product-block"):
        name_tag = item.select_one(".product-title")
        price_tag = item.select_one(".price")
        link_tag = item.select_one("a")

        if name_tag and price_tag:
            try:
                price = float(price_tag.get_text(strip=True).replace("₼", "").strip())
                link = "https://bazarstore.az" + link_tag["href"] if link_tag else "#"
                results.append({
                    "market": "Bazarstore",
                    "name": name_tag.get_text(strip=True),
                    "price": price,
                    "link": link
                })
            except:
                pass
    return results

def scrape_bravo(product_name):
    url = f"https://bravo.az/search?q={product_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for item in soup.select(".product-item"):
        name_tag = item.select_one(".product-title")
        price_tag = item.select_one(".product-price")
        link_tag = item.select_one("a")

        if name_tag and price_tag:
            try:
                price = float(price_tag.get_text(strip=True).replace("₼", "").strip())
                link = "https://bravo.az" + link_tag["href"] if link_tag else "#"
                results.append({
                    "market": "Bravo",
                    "name": name_tag.get_text(strip=True),
                    "price": price,
                    "link": link
                })
            except:
                pass
    return results

@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    query = ""

    if request.method == "POST":
        query = request.form.get("product")
        if query:
            results.extend(scrape_bazarstore(query))
            results.extend(scrape_bravo(query))
            results = sorted(results, key=lambda x: x["price"])

    return render_template("index.html", results=results, query=query)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
