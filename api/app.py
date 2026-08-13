from flask import Flask, render_template, request
import requests

app = Flask(__name__,
            template_folder="../templates",
            static_folder="../static")

@app.route("/", methods=["GET", "POST"])
def index():
    clima = None

    if request.method == "POST":
        cidade = request.form.get("cidade", "").strip()

        if not cidade:
            clima = {"erro": "Digite uma cidade"}
            return render_template("index.html", clima=clima)

        try:
            # Geocoding
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_params = {
                "name": cidade,
                "count": 1,
                "language": "pt",
                "format": "json"
            }

            geo_resp = requests.get(geo_url, params=geo_params, timeout=10)
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()

            resultados = geo_data.get("results")
            if not resultados:
                clima = {"erro": "Cidade não encontrada"}
                return render_template("index.html", clima=clima)

            result = resultados[0]

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

            clima_resp = requests.get(clima_url, params=clima_params, timeout=10)
            clima_resp.raise_for_status()
            clima_data = clima_resp.json()

            cw = clima_data.get("current_weather")
            if not cw:
                clima = {"erro": "Não foi possível obter o clima agora. Tente novamente."}
                return render_template("index.html", clima=clima)

            weather_code = cw.get("weathercode")

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

            eh_noite = cw.get("is_day") == 0

            clima = {
                "cidade": cidade.title(),
                "estado": estado,
                "pais": pais,
                "temperatura": cw.get("temperature"),
                "vento": cw.get("windspeed"),
                "tipo": tipo,
                "eh_noite": eh_noite,
                "dia_offset": 0
            }

        except requests.exceptions.RequestException as e:
            clima = {"erro": f"Erro ao consultar a API de clima: {e}"}
        except (KeyError, IndexError, ValueError) as e:
            clima = {"erro": f"Erro ao interpretar a resposta da API: {e}"}

    return render_template("index.html", clima=clima)