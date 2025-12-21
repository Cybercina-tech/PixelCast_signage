<template>
  <div class="space-y-6">
    <!-- Template Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">Total Templates</p>
          <p class="text-3xl font-bold text-gray-900">
            {{ analyticsStore.templateStats?.total_templates || 0 }}
          </p>
        </div>
      </Card>

      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">Active Screens</p>
          <p class="text-3xl font-bold text-indigo-600">
            {{ analyticsStore.templateStats?.total_active_screens || 0 }}
          </p>
        </div>
      </Card>

      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">By Orientation</p>
          <div class="space-y-1 mt-2">
            <div v-for="orient in analyticsStore.templateStats?.by_orientation || []" :key="orient.orientation">
              <span class="text-sm text-gray-600">{{ orient.orientation }}:</span>
              <span class="text-lg font-bold text-gray-900 ml-2">{{ orient.count }}</span>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Most Active Templates -->
    <Card title="Most Active Templates">
      <div v-if="analyticsStore.templateStats?.most_active_templates?.length > 0" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Template Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Active Screens</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="template in analyticsStore.templateStats.most_active_templates" :key="template.template_id">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ template.template_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <span class="px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs font-medium">
                  {{ template.active_screen_count }} screens
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <router-link
                  :to="`/templates/${template.template_id}`"
                  class="text-indigo-600 hover:text-indigo-900 font-medium"
                >
                  View Details
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center text-gray-500 py-8">
        No active templates data available
      </div>
    </Card>
  </div>
</template>

<script setup>
import { useAnalyticsStore } from '@/stores/analytics'
import Card from '@/components/common/Card.vue'

const analyticsStore = useAnalyticsStore()
</script>
