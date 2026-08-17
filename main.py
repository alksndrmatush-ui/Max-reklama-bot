import os
import time
import json
import urllib.request
import urllib.parse

API_URL = "https://platform-api2.max.ru"
TOKEN = os.environ.get("MAX_BOT_TOKEN", "ВСТАВЬ_ТОКЕН_ПОЗЖЕ")


def api_request(method, endpoint, data=None):
    url = API_URL + endpoint

    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }

    request_data = None
    if data is not None:
        request_data = json.dumps(data).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=request_data,
        headers=headers,
        method=method
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def send_message(chat_id, text):
    data = {
        "chat_id": chat_id,
        "text": text
    }

    return api_request("POST", "/messages", data)


def get_updates(marker=None):
    params = {
        "limit": 100
    }

    if marker:
        params["marker"] = marker

    endpoint = "/updates?" + urllib.parse.urlencode(params)

    return api_request("GET", endpoint)


def handle_update(update):
    update_type = update.get("update_type")

    if update_type == "bot_started":
        chat_id = update.get("chat_id")

        if chat_id:
            send_message(
                chat_id,
                "Здравствуйте! 👋\n\n"
                "Я рекламный помощник.\n\n"
                "Здесь можно узнать о товарах и услугах, "
                "а также получить информацию для заказа.\n\n"
                "Напишите, что вас интересует."
            )

    elif update_type == "message_created":
        message = update.get("message", {})
        body = message.get("body", {})
        text = body.get("text", "")

        chat_id = update.get("chat_id")

        if not chat_id or not text:
            return

        text_lower = text.lower().strip()

        if text_lower in ("/start", "старт", "начать"):
            answer = (
                "Здравствуйте! 👋\n\n"
                "Я рекламный помощник.\n"
                "Напишите, какой товар вас интересует."
            )

        elif "дров" in text_lower:
            answer = (
                "🪵 ДРОВА\n\n"
                "Уточните, пожалуйста:\n"
                "• какой объём нужен;\n"
                "• ваш населённый пункт;\n"
                "• нужны колотые или в полене.\n\n"
                "После этого сможем рассчитать стоимость."
            )

        elif "пиломат" in text_lower or "доска" in text_lower:
            answer = (
                "🌲 ПИЛОМАТЕРИАЛЫ\n\n"
                "Напишите:\n"
                "• размер и сорт;\n"
                "• необходимый объём;\n"
                "• населённый пункт доставки.\n\n"
                "Рассчитаем предложение."
            )

        elif "уголь" in text_lower:
            answer = (
                "⛏️ УГОЛЬ\n\n"
                "Для расчёта напишите:\n"
                "• марку угля;\n"
                "• необходимый объём;\n"
                "• населённый пункт доставки.\n\n"
                "После этого можно будет рассчитать стоимость с доставкой."
            )

        else:
            answer = (
                "Принял 👍\n\n"
                "Напишите, что вас интересует:\n"
                "🪵 Дрова\n"
                "🌲 Пиломатериалы\n"
                "⛏️ Уголь\n\n"
                "Также укажите населённый пункт и необходимый объём."
            )

        send_message(chat_id, answer)


def main():
    print("MAX рекламный бот запущен")

    marker = None

    while True:
        try:
            result = get_updates(marker)

            marker = result.get("marker", marker)

            updates = result.get("updates", [])

            for update in updates:
                try:
                    handle_update(update)
                except Exception as error:
                    print("Ошибка обработки:", error)

        except Exception as error:
            print("Ошибка подключения:", error)
            time.sleep(5)


if __name__ == "__main__":
    main()
