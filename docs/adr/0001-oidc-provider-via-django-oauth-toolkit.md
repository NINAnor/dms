# Issue tokens as an OIDC provider using django-oauth-toolkit

Catalog already acts as an OIDC *client* (via django-allauth, authenticating its own users against an external IdP). We now also need catalog to act as an OIDC *provider*, issuing tokens to other apps that treat catalog as their identity source. We decided to add this second, independent role using `django-oauth-toolkit` (RS256, `OIDC_ENABLED`), mirroring the pattern already proven in `seapop-backend` (commits bfcdd0a/f440740) and `genlab_bestilling` (commits 16a3521/77c35cd), rather than inventing a bespoke implementation. The two roles are kept fully separate: the provider wiring (`oauth2_provider` app, `/o/` routes, `OAUTH2_PROVIDER` setting, `OIDC_RSA_PRIVATE_KEY`) is additive and must not touch the existing client-side `AUTHENTICATION_BACKENDS` / `SOCIALACCOUNT_PROVIDERS` / `OIDC_CLIENT_ID` / `OIDC_SECRET` / `OIDC_PROVIDER_*` settings used for allauth.

## Considered Options

- Build a custom OAuth2/OIDC provider from scratch — rejected: `django-oauth-toolkit` already solves this and is proven across two sibling NINA repos with an identical shape of settings.
- Reuse/extend the existing allauth `OIDC_*` env vars for the provider's signing key — rejected: the human maintainer explicitly asked to keep the bare `OIDC_RSA_PRIVATE_KEY` name (unprefixed, as in the reference repos) but rely on `.env.example` comments to disambiguate client vs. provider, rather than inventing a new prefixed name, to stay consistent with the established cross-repo pattern.

## Consequences

- v1 ships with Authorization Code + PKCE grant only, baseline OIDC claims (`openid` scope; `sub`, `email`, `name`), and Django-admin-only management of `oauth2_provider.Application` — no seeded fixture, no custom claims, no Client Credentials grant, no custom UI. These are intentional scope cuts, not oversights; revisit only when a concrete consumer needs them.
- `OAUTH2_PROVIDER` is enabled conditionally on the presence of `OIDC_RSA_PRIVATE_KEY`, matching the reference repos' pattern of logging `OIDC_ENABLED: True/False` at boot so the feature is opt-in and backward compatible when the env var is absent.
