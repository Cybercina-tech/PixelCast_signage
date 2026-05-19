import { computed, unref } from 'vue'

/**
 * Format subscription trial / billing remaining for dashboard and settings.
 * @param {import('vue').MaybeRefOrGetter<object|null|undefined>} subscription
 */
export function useBillingTrial(subscription) {
  const sub = computed(() => {
    const raw = typeof subscription === 'function' ? subscription() : unref(subscription)
    return raw || null
  })

  const trialDaysRemaining = computed(() => {
    const days = sub.value?.trial_days_remaining
    return days === null || days === undefined ? null : Number(days)
  })

  const billingDaysRemaining = computed(() => {
    const days = sub.value?.billing_days_remaining
    return days === null || days === undefined ? null : Number(days)
  })

  const hasActiveTrial = computed(() => trialDaysRemaining.value !== null)

  const trialRemainingLabel = computed(() => {
    if (trialDaysRemaining.value === null) return null
    const n = trialDaysRemaining.value
    if (n <= 0) return 'Trial ended'
    if (n === 1) return '1 day left in trial'
    return `${n} days left in trial`
  })

  const billingRemainingLabel = computed(() => {
    if (billingDaysRemaining.value === null) return null
    const n = billingDaysRemaining.value
    if (n <= 0) return 'Billing period ended'
    if (n === 1) return '1 day left in billing period'
    return `${n} days left in billing period`
  })

  const showBillingPeriod = computed(() => billingDaysRemaining.value !== null)

  return {
    trialDaysRemaining,
    billingDaysRemaining,
    hasActiveTrial,
    trialRemainingLabel,
    billingRemainingLabel,
    showBillingPeriod,
  }
}
