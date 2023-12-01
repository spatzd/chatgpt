import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

app = Flask(__name__)

# Slack API token
slack_token = "YOUR_SLACK_TOKEN"
client = WebClient(token=slack_token)

# User IDs for standup
standup_users = ["USER_ID_1", "USER_ID_2"]

# Standup channel ID
standup_channel = "CHANNEL_ID"

# Standup schedule (every weekday at 9:00 AM)
standup_schedule = {"day_of_week": "mon-fri", "hour": 9, "minute": 0}

def send_standup_message():
    try:
        for user_id in standup_users:
            # Get user's username
            user_info = client.users_info(user=user_id)
            username = user_info["user"]["profile"]["real_name_normalized"]

            # Send standup message
            standup_message = f"Hey {username}, it's time for your standup! How did your day go?"
            client.chat_postMessage(channel=standup_channel, text=standup_message)
    except SlackApiError as e:
        print(f"Error sending standup message: {e.response['error']}")

# Set up scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(send_standup_message, "cron", **standup_schedule)
scheduler.start()

# Listen for incoming messages
@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json

    if "event" in data and "user" in data["event"] and data["event"]["user"] in standup_users:
        user_id = data["event"]["user"]

        # Acknowledge the event
        return {"challenge": data["challenge"]}

    return {"message": "OK"}

if __name__ == "__main__":
    app.run(port=3000)
