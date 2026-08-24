import os
import time
import json
import urllib.request
import urllib.parse
import urllib.error


API_URL = "https://platform-api2.max.ru"
TOKEN = os.environ.get("MAX_BOT_TOKEN")


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

    try:
        with urllib.request.urlopen(request, timeout=100) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="ignore")
        print("HTTP ошибка:", error.code, body)
        raise

    except Exception as error:
        print("Ошибка API:", error)
        raise


def send_message(chat_id, text):
    endpoint = "/messages?" + urllib.parse.urlencode({
        "chat_id": chat_id
    })

    return api_request(
        "POST",
        endpoint,
        {
            "text": text
        }
    )


def get_updates(marker=None):
    params = {
        "limit": 100,
        "timeout": 90
    }

    if marker is not None:
        params["marker"] = marker

    endpoint = "/updates?" + urllib.parse.urlencode(params)

    return api_request("GET", endpoint)


def handle_update(update):
    update_type = update.get("update_type")

    print("Получено обновление:", update_type)

    if update_type == "bot_started":
        chat_id = update.get("chat_id")

        if chat_id:
            send_message(
                chat_id,
                "Здравствуйте! 👋\n\n"
                "Я рекламный помощник.\n\n"
                "Здесь можно узнать о товарах и "
                "получить информацию для заказа.\n\n"
                "Напишите, что вас интересует."
            )

    elif update_type == "message_created":
        message = update.get("message", {})
        body = message.get("body", {})

        text = body.get("text", "")
        text_lower = text.lower()

        chat_id = update.get("chat_id")

        if not chat_id:
            recipient = message.get("recipient", {})
            chat_id = recipient.get("chat_id")

        if not chat_id:
            print("Не найден chat_id")
            return

        if "дров" in text_lower:
            answer = (
                "🪵 ДРОВА\n\n"
                "Уточните, пожалуйста:\n"
                "• какой объём нужен;\n"
                "• ваш населённый пункт;\n"
                "• нужны колотые или в полене.\n\n"
                "После этого сможем рассчитать стоимость."
            )

        elif (
            "пиломат" in text_lower
            or "доска" in text_lower
        ):
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
                "После этого можно будет рассчитать "
                "стоимость с доставкой."
            )

        else:
            answer = (
                "Принял 👍\n\n"
                "Напишите, что вас интересует:\n"
                "🪵 Дрова\n"
                "🌲 Пиломатериалы\n"
                "⛏️ Уголь\n\n"
                "Также укажите населённый пункт "
                "и необходимый объём."
            )

        send_message(chat_id, answer)


def main():
    print("MAX рекламный бот запущен")

    if not TOKEN:
        print("ОШИБКА: переменная MAX_BOT_TOKEN не найдена")
        return

    marker = None

    while True:
        try:
            result = get_updates(marker)

            if not isinstance(result, dict):
                print("Неожиданный ответ API:", result)
                time.sleep(5)
                continue

            new_marker = result.get("marker")

            if new_marker is not None:
                marker = new_marker

            updates = result.get("updates", [])

            for update in updates:
                try:
                    handle_update(update)

                except Exception as error:
                    print(
                        "Ошибка обработки обновления:",
                        error
                    )

        except Exception as error:
            print(
                "Ошибка подключения к MAX:",
                error
            )

            time.sleep(5)


if __name__ == "__main__":
    main()
