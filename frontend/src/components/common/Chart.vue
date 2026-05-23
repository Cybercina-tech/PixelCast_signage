<template>
  <div class="w-full h-52 min-h-[13rem] sm:h-64 sm:min-h-[16rem]">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { Chart as ChartJS } from 'chart.js'
import { useThemeStore } from '@/stores/theme'

// Chart.js components are registered globally in plugins/chartjs.js
// No need to register here - they're already available

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
const themeStore = useThemeStore()

const buildThemedOptions = (baseOptions = {}) => {
  const isDark = themeStore.isDarkMode
  const axisTickColor = isDark ? '#94a3b8' : '#64748b'
  const axisGridColor = isDark ? 'rgba(148, 163, 184, 0.14)' : 'rgba(15, 23, 42, 0.1)'
  const legendColor = isDark ? '#e2e8f0' : '#334155'
  const tooltipBg = isDark ? 'rgba(15, 23, 42, 0.9)' : 'rgba(255, 255, 255, 0.96)'
  const tooltipTitle = isDark ? '#f8fafc' : '#0f172a'
  const tooltipBody = isDark ? '#cbd5e1' : '#334155'
  const tooltipBorder = isDark ? 'rgba(148, 163, 184, 0.24)' : 'rgba(148, 163, 184, 0.3)'

  const themedScales = baseOptions.scales
    ? Object.fromEntries(
        Object.entries(baseOptions.scales).map(([key, value]) => [
          key,
          {
            ...value,
            ticks: {
              color: axisTickColor,
              ...(value?.ticks || {}),
            },
            grid: {
              color: axisGridColor,
              ...(value?.grid || {}),
            },
          },
        ]),
      )
    : undefined

  return {
    responsive: true,
    maintainAspectRatio: false,
    ...baseOptions,
    plugins: {
      ...(baseOptions.plugins || {}),
      legend: {
        ...(baseOptions.plugins?.legend || {}),
        labels: {
          color: legendColor,
          ...(baseOptions.plugins?.legend?.labels || {}),
        },
      },
      tooltip: {
        backgroundColor: tooltipBg,
        titleColor: tooltipTitle,
        bodyColor: tooltipBody,
        borderColor: tooltipBorder,
        borderWidth: 1,
        ...(baseOptions.plugins?.tooltip || {}),
      },
    },
    ...(themedScales ? { scales: themedScales } : {}),
  }
}

const createChart = () => {
  if (!chartCanvas.value) return
  
  // Destroy existing chart if it exists
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
  
  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return
  
  // Ensure data is valid
  const chartData = props.data || { labels: [], datasets: [] }
  
  chartInstance = new ChartJS(ctx, {
    type: props.type,
    data: chartData,
    options: buildThemedOptions(props.options),
  })
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
        ...buildThemedOptions(props.options),
      }
      chartInstance.update()
    }
  },
  { deep: true }
)

watch(
  () => themeStore.theme,
  () => {
    if (!chartInstance) return
    chartInstance.options = {
      ...buildThemedOptions(props.options),
    }
    chartInstance.update()
  },
)
</script>
