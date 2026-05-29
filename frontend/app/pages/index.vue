<template>
  <UContainer class="py-20 min-h-screen flex flex-col justify-center">

    <div class="text-center space-y-8">
      <h1 class="text-5xl font-extrabold tracking-tight sm:text-6xl">
        Твой Маркетплейс Цифровых Товаров
      </h1>

      <p class="text-lg opacity-80 max-w-2xl mx-auto">
        Лицензионные ключи Steam, подписки на сервисы, игровая валюта и аккаунты. Моментальная доставка на email сразу после оплаты.
      </p>

      <div class="flex justify-center gap-4 pt-4">
        <UButton size="xl" color="primary" to="/catalog">
          Перейти в каталог
        </UButton>
        <UButton size="xl" color="gray" variant="ghost" to="/about">
          Как мы работаем
        </UButton>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24">
      <UCard>
        <template #header>
          <h3 class="text-xl font-bold">Моментальная выдача</h3>
        </template>
        Ключ активации появляется на экране и дублируется на почту ровно через секунду после оплаты.
      </UCard>

      <UCard>
        <template #header>
          <h3 class="text-xl font-bold">Безопасная сделка</h3>
        </template>
        Деньги переводятся продавцу только после того, как ты подтвердишь валидность ключа или аккаунта.
      </UCard>

      <UCard>
        <template #header>
          <h3 class="text-xl font-bold">Сотни продавцов</h3>
        </template>
        Конкуренция рождает лучшие цены. Выбирай товары по отзывам и рейтингу продавцов.
      </UCard>
    </div>

  </UContainer>
</template>

<script setup>
useHead({
  title: 'Цифровые товары | myMarket'
})
</script>
