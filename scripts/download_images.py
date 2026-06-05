import os
import urllib.request
import time


CAT_DIR = "scripts/seed_categories"
PROD_DIR = "scripts/seed_products"

os.makedirs(CAT_DIR, exist_ok=True)
os.makedirs(PROD_DIR, exist_ok=True)

# Ключевые слова для реалистичности (игровой магазин)
cat_keywords = ["neon", "cyberpunk", "abstract", "software"]
prod_keywords = ["game", "xbox", "playstation", "computer", "rpg"]

print("📥 Начинаем скачивание пула изображений...")

# 1. Скачиваем картинки для категорий (горизонтальные баннеры 800x400)
print(f"Скачиваем обложки категорий в {CAT_DIR}...")
for i, kw in enumerate(cat_keywords, start=1):
    # lock=... нужен, чтобы сервис выдавал разные картинки, а не кэшировал одну
    url = f"https://loremflickr.com/800/400/{kw}?lock={i}"
    filename = os.path.join(CAT_DIR, f"category_{kw}_{i}.jpg")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f" ✅ Сохранено: {filename}")
        time.sleep(1) # Небольшая пауза, чтобы сервис не заблокировал
    except Exception as e:
        print(f" ❌ Ошибка при скачивании {url}: {e}")

# 2. Скачиваем картинки для товаров (постеры 600x800 или 800x450)
print(f"\nСкачиваем обложки товаров в {PROD_DIR}...")
for i in range(1, 16): # Скачаем 15 разных картинок
    kw = prod_keywords[i % len(prod_keywords)]
    # Используем соотношение 16:9, так как в твоем Vue-шаблоне стоит aspect-video
    url = f"https://loremflickr.com/800/450/{kw}?lock={i+100}"
    filename = os.path.join(PROD_DIR, f"product_{kw}_{i}.jpg")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f" ✅ Сохранено: {filename}")
        time.sleep(1)
    except Exception as e:
        print(f" ❌ Ошибка при скачивании {url}: {e}")

print("\n🎉 Все картинки успешно загружены! Можно запускать генератор (mass_seed).")