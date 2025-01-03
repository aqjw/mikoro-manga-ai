import json
from datetime import datetime

import requests
import time

# Headers for the requests
HEADERS = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6,hy;q=0.5,ay;q=0.4,uk;q=0.3',
    'cache-control': 'no-cache',
    'cookie': '_ga=GA1.1.1635637141.1704896763; dle_user_id=53958; dle_password=8d188cb12d9eca1dc2e1f4b385763d8c; _ym_uid=1705264269962276346; _ga_GQJYLPCZ04=deleted; __utma=227790669.1635637141.1704896763.1715085498.1715092150.438; sortingcomments_sort_by=date; sortingcomments_direction=desc; ajs_anonymous_id=%2293cafe75-1969-487b-8d96-24edd3dc9708%22; _ym_d=1729860331; dle_newpm=0; PHPSESSID=6f4bn293i5qv7v4sv8tij33qqp; _ga_GQJYLPCZ04=GS1.1.1733150708.1331.1.1733151949.0.0.0',
    'pragma': 'no-cache',
    'referer': 'https://animestars.org/aniserials/video/action/2717-drevnij-lekar-v-sovremennom-gorode.html',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}


def is_within_schedule():
    now = datetime.now()
    return 1 <= now.hour < 6


def user_count_timer():
    url = ('https://animestars.org/engine/ajax/controller.php?mod=user_count_timer&user_hash'
           '=b33577f9e0f179475fb4bbf8fb5c1d5378f75736')
    while True:
        if is_within_schedule():
            try:
                response = requests.get(url, headers=HEADERS)
                print(f"User Count Timer Response: {json.loads(response.text)}")
            except Exception as e:
                print(f"Error in User Count Timer Request: {e}")
            time.sleep(60)
        else:
            time.sleep(300)


def reward_card_checker():
    url = 'https://animestars.org/engine/ajax/controller.php?mod=reward_card&action=check_reward'
    take_card_url = 'https://animestars.org/engine/ajax/controller.php?mod=cards_ajax'
    while True:
        if is_within_schedule():
            try:
                response = requests.get(url, headers=HEADERS)
                print(f"Reward Card Response: {json.loads(response.text)}")
                data = response.json()
                if data.get("if_reward") == "yes":
                    owner_id = data["cards"]["owner_id"]
                    payload = {
                        'action': 'take_card',
                        'owner_id': owner_id
                    }
                    card_response = requests.post(take_card_url, headers=HEADERS, data=payload)
                    print(f"Take Card Response: {json.loads(card_response.text)}")
            except Exception as e:
                print(f"Error in Reward Card Checker Request: {e}")
            time.sleep(160)
        else:
            time.sleep(300)


if __name__ == "__main__":
    import threading

    threading.Thread(target=user_count_timer, daemon=True).start()
    threading.Thread(target=reward_card_checker, daemon=True).start()

    while True:
        time.sleep(1)
