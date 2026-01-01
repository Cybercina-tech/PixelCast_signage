<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="bg-card rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <div class="p-6 border-b border-border-color">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-primary">{{ title }}</h3>
          <button
            @click="$emit('close')"
            class="text-muted hover:text-secondary transition-colors"
          >
            <XMarkIcon class="w-6 h-6" />
          </button>
        </div>
      </div>

      <div class="p-6 space-y-4">
        <!-- Selected Items Count -->
        <div class="badge-primary border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <p class="text-sm text-primary dark:text-slate-300">
            <strong class="text-primary dark:text-slate-100">{{ (selectedItems || []).length }}</strong> item(s) selected
          </p>
        </div>

        <!-- Operation Form -->
        <slot name="form" :selectedItems="selectedItems || []">
          <div v-if="operation === 'delete'" class="badge-error border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p class="text-sm text-primary dark:text-slate-300">
              Are you sure you want to delete {{ (selectedItems || []).length }} item(s)? This action cannot be undone.
            </p>
          </div>

          <div v-else-if="operation === 'update'" class="space-y-4">
            <div>
              <label class="label-base block text-sm mb-2">Update Fields</label>
              <slot name="update-form" :selectedItems="selectedItems"></slot>
            </div>
          </div>

          <div v-else-if="operation === 'activate_template'" class="space-y-4">
            <div>
              <label class="label-base block text-sm mb-2">Select Template</label>
              <select
                v-model="templateId"
                class="select-base w-full px-3 py-2 rounded-lg"
                required
              >
                <option value="">Select a template...</option>
                <option v-for="template in templates" :key="template.id" :value="template.id">
                  {{ template.name }}
                </option>
              </select>
            </div>
            <div class="flex items-center">
              <input
                v-model="syncContent"
                type="checkbox"
                id="syncContent"
                class="checkbox-base mr-2"
              />
              <label for="syncContent" class="text-sm text-primary dark:text-slate-300">Sync content after activation</label>
            </div>
          </div>

          <div v-else-if="operation === 'send_command'" class="space-y-4">
            <div>
              <label class="label-base block text-sm mb-2">Command Type</label>
              <select
                v-model="commandType"
                class="select-base w-full px-3 py-2 rounded-lg"
                required
              >
                <option value="">Select command type...</option>
                <option value="restart">Restart</option>
                <option value="refresh">Refresh</option>
                <option value="change_template">Change Template</option>
                <option value="display_message">Display Message</option>
                <option value="sync_content">Sync Content</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <div>
              <label class="label-base block text-sm mb-2">Priority</label>
              <input
                v-model.number="commandPriority"
                type="number"
                min="0"
                max="10"
                class="input-base w-full px-3 py-2 rounded-lg"
                placeholder="0"
              />
            </div>
            <div>
              <label class="label-base block text-sm mb-2">Payload (JSON)</label>
              <textarea
                v-model="commandPayload"
                rows="4"
                class="textarea-base w-full px-3 py-2 rounded-lg font-mono text-sm"
                placeholder='{"key": "value"}'
              ></textarea>
            </div>
          </div>
        </slot>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-4">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-primary-color"></div>
          <p class="mt-2 text-sm text-muted">Processing...</p>
        </div>

        <!-- Error State -->
        <div v-if="error" class="badge-error border border-red-200 dark:border-red-800 px-4 py-3 rounded-lg text-sm">
          {{ error }}
        </div>

        <!-- Success Result -->
        <div v-if="result && !loading" class="badge-success border border-emerald-200 dark:border-emerald-800 rounded-lg p-4">
          <p class="text-sm font-medium mb-2 text-primary dark:text-slate-300">Operation Completed</p>
          <ul class="text-sm space-y-1 text-primary dark:text-slate-300">
            <li>Success: {{ result.success_count || 0 }}</li>
            <li>Failed: {{ result.failure_count || 0 }}</li>
          </ul>
          <div v-if="result.results && result.results.length > 0" class="mt-4 max-h-48 overflow-y-auto">
            <p class="text-xs font-medium mb-2 text-primary dark:text-slate-300">Details:</p>
            <ul class="text-xs space-y-1 text-primary dark:text-slate-300">
              <li v-for="(item, idx) in result.results" :key="idx">
                {{ item.item_id }}: {{ item.status }} - {{ item.message }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="p-6 border-t border-border-color flex justify-end space-x-3">
        <button
          @click="$emit('close')"
          class="btn-outline px-4 py-2 rounded-lg"
          :disabled="loading"
        >
          Cancel
        </button>
        <button
          @click="handleConfirm"
          :disabled="loading || !canConfirm"
          class="btn-primary px-4 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Confirm
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  operation: {
    type: String,
    required: true,
  },
  selectedItems: {
    type: Array,
    required: true,
  },
  templates: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
  result: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close', 'confirm'])

const templateId = ref('')
const syncContent = ref(true)
const commandType = ref('')
const commandPriority = ref(0)
const commandPayload = ref('{}')

const canConfirm = computed(() => {
  if (props.operation === 'delete') return true
  if (props.operation === 'activate_template') return !!templateId.value
  if (props.operation === 'send_command') return !!commandType.value
  return true
})

const handleConfirm = () => {
  let payload = {
    item_ids: (props.selectedItems || []).map(item => item.id),
  }

  if (props.operation === 'activate_template') {
    payload.template_id = templateId.value
    payload.sync_content = syncContent.value
  } else if (props.operation === 'send_command') {
    payload.command_type = commandType.value
    payload.priority = commandPriority.value
    try {
      payload.payload = JSON.parse(commandPayload.value || '{}')
    } catch (e) {
      // Invalid JSON, use empty object
      payload.payload = {}
    }
  }

  emit('confirm', payload)
}
</script>
