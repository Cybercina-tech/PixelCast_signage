import { describe, it, expect } from 'vitest'
import { isTransientNetworkError } from './networkError'

describe('isTransientNetworkError', () => {
  it('returns true for axios network error without response', () => {
    expect(isTransientNetworkError({ message: 'Network Error' })).toBe(true)
  })

  it('returns false when response exists', () => {
    expect(isTransientNetworkError({ message: 'Network Error', response: { status: 500 } })).toBe(false)
  })

  it('returns true for ERR_NETWORK code', () => {
    expect(isTransientNetworkError({ code: 'ERR_NETWORK', message: 'x' })).toBe(true)
  })
})
