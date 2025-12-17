<template>
  <div class="w-full h-64">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps({
  type: {
    type: String,
    default: 'line',
    validator: (value) => ['line', 'bar', 'doughnut', 'pie'].includes(value),
  },
  data: {
    type: Object,
    required: true,
  },
  options: {
    type: Object,
    default: () => ({}),
  },
})

const chartCanvas = ref(null)
let chartInstance = null

const createChart = () => {
  if (chartCanvas.value && !chartInstance) {
    const ctx = chartCanvas.value.getContext('2d')
    chartInstance = new ChartJS(ctx, {
      type: props.type,
      data: props.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        ...props.options,
      },
    })
  }
}

onMounted(() => {
  createChart()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})

watch(
  () => props.data,
  (newData) => {
    if (chartInstance) {
      chartInstance.data = newData
      chartInstance.update()
    } else {
      createChart()
    }
  },
  { deep: true }
)

watch(
  () => props.type,
  (newType) => {
    if (chartInstance) {
      chartInstance.destroy()
      chartInstance = null
      createChart()
    }
  }
)

watch(
  () => props.options,
  () => {
    if (chartInstance) {
      chartInstance.options = {
        responsive: true,
        maintainAspectRatio: false,
        ...props.options,
      }
      chartInstance.update()
    }
  },
  { deep: true }
)
</script>
