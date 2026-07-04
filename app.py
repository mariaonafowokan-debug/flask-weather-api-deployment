import json
import requests
from flask import Flask, request

app = Flask(__name__)

# API configuration details
API_KEY = os.getenv("MY_SECRET_API_KEY")
WEATHER_ENDPOINT = "http://openweathermap.org"


# --- YOUR CORE FUNCTIONS FROM CLASS ---
def get_coordinates(postcode):
    # Cleans spaces out so the API doesn't break
    clean_postcode = postcode.replace(" ", "")
    response = requests.get(f"https://postcodes.io{clean_postcode}")

    if response.status_code == 200:
        data = response.json()
        lat = data["result"]["latitude"]
        lon = data["result"]["longitude"]
        return lat, lon
    return None, None


def get_weather(lat, lon):
    # Using your trainer's params layout
    response = requests.get(
        WEATHER_ENDPOINT,
        params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"},
    )
    if response.status_code == 200:
        return response.json()
    return None


# ---  FRONTEND WEB PAGE ENDPOINT ---
@app.route("/")
def home():
    # Opens your local HTML file and reads it directly as a string to serve it
    with open("index.html", "r") as file:
        return file.read()


# --- ---
@app.route("/weather_api", methods=["GET", "POST"])
@app.route("/weather_api/<postcode_path>", methods=["GET"])
def weather_api(postcode_path=None):

    # BONUS 1: Handle POST request for multiple postcodes
    if request.method == "POST":
        # request.data captures the raw string sent to Flask
        raw_body = request.data.decode("utf-8")
        body_data = json.loads(raw_body)  # Turn raw string into Python dictionary
        postcodes_list = body_data.get("postcodes", [])

        multiple_results = {}
        for pc in postcodes_list:
            lat, lon = get_coordinates(pc)
            if lat and lon:
                weather_data = get_weather(lat, lon)
                if weather_data:
                    # Clean up the output structure cleanly for the user
                    multiple_results[pc] = {
                        "Location": weather_data["name"],
                        "Temperature": f"{weather_data['main']['temp']}°C",
                        "Conditions": weather_data["weather"][0]["description"],
                    }
                else:
                    multiple_results[pc] = {"error": "Weather fetch failed"}
            else:
                multiple_results[pc] = {"error": "Invalid postcode"}

        return json.dumps(multiple_results)

    # CORE TASK: Handle GET requests (Checks path first, drops back to query parameter)
    if postcode_path:
        postcode = postcode_path
    else:
        postcode = request.args.get("postcode")

    # If they hit the URL without passing anything at all
    if not postcode:
        return json.dumps({"error": "Please provide a postcode!"}), 400

    # Execute the two API chains
    lat, lon = get_coordinates(postcode)
    if lat is None or lon is None:
        return json.dumps({"error": "Postcode not found by postcodes.io"}), 404

    weather_data = get_weather(lat, lon)
    if not weather_data:
        return json.dumps({"error": "Could not get weather from OpenWeather"}), 500

    # Build the final dictionary with the dictionary-digging structure
    formatted_output = {
        "postcode": postcode,
        "Location": weather_data["name"],
        "Temperature": f"{weather_data['main']['temp']}°C",
        "Feels like": f"{weather_data['main']['feels_like']}°C",
        "Conditions": weather_data["weather"][0]["description"],
        "Humidity": f"{weather_data['main']['humidity']}%",
        "Icon_Code": weather_data["weather"][0]["icon"],  # OpenWeather specific icon ID
    }

    return json.dumps(formatted_output)


if __name__ == "__main__":
    app.run(debug=True)
