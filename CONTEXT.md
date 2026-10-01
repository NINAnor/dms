# Catalog (DMS)

Catalog is NINA's data management system (DMS): a Django app for cataloging projects, datasets, and services.

## Language

**OIDC Client Role**:
Catalog's existing behavior of delegating user authentication to an external identity provider (e.g. Feide/Keycloak) via django-allauth. Configured through `OIDC_CLIENT_ID`, `OIDC_SECRET`, `OIDC_PROVIDER_URL`, `OIDC_PROVIDER_ID`, `OIDC_PROVIDER_NAME` and wired via `AUTHENTICATION_BACKENDS` / `SOCIALACCOUNT_PROVIDERS`. Catalog is the *relying party* in this role.
_Avoid_: "OIDC", "OIDC integration" (ambiguous with the Provider Role below)

**OIDC Provider Role**:
Catalog acting as the identity source for other applications, issuing them OAuth2/OIDC tokens via `django-oauth-toolkit`. Configured through `OIDC_RSA_PRIVATE_KEY` and the `OAUTH2_PROVIDER` setting, exposed at `/o/`. Catalog is the *authorization server* in this role. Independent of, and additive to, the Client Role above — the two must not be conflated or share settings.
_Avoid_: "OIDC", "SSO provider"
