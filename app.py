from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    clima = None

    if request.method == "POST":
        cidade = request.form["cidade"]

        # Geocoding
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": cidade,
            "count": 1,
            "language": "pt",
            "format": "json"
        }

        geo_data = requests.get(geo_url, params=geo_params).json()

        if "results" not in geo_data:
            clima = {"erro": "Cidade não encontrada"}
        else:
            result = geo_data["results"][0]

            lat = result["latitude"]
            lon = result["longitude"]
            estado = result.get("admin1", "")
            pais = result.get("country", "")

            clima_url = "https://api.open-meteo.com/v1/forecast"
            clima_params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True
            }

            clima_data = requests.get(clima_url, params=clima_params).json()
            cw = clima_data["current_weather"]

            weather_code = cw["weathercode"]

            if weather_code == 0:
                tipo = "sol"
            elif weather_code in [1, 2, 3]:
                tipo = "nublado"
            elif weather_code in [61, 63, 65]:
                tipo = "chuva"
            elif weather_code in [71, 73, 75]:
                tipo = "neve"
            else:
                tipo = "padrao"

            # 🔥 AQUI ESTÁ O QUE FALTAVA
            eh_noite = cw["is_day"] == 0

            clima = {
                "cidade": cidade.title(),
                "estado": estado,
                "pais": pais,
                "temperatura": cw["temperature"],
                "vento": cw["windspeed"],
                "tipo": tipo,
                "eh_noite": eh_noite
            }

    return render_template("index.html", clima=clima)

if __name__ == "__main__":
    app.run(debug=True)
