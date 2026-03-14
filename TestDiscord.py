import requests
import StockLib
import random

# https://discord.com/api/webhooks/1363216809817407709/EKxGlWzS9vMv_JxPnWbP8j326xymBiCiup0pOg55xhl5rGcIJAC-cIgd4DM8BucorUfn


def _get_user_agent() -> str:
    """Get a random User-Agent strings from a list of some recent real browsers

    Parameters
    ----------
    None

    Returns
    -------
    str
        random User-Agent strings
    """
    user_agent_strings = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:84.0) Gecko/20100101 Firefox/84.0",
    ]

    return random.choice(user_agent_strings)


# The URL of the API endpoint you want to query
api_url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/2025-11-05"

try:
    # 1. Send the GET request
    # response = requests.get(api_url)
    response = requests.get(api_url, headers={"User-Agent": _get_user_agent()})
    # Check if the request was successful (status code 200)
    response.raise_for_status()

    # 2. Get the JSON data as a Python dictionary/list
    data = response.json()

    # 3. Work with the data
    print("Request Successful!")
    print(f"Data type: {type(data)}")
    print("--- First 3 keys/values ---")

    # Print a few key-value pairs
    if isinstance(data, dict):
        for key, value in list(data.items())[:3]:
            print(f"**{key}**: {value}")

    # If the response is a list of dictionaries (like a list of posts)
    elif isinstance(data, list) and data:
        print(data[0])

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")


# from fear_greed_index import CNNFearAndGreedIndex

# cnn_fg = CNNFearAndGreedIndex()

# plot Fear and Greed charts
# fig = plt.figure(figsize=(20, 7))
# cnn_fg.plot_all_charts(fig)
# plt.show()
# testtt = cnn_fg.get_index()


# print Fear and Greed complete report
# print(cnn_fg.get_complete_report())
# print(testtt)


def notify_discord_webhook(msg):
    url = "https://discord.com/api/webhooks/1363216809817407709/EKxGlWzS9vMv_JxPnWbP8j326xymBiCiup0pOg55xhl5rGcIJAC-cIgd4DM8BucorUfn"
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "StockNotifyBot"}
    res = requests.post(url, headers=headers, json=data)
    if res.status_code in (200, 204):
        print(f"Request fulfilled with response: {res.text}")
    else:
        print(f"Request failed with response: {res.status_code}-{res.text}")


notify_discord_webhook("test112222")


# StockLib.notify_discord_webhook("特大單")
