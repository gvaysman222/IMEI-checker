from flask import Flask, request, jsonify
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

IMEI_API_URL = "https://api.imeicheck.net/v1/checks"
VALID_TOKEN = os.getenv('API_AUTH_TOKEN')


@app.route("/api/check-imei", methods=["POST"])
def check_imei():
    data = request.get_json()
    # print(data)

    if not data:
        return jsonify({"error": "Ошибка: JSON не передан или формат некорректен"}), 400

    imei = data.get("imei")
    token = data.get("token")

    if not imei or not imei.isdigit() or len(imei) not in [14, 15]:
        return jsonify({"error": "Некорректный IMEI"}), 400

    if token != VALID_TOKEN:
        return jsonify({"error": "Неверный токен"}), 403

    headers = {
        "Authorization": f"Bearer {VALID_TOKEN}",
        "Content-Type": "application/json"
    }
    body = json.dumps({"deviceId": imei, "serviceId": 12})

    # print(headers)
    # print(body)

    response = requests.post(IMEI_API_URL, headers=headers, data=body)

    # print(response.status_code, response.text)

    if response.status_code == 200:
        return response.json()
    else:
        return jsonify({"error": "Ошибка проверки IMEI", "details": response.text}), response.status_code


if __name__ == "__main__":
    app.run(debug=True)
