import logging

import httpx

log = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, shop_id: int, secret_key: str):
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.base_url = "https://api.yookassa.ru/v3/payments"

        # Передаем туда Basic-авторизацию, которую требуют платежные шлюзы
        self.client = httpx.AsyncClient(
            auth=(str(self.shop_id), self.secret_key),
            timeout=httpx.Timeout(10.0),  # Защита от вечно зависшего банка
        )

    async def create_payment_intent(
        self, order_id: int, amount: int, description: str
    ) -> str:
        log.debug("Запрос к API банка для заказа #%s на сумму %s", order_id, amount)

        # Формируем тело запроса по спецификации платежного шлюза
        payload = {
            "amount": {"value": f"{amount}.00", "currency": "RUB"},
            "capture": True,  # Деньги списываются сразу (а не замораживаются)
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://mystore.ru/orders/{order_id}/success",  # Куда вернуть юзера после оплаты
            },
            "description": description,
            "metadata": {
                "order_id": str(order_id)  # Передаем ID заказа в метаданных шлюза
            },
        }

        # ЮKassa требует уникальный ключ для защиты от повторных списаний (Idempotence-Key)
        headers = {"Idempotence-Key": f"order-{order_id}"}

        try:
            response = await self.client.post(
                self.base_url, json=payload, headers=headers
            )

            # Если банк ответил ошибкой (например, 401 или 400) — выбрасываем исключение
            response.raise_for_status()

            data = response.json()

            # Достаем из ответа банка ту самую заветную ссылку, куда нужно отправить пользователя
            payment_link = data["confirmation"]["confirmation_url"]

            log.info("Ссылка на оплату для заказа #%s успешно получена", order_id)
            return payment_link

        except httpx.HTTPStatusError as e:
            log.error("Банк вернул ошибку: %s, Тело ответа: %s", e, e.response.text)
            raise RuntimeError(f"Ошибка платежного шлюза: {e.response.status_code}")

        except httpx.RequestError as e:
            log.critical("Сетевая ошибка при попытке связаться с банком: %s", e)
            raise RuntimeError("Платежный сервис временно недоступен")

    async def close(self):
        """Не забываем закрывать HTTP-клиент при остановке приложения/воркера"""
        await self.client.aclose()
