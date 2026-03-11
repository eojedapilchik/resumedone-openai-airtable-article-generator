import requests


def notif_rocketchat(message="", channel="#web-auto", webhook_url="https://rc1.infrozix.com/hooks/6960f6f1cb3b5d80ad825f33/95Ko5EuZPxGDLjmbn6xDGcEAoTpQAAsoE7sbscGAp9zpAM8Y", username=None, emoji=None):
    """
    Send a notification to Rocket.Chat using a webhook

    **Parameters:**
    * `message`: Text message to send
    * `webhook_url`: Rocket.Chat webhook URL (default is provided)

    **Returns:**
    * Dictionary with status and response details
    """
    try:
        message_length = len(message)
        max_length = 5000
        if message_length > max_length:
            segments = [message[i:i+max_length] for i in range(0, message_length, max_length)]
            for segment in segments:
                data = {
                    "channel": channel,
                    "text": segment
                }
                if username:
                    data["alias"] = username
                if emoji:
                    data["emoji"] = emoji
                response = requests.post(webhook_url, headers={"Content-Type": "application/json"}, json=data, timeout=10)
                if response.status_code == 200:
                    continue
                else:
                    raise Exception(f"Error {response.status_code}: {response.text}")
        else:
            data = {
                "channel": channel,
                "text": message
            }
            if username:
                data["alias"] = username
            if emoji:
                data["emoji"] = emoji
            response = requests.post(webhook_url, headers={"Content-Type": "application/json"}, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
