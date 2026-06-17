import logging
import re

from transliterate import translit

log = logging.getLogger(__name__)


def normalize_category_name(raw_name: str | None) -> str:
    if not raw_name:
        return raw_name

    # 1. Приводим к нижнему регистру
    name = raw_name.lower()

    # 2. Вырезаем всё, кроме латиницы, кириллицы и цифр
    name = re.sub(r"[^a-zа-я0-9]", "", name)

    if not name:
        return ""

    # 3. Транслитерация: переводим русские буквы в английские
    try:
        # reversed=True означает перевод ИЗ кириллицы В латиницу
        name = translit(name, "ru", reversed=True)
    except Exception as e:
        log.debug("Ошибка транслитерации для строки '%s': %s", name, e)

    return name
