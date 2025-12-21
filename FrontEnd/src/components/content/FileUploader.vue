<template>
  <div class="space-y-4">
    <!-- File Input -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        {{ label || 'Select File' }}
      </label>
      <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-indigo-400 transition">
        <div class="space-y-1 text-center">
          <svg
            class="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          <div class="flex text-sm text-gray-600">
            <label
              for="file-upload"
              class="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
            >
              <span>Upload a file</span>
              <input
                id="file-upload"
                name="file-upload"
                type="file"
                class="sr-only"
                :accept="accept"
                @change="handleFileChange"
              />
            </label>
            <p class="pl-1">or drag and drop</p>
          </div>
          <p class="text-xs text-gray-500">{{ acceptHint }}</p>
        </div>
      </div>
    </div>

    <!-- Selected File -->
    <div v-if="selectedFile" class="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <DocumentIcon class="w-8 h-8 text-gray-400" />
          <div>
            <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
            <p class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
          </div>
        </div>
        <button
          @click="clearFile"
          class="text-red-600 hover:text-red-800"
        >
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Validation Result -->
    <div v-if="validationResult" class="space-y-2">
      <div
        v-if="validationResult.is_valid"
        class="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg text-sm"
      >
        ✓ File is valid and ready to upload
      </div>
      <div
        v-else
        class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm"
      >
        <p class="font-medium mb-1">Validation failed:</p>
        <ul class="list-disc list-inside space-y-1">
          <li v-for="(error, idx) in validationResult.errors" :key="idx">{{ error }}</li>
        </ul>
      </div>
      <div v-if="validationResult.warnings && validationResult.warnings.length > 0" class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg text-sm">
        <p class="font-medium mb-1">Warnings:</p>
        <ul class="list-disc list-inside space-y-1">
          <li v-for="(warning, idx) in validationResult.warnings" :key="idx">{{ warning }}</li>
        </ul>
      </div>
    </div>

    <!-- Validation Loading -->
    <div v-if="validating" class="text-center py-2">
      <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
      <p class="mt-1 text-xs text-gray-600">Validating file...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { DocumentIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useContentValidationStore } from '@/stores/contentValidation'

const props = defineProps({
  label: String,
  accept: {
    type: String,
    default: '*/*',
  },
  acceptHint: {
    type: String,
    default: 'PNG, JPG, GIF, MP4, WEBM up to 500MB',
  },
  contentType: {
    type: String,
    required: true,
  },
  autoValidate: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['file-selected', 'validation-result', 'clear'])

const validationStore = useContentValidationStore()
const selectedFile = ref(null)
const validating = ref(false)
const validationResult = ref(null)

const handleFileChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  selectedFile.value = file
  emit('file-selected', file)

  if (props.autoValidate) {
    await validateFile(file)
  }
}

const validateFile = async (file) => {
  validating.value = true
  validationResult.value = null

  try {
    const result = await validationStore.validateFile(
      file,
      props.contentType,
      file.name
    )
    validationResult.value = result
    emit('validation-result', result)
  } catch (error) {
    validationResult.value = {
      is_valid: false,
      errors: [error.message || 'Validation failed'],
      warnings: [],
    }
    emit('validation-result', validationResult.value)
  } finally {
    validating.value = false
  }
}

const clearFile = () => {
  selectedFile.value = null
  validationResult.value = null
  emit('clear')
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Expose methods for parent component
defineExpose({
  validateFile,
  clearFile,
  getFile: () => selectedFile.value,
  getValidationResult: () => validationResult.value,
})
</script>
