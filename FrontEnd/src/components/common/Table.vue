<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            {{ column.label }}
          </th>
          <th v-if="actions" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
            Actions
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr v-for="row in data" :key="row.id || row[primaryKey]">
          <td
            v-for="column in columns"
            :key="column.key"
            class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
          >
            <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
              {{ row[column.key] }}
            </slot>
          </td>
          <td v-if="actions" class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <slot name="actions" :row="row">
              <button
                v-if="actions.includes('edit')"
                @click="$emit('edit', row)"
                class="text-indigo-600 hover:text-indigo-900 mr-3"
              >
                Edit
              </button>
              <button
                v-if="actions.includes('delete')"
                @click="$emit('delete', row)"
                class="text-red-600 hover:text-red-900"
              >
                Delete
              </button>
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="data.length === 0" class="text-center py-8 text-gray-500">
      No data available
    </div>
  </div>
</template>

<script setup>
defineProps({
  columns: {
    type: Array,
    required: true,
  },
  data: {
    type: Array,
    required: true,
  },
  actions: {
    type: Array,
    default: () => [],
  },
  primaryKey: {
    type: String,
    default: 'id',
  },
})

defineEmits(['edit', 'delete'])
</script>
