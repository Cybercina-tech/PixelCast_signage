<template>
  <div class="space-y-4">
    <!-- File Input -->
    <div>
      <label class="label-base block text-sm mb-2">
        {{ label || 'Select File' }}
      </label>
      <div class="upload-zone mt-1 flex justify-center px-6 pt-5 pb-6 rounded-lg">
        <div class="space-y-1 text-center">
          <svg
            class="mx-auto h-12 w-12 text-muted"
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
          <div class="flex text-sm text-secondary">
            <label
              for="file-upload"
              class="relative cursor-pointer bg-transparent rounded-md font-medium text-primary-color hover:text-emerald-700 dark:hover:text-emerald-300 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-emerald-500 dark:focus-within:ring-emerald-400"
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
          <p class="text-xs text-muted">{{ acceptHint }}</p>
        </div>
      </div>
    </div>

    <!-- Selected File -->
    <div v-if="selectedFile" class="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <DocumentIcon class="w-8 h-8 text-muted" />
          <div>
            <p class="text-sm font-medium text-primary">{{ selectedFile.name }}</p>
            <p class="text-xs text-muted">{{ formatFileSize(selectedFile.size) }}</p>
            <!-- File Metadata -->
            <div v-if="selectedFile._metadata" class="mt-1 text-xs text-muted">
              <span v-if="selectedFile._metadata.type === 'image'">
                {{ selectedFile._metadata.width }}×{{ selectedFile._metadata.height }}px
                ({{ selectedFile._metadata.aspectRatio.toFixed(2) }}:1)
              </span>
              <span v-else-if="selectedFile._metadata.type === 'video'">
                {{ selectedFile._metadata.durationFormatted }}
                <span v-if="selectedFile._metadata.width && selectedFile._metadata.height">
                  • {{ selectedFile._metadata.width }}×{{ selectedFile._metadata.height }}px
                </span>
              </span>
            </div>
          </div>
        </div>
        <button
          @click="clearFile"
          class="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors"
        >
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Validation Result -->
    <div v-if="validationResult" class="space-y-2">
      <div
        v-if="validationResult.is_valid"
        class="badge-success border border-emerald-200 dark:border-emerald-800 px-4 py-3 rounded-lg text-sm"
      >
        ✓ File is valid and ready to upload
      </div>
      <div
        v-else
        class="badge-error border border-red-200 dark:border-red-800 px-4 py-3 rounded-lg text-sm"
      >
        <p class="font-medium mb-1">Validation failed:</p>
        <ul class="list-disc list-inside space-y-1">
          <li v-for="(error, idx) in validationResult.errors" :key="idx">{{ error }}</li>
        </ul>
      </div>
      <div v-if="validationResult.warnings && validationResult.warnings.length > 0" class="badge-warning border border-amber-200 dark:border-amber-800 px-4 py-3 rounded-lg text-sm">
        <p class="font-medium mb-1">Warnings:</p>
        <ul class="list-disc list-inside space-y-1">
          <li v-for="(warning, idx) in validationResult.warnings" :key="idx">{{ warning }}</li>
        </ul>
      </div>
    </div>

    <!-- Validation Loading -->
    <div v-if="validating" class="text-center py-2">
      <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-primary-color"></div>
      <p class="mt-1 text-xs text-muted">Validating file...</p>
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
  targetZone: {
    type: Object,
    default: null,
    // Expected format: { width: number, height: number }
    // Used for aspect ratio validation
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

  // Read file metadata before validation
  await readFileMetadata(file)

  if (props.autoValidate) {
    await validateFile(file)
  }
}

/**
 * Read file metadata (dimensions for images, duration for videos)
 */
const readFileMetadata = async (file) => {
  try {
    if (props.contentType === 'image') {
      await readImageMetadata(file)
    } else if (props.contentType === 'video') {
      await readVideoMetadata(file)
    }
  } catch (error) {
    console.warn('Failed to read file metadata:', error)
  }
}

/**
 * Read image dimensions and check aspect ratio
 */
const readImageMetadata = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    const img = new Image()
    
    reader.onload = (e) => {
      img.onload = () => {
        const width = img.width
        const height = img.height
        const aspectRatio = width / height
        
        // Store metadata
        file._metadata = {
          width,
          height,
          aspectRatio,
          type: 'image'
        }
        
        // Check aspect ratio if target zone is provided
        if (props.targetZone) {
          const targetAspectRatio = props.targetZone.width / props.targetZone.height
          const ratioDifference = Math.abs(aspectRatio - targetAspectRatio) / targetAspectRatio
          
          // Warn if aspect ratio differs significantly (>20%)
          if (ratioDifference > 0.2) {
            const warning = `Image aspect ratio (${width}x${height}) differs significantly from target zone (${props.targetZone.width}x${props.targetZone.height}). This may cause distortion.`
            if (validationResult.value) {
              if (!validationResult.value.warnings) {
                validationResult.value.warnings = []
              }
              validationResult.value.warnings.push(warning)
            }
          }
        }
        
        resolve()
      }
      
      img.onerror = () => {
        reject(new Error('Failed to load image'))
      }
      
      img.src = e.target.result
    }
    
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

/**
 * Read video metadata (duration, format)
 */
const readVideoMetadata = (file) => {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video')
    const url = URL.createObjectURL(file)
    
    video.onloadedmetadata = () => {
      const duration = video.duration
      const width = video.videoWidth
      const height = video.videoHeight
      const aspectRatio = width / height
      
      // Store metadata
      file._metadata = {
        duration,
        durationFormatted: formatDuration(duration),
        width,
        height,
        aspectRatio,
        type: 'video'
      }
      
      // Check duration
      if (duration > 3600) { // 1 hour
        const warning = `Video duration (${formatDuration(duration)}) is very long. This may cause performance issues on some screens.`
        if (validationResult.value) {
          if (!validationResult.value.warnings) {
            validationResult.value.warnings = []
          }
          validationResult.value.warnings.push(warning)
        }
      }
      
      // Check resolution
      if (width > 3840 || height > 2160) {
        const warning = `Video resolution (${width}x${height}) exceeds 4K. This may not play on all screens.`
        if (validationResult.value) {
          if (!validationResult.value.warnings) {
            validationResult.value.warnings = []
          }
          validationResult.value.warnings.push(warning)
        }
      }
      
      URL.revokeObjectURL(url)
      resolve()
    }
    
    video.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('Failed to load video'))
    }
    
    video.src = url
  })
}

/**
 * Format duration in seconds to readable string
 */
const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
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
