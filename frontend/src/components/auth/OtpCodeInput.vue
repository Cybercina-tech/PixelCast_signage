<template>
  <div class="otp-input" @paste="onPaste">
    <input
      v-for="(_, index) in digits"
      :key="index"
      :ref="(el) => setInputRef(el, index)"
      type="text"
      inputmode="numeric"
      autocomplete="one-time-code"
      maxlength="1"
      class="otp-input__cell auth-input cosmic-input"
      :class="{ 'otp-input__cell--filled': digits[index], 'otp-input__cell--active': activeIndex === index }"
      :value="digits[index]"
      :aria-label="`Digit ${index + 1} of 6`"
      @input="onCellInput(index, $event)"
      @keydown="onKeydown(index, $event)"
      @focus="activeIndex = index"
      @blur="activeIndex = -1"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'complete'])

const inputRefs = ref([])
const activeIndex = ref(0)

const digits = computed(() => {
  const raw = String(props.modelValue || '').replace(/\D/g, '').slice(0, 6)
  return Array.from({ length: 6 }, (_, i) => raw[i] || '')
})

function setInputRef(el, index) {
  if (el) inputRefs.value[index] = el
}

function updateFromDigits(arr) {
  const value = arr.join('').replace(/\D/g, '').slice(0, 6)
  emit('update:modelValue', value)
  if (value.length === 6) emit('complete', value)
}

function onCellInput(index, event) {
  if (props.disabled) return
  const char = String(event.target.value || '').replace(/\D/g, '').slice(-1)
  const next = [...digits.value]
  next[index] = char
  updateFromDigits(next)
  event.target.value = char
  if (char && index < 5) {
    inputRefs.value[index + 1]?.focus()
  }
}

function onKeydown(index, event) {
  if (props.disabled) return
  if (event.key === 'Backspace') {
    if (digits.value[index]) {
      const next = [...digits.value]
      next[index] = ''
      updateFromDigits(next)
    } else if (index > 0) {
      inputRefs.value[index - 1]?.focus()
      const next = [...digits.value]
      next[index - 1] = ''
      updateFromDigits(next)
    }
    event.preventDefault()
  }
  if (event.key === 'ArrowLeft' && index > 0) {
    inputRefs.value[index - 1]?.focus()
    event.preventDefault()
  }
  if (event.key === 'ArrowRight' && index < 5) {
    inputRefs.value[index + 1]?.focus()
    event.preventDefault()
  }
}

function onPaste(event) {
  if (props.disabled) return
  const pasted = (event.clipboardData?.getData('text') || '').replace(/\D/g, '').slice(0, 6)
  if (!pasted) return
  event.preventDefault()
  updateFromDigits(pasted.split(''))
  const focusIdx = Math.min(pasted.length, 5)
  inputRefs.value[focusIdx]?.focus()
}

watch(
  () => props.modelValue,
  (v) => {
    if (!v && inputRefs.value[0]) {
      inputRefs.value[0].focus()
    }
  }
)

defineExpose({
  focus() {
    inputRefs.value[0]?.focus()
  },
})
</script>
