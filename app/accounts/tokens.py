"""Custom SimpleJWT refresh tokens with a `role` claim (copied to access tokens)."""

from rest_framework_simplejwt.tokens import RefreshToken


class ScreenGramRefreshToken(RefreshToken):
    """Refresh (and derived access) tokens include the user's current `role`."""

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token["role"] = user.role
        return token
