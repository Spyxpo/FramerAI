import requests

BASE_URL = "http://127.0.0.1:5000"


def send_message(message):
    url = f"{BASE_URL}/message"
    headers = {"Content-Type": "application/json"}
    payload = {"message": message}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def stop_ai_process():
    url = f"{BASE_URL}/stop"
    response = requests.post(url)
    return response.json()


if __name__ == "__main__":
    while True:
        try:
            question = str(input("Enter your question: "))
            response = send_message(f"chat {question}")
            print("AI: " + response.get("response"))
        except Exception as e:
            stop_ai_process()
            print("AI: Error:", e)
            break
