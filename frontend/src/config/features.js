/**

 * Feature flags (build-time). Keep in sync with backend settings.

 */

export const ENABLE_2FA = import.meta.env.VITE_ENABLE_2FA === 'true'



/** Email OTP after login/signup — matches backend REQUIRE_EMAIL_VERIFICATION */

export const ENABLE_EMAIL_VERIFICATION =

  import.meta.env.VITE_REQUIRE_EMAIL_VERIFICATION === 'true'


