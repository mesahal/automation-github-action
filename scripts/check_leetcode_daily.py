import os
import smtplib
import requests
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIG ---
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
TO_EMAIL = EMAIL_USER  # send to yourself

LAST_FILE = "scripts/last_daily.txt"
LEETCODE_API_URL = "https://leetcode.com/graphql"

# --- GraphQL query for daily challenge ---
QUERY = {
    "query": """
    query questionOfToday {
      activeDailyCodingChallengeQuestion {
        date
        link
        question {
          title
          titleSlug
          difficulty
        }
      }
    }
    """
}

def get_leetcode_daily():
    try:
        res = requests.post(LEETCODE_API_URL, json=QUERY, timeout=10)
        res.raise_for_status()
        data = res.json()
        daily = data["data"]["activeDailyCodingChallengeQuestion"]
        return {
            "date": daily["date"],
            "title": daily["question"]["title"],
            "slug": daily["question"]["titleSlug"],
            "difficulty": daily["question"]["difficulty"],
            "link": "https://leetcode.com" + daily["link"],
        }
    except Exception as e:
        print("❌ Error fetching LeetCode API:", e)
        return None


def send_email(problem, today_str):
    subject = f"🧠 LeetCode Daily Challenge - {problem['title']}"
    body_html = f"""
    <html>
    <body style="font-family:Arial, sans-serif;">
        <h2>🎯 LeetCode Daily Challenge ({today_str})</h2>
        <p><b>Title:</b> {problem['title']}</p>
        <p><b>Difficulty:</b> <span style="color:{'green' if problem['difficulty']=='Easy' else 'orange' if problem['difficulty']=='Medium' else 'red'};">
            {problem['difficulty']}</span></p>
        <p>🔗 <a href="{problem['link']}">{problem['link']}</a></p>
        <br/>
        <p>Happy coding! 🚀</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("📧 Email sent successfully!")


def read_last_sent_date():
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE) as f:
            return f.read().strip()
    return ""


def save_today_date(today_str):
    os.makedirs(os.path.dirname(LAST_FILE), exist_ok=True)
    with open(LAST_FILE, "w") as f:
        f.write(today_str)


def main():
    today_bdt = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=6))).date()
    today_str = str(today_bdt)
    print("📅 Today (BDT):", today_str)

    last_sent = read_last_sent_date()
    if last_sent == today_str:
        print("🕒 Already sent today's problem. Exiting.")
        return

    problem = get_leetcode_daily()
    if not problem:
        print("⚠️ Failed to get problem data.")
        return

    print("🧩 API Problem Date:", problem["date"])

    if problem["date"] == today_str:
        print("✅ New problem detected! Sending email...")
        send_email(problem, today_str)
        save_today_date(today_str)
    else:
        print("⏳ Not updated yet on LeetCode.")


if __name__ == "__main__":
    main()
