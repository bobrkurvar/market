<template>
  <aside class="w-full md:w-64 flex-shrink-0">
    <UCard :ui="{ body: { padding: 'p-4 sm:p-5' } }">
      <template #header>
        <div class="flex justify-between items-center">
          <h3 class="font-bold text-lg">Фильтры</h3>
        </div>
      </template>

      <div class="space-y-6">

        <template v-if="config && config.length">
          <div v-for="filter in config" :key="filter.key" class="border-b border-gray-100 dark:border-gray-800 pb-4 last:border-0 last:pb-0">
            <h4 class="font-medium text-sm mb-3">{{ filter.label }}</h4>

            <div v-if="filter.type === 'checkbox'" class="space-y-2">
              <UCheckbox
                v-for="option in getOptions(filter)"
                :key="option"
                :label="option"
                :model-value="draftFilters[filter.key]?.includes(option)"
                @update:model-value="toggleCheckbox(filter.key, option)"
              />
            </div>

            <div v-else-if="filter.type === 'radio'" class="space-y-2">
              <URadio
                v-for="option in getOptions(filter)"
                :key="option"
                v-model="draftFilters[filter.key]"
                :value="option"
                :label="option"
              />
            </div>

            <div v-else-if="filter.type === 'select'">
              <USelectMenu
                v-model="draftFilters[filter.key]"
                :items="getOptions(filter)"
                placeholder="Выберите..."
                clear
              />
            </div>

            <div v-else-if="filter.type === 'range'" class="flex items-center space-x-2">
              <UInput
                v-model="draftFilters[filter.key === 'price' ? 'min_price' : `${filter.key}_min`]"
                type="number"
                placeholder="От"
                class="w-full"
              />
              <span class="text-gray-400">-</span>
              <UInput
                v-model="draftFilters[filter.key === 'price' ? 'max_price' : `${filter.key}_max`]"
                type="number"
                placeholder="До"
                class="w-full"
              />
            </div>
          </div>
        </template>
      </div>

      <div class="mt-6 flex flex-col gap-2 pt-4 border-t border-gray-100 dark:border-gray-800">
        <UButton color="primary" block @click="applyFilters">Применить</UButton>
        <UButton v-if="hasActiveFilters" color="gray" variant="soft" block @click="clearFilters">Сбросить</UButton>
      </div>
    </UCard>
  </aside>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  config: {
    type: Array,
    default: () => []
  }
})

const route = useRoute()
const router = useRouter()
const draftFilters = ref({})

const getOptions = (filter) => {
  return Array.isArray(filter?.options) ? filter.options : []
}

const syncFromUrl = () => {
  const q = route.query
  const newDraft = {}

  if (props.config) {
    props.config.forEach(f => {
      if (f.type === 'checkbox') {
        newDraft[f.key] = q[f.key] ? (typeof q[f.key] === 'string' ? q[f.key].split(',') : q[f.key]) : []
      } else if (f.type === 'range') {
        // Учитываем нашу логику для ключа 'price'
        const minKey = f.key === 'price' ? 'min_price' : `${f.key}_min`
        const maxKey = f.key === 'price' ? 'max_price' : `${f.key}_max`
        newDraft[minKey] = q[minKey] || undefined
        newDraft[maxKey] = q[maxKey] || undefined
      } else {
        newDraft[f.key] = q[f.key] || undefined
      }
    })
  }
  draftFilters.value = newDraft
}

watch(() => route.query, syncFromUrl, { immediate: true, deep: true })
watch(() => props.config, syncFromUrl, { deep: true })

const toggleCheckbox = (key, option) => {
  const arr = draftFilters.value[key] || []
  if (arr.includes(option)) {
    draftFilters.value[key] = arr.filter(v => v !== option)
  } else {
    draftFilters.value[key] = [...arr, option]
  }
}

const hasActiveFilters = computed(() => {
  const queryKeys = Object.keys(route.query).filter(k => k !== 'q')
  return queryKeys.length > 0
})

const applyFilters = () => {
  const newQuery = {}
  if (route.query.q) newQuery.q = route.query.q

  for (const [key, value] of Object.entries(draftFilters.value)) {
    if (value !== undefined && value !== null && value !== '') {
      if (Array.isArray(value)) {
        if (value.length > 0) newQuery[key] = value.join(',')
      } else {
        newQuery[key] = value
      }
    }
  }

  router.replace({ query: newQuery })
}

const clearFilters = () => {
  const newQuery = {}
  if (route.query.q) newQuery.q = route.query.q
  router.replace({ query: newQuery })
}
</script>
