import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://username:password@localhost/databasename"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
CORS(app)

class Coin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.String(255))
    one_hour_change = db.Column(db.String(255))
    twenty_four_hour_change = db.Column(db.String(255))
    seven_day_change = db.Column(db.String(255))
    market_cap = db.Column(db.String(255))
    volume = db.Column(db.String(255))
    circulating_supply = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

@app.route("/coin_data", methods=["POST"])
def coin_data():
    coins = scrape_coin_data()

    for coin_data in coins:
        coin = Coin(
            name=coin_data["Name"],
            price=coin_data["Price"],
            one_hour_change=coin_data["1h%"],
            twenty_four_hour_change=coin_data["24h%"],
            seven_day_change=coin_data["7d%"],
            market_cap=coin_data["Market Cap"],
            volume=coin_data["Volume(24h)"],
            circulating_supply=coin_data["Circulating Supply"]
        )
        db.session.add(coin)

    db.session.commit()
    return jsonify(coins)

@app.route("/latest_data", methods=["GET"])
def latest_data():
    coins = Coin.query.order_by(Coin.created_at.desc()).limit(10).all()

    coin_data = []
    for coin in coins:
        coin_info = {
            "Name": coin.name,
            "Price": coin.price,
            "1h%": coin.one_hour_change,
            "24h%": coin.twenty_four_hour_change,
            "7d%": coin.seven_day_change,
            "Market Cap": coin.market_cap,
            "Volume(24h)": coin.volume,
            "Circulating Supply": coin.circulating_supply
        }
        coin_data.append(coin_info)

    return jsonify(coin_data)

def scrape_coin_data():
    url = "https://coinmarketcap.com/trending-cryptocurrencies/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    coins = []
    table = soup.find("table",class_="sc-80e4f26c-0 cWVTqT")
    rows = table.find_all("tr")[1:]

    for row in rows:
        data = row.find_all("td")
        name = data[1].div.a.text.strip()
        price = data[3].a.text.strip()
        one_hour_change = data[7].span.text.strip()
        twenty_four_hour_change = data[8].span.text.strip()
        seven_day_change = data[9].span.text.strip()
        market_cap = data[10].div.text.strip()
        volume = data[11].div.text.strip()
        circulating_supply = data[6].div.a.text.strip()

        coin = {
            "Name": name,
            "Price": price,
            "1h%": one_hour_change,
            "24h%": twenty_four_hour_change,
            "7d%": seven_day_change,
            "Market Cap": market_cap,
            "Volume(24h)": volume,
            "Circulating Supply": circulating_supply
        }
        coins.append(coin)

    return coins

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
