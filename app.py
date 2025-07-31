from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# =====================
# OBA Market Scraper
# =====================
def scrape_oba(product_name):
    try:
        url = f"https://oba.az/products/?search={product_name}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception:
        return []

    results = []
    for item in soup.select(".product-item"):  # OBA məhsul kartları
        try:
            name_tag = item.select_one(".product-title")
            price_tag = item.select_one(".price-current")
            link_tag = item.select_one("a")

            if not name_tag or not price_tag:
                continue

            price_text = price_tag.get_text(strip=True).replace("₼", "").strip()
            price = float(price_text.replace(",", "."))
            link = "https://oba.az" + link_tag["href"] if link_tag else "#"

            results.append({
                "market": "OBA Market",
                "name": name_tag.get_text(strip=True),
                "price": price,
                "link": link
            })
        except:
            pass
    return results


# =====================
# Neptun Market Scraper
# =====================
def scrape_neptun(product_name):
    try:
        url = f"https://neptun.az/search?search={product_name}&submit_search=&route=product%2Fsearch"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception:
        return []

    results = []
    for item in soup.select(".product-layout"):  # Neptun məhsul kartları
        try:
            name_tag = item.select_one(".caption a")
            price_tag = item.select_one(".price")
            link_tag = item.select_one(".caption a")

            if not name_tag or not price_tag:
                continue

            # Qiyməti təmizləyirik
            price_text = price_tag.get_text(strip=True).replace("₼", "").strip()
            price = float(price_text.replace(",", "."))
            link = link_tag["href"] if link_tag else "#"

            results.append({
                "market": "Neptun Market",
                "name": name_tag.get_text(strip=True),
                "price": price,
                "link": link
            })
        except:
            pass
    return results


# =====================
# Web interfeys
# =====================
@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    query = ""

    if request.method == "POST":
        query = request.form.get("product")
        if query:
            results.extend(scrape_oba(query))
            results.extend(scrape_neptun(query))
            results = sorted(results, key=lambda x: x["price"])

    return render_template("index.html", results=results, query=query)


if __name__ == "__main__":
    app.run(debug=True)
