import os
import smtplib
import requests
from email.mime.text import MIMEText

# --- CONFIG ---
LAT = 23.7361   # Basabo, Dhaka
LON = 90.4285
API_KEY = os.environ["OPENWEATHER_API_KEY"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
TO_EMAIL = os.environ["EMAIL_USER"]  # Send to self

# --- Fetch weather data ---
url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
res = requests.get(url)
data = res.json()
print("DEBUG: API response:", res.status_code, res.text)

# --- Check next 1 hour rain probability ---
rain_expected = False
if "list" in data and len(data["list"]) > 0:
    first_forecast = data["list"][0]
    weather_desc = first_forecast["weather"][0]["description"]
    if "rain" in weather_desc.lower():
        rain_expected = True

# --- Send email if rain ---
if rain_expected:
    msg = MIMEText(f"☔ Rain expected in Basabo, Dhaka within the next hour!\nWeather: {weather_desc}")
    msg["Subject"] = "Rain Alert for Basabo 🌧️"
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        print("✅ Rain alert email sent!")
else:
    print("🌤️ No rain expected in the next hour.")
