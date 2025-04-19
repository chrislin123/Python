
import requests
import StockLib

#https://discord.com/api/webhooks/1363216809817407709/EKxGlWzS9vMv_JxPnWbP8j326xymBiCiup0pOg55xhl5rGcIJAC-cIgd4DM8BucorUfn



def notify_discord_webhook(msg):
    url = 'https://discord.com/api/webhooks/1363216809817407709/EKxGlWzS9vMv_JxPnWbP8j326xymBiCiup0pOg55xhl5rGcIJAC-cIgd4DM8BucorUfn'
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "StockNotifyBot"}
    res = requests.post(url, headers = headers, json = data)
    if res.status_code in (200, 204):
        print(f"Request fulfilled with response: {res.text}")
    else:
        print(f"Request failed with response: {res.status_code}-{res.text}")


# notify_discord_webhook('test112222')



StockLib.notify_discord_webhook("特大單")