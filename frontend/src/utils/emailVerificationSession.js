export const EMAIL_VERIFY_TOKEN_KEY = 'pixelcast_email_verification_token'
export const EMAIL_VERIFY_MASKED_KEY = 'pixelcast_email_verification_email'

export function storeEmailVerificationSession(token, email) {
  if (token) sessionStorage.setItem(EMAIL_VERIFY_TOKEN_KEY, token)
  if (email) sessionStorage.setItem(EMAIL_VERIFY_MASKED_KEY, email)
}

export function clearEmailVerificationSession() {
  sessionStorage.removeItem(EMAIL_VERIFY_TOKEN_KEY)
  sessionStorage.removeItem(EMAIL_VERIFY_MASKED_KEY)
}

export function readEmailVerificationSession() {
  return {
    token: sessionStorage.getItem(EMAIL_VERIFY_TOKEN_KEY) || '',
    email: sessionStorage.getItem(EMAIL_VERIFY_MASKED_KEY) || '',
  }
}
