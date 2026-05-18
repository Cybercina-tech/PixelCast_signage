# SaaS Super Admin Panel — Audit Report

**Date:** 2026-05-18  
**Scope:** `/super-admin/*` (Developer role), backend `/api/platform/*`, `/api/platform/blog/*`, `/api/platform/tickets/*`, plus shared `/api/users/`, `/api/screens/`, `/api/core/*`  
**Method:** Static code mapping (frontend ↔ backend) + API probe with Developer JWT + browser smoke on running stack (`http://localhost:4173`)  
**Code changes:** None (read-only audit)

---

## Executive summary

| Category | Count |
|----------|------:|
| Menu sections audited | 22 routes |
| Fully wired (UI + API, probe 200) | 16 |
| Works with env / data caveats | 4 |
| Backend exists, **no Super Admin UI** | 5 |
| UI partial vs backend CRUD | 4 |
| Blocked by config (403) | 1 |

The Super Admin shell is **substantially implemented**. Main gaps are: **gateway instances disabled by default**, **tenant integrations (API keys/webhooks) and per-tenant SaaS license APIs without UI**, **expense ledger read-only in UI**, and **ticket CSV export / agent performance not exposed in UI**.

---

## Prerequisites for SaaS APIs

| Requirement | Dev compose | Notes |
|-------------|-------------|--------|
| Role `Developer` | Required | All `/super-admin` routes use `requiresRole: ['Developer']` |
| `PLATFORM_SAAS_ENABLED` | `true` in `.env` / compose | Most `/api/platform/*` return **403** if false |
| `PLATFORM_GATEWAY_ENABLED` | **`false` in `.env.example`** | Gateway list returns **403** until `true` |
| Stripe keys | Often empty locally | Checkout/portal buttons return 503/400; overview still loads |
| OpenAI (Blog AI) | Optional | Generate fails without key; settings/logs may still load |

Public deployment flags: `GET /api/public/deployment/` (used on System health page).

---

## Section-by-section matrix

Legend:
- **API probe:** HTTP status with valid Developer JWT (2026-05-18, local Docker)
- **UI:** Page exists and loads in browser
- **FE↔BE:** Frontend calls match registered backend routes

| # | Nav label | Route | Frontend | Backend API(s) | API probe | FE↔BE | Verdict |
|---|-----------|-------|----------|------------------|-----------|-------|---------|
| 1 | Dashboard | `/super-admin` | `SuperAdminHome.vue` | `GET /platform/overview/` | 200 | OK | **OK** — KPIs/charts |
| 2 | Blog | `/super-admin/blog` | `SuperAdminBlogList.vue` | `GET/POST/PATCH/DELETE /platform/blog/posts/` | 200 | OK | **OK** |
| 3 | Blog (editor) | `/super-admin/blog/new`, `/:id` | `SuperAdminBlogEditor.vue` | posts CRUD + `POST .../publish/` | (not all probed) | OK | **OK** |
| 4 | Blog AI | `/super-admin/blog/ai` | `SuperAdminBlogAI.vue` | `.../blog/ai/settings|generate|logs/` | 200 settings | OK | **Partial** — needs `OPENAI` / AI config to generate |
| 5 | Reports & cohorts | `/super-admin/reports` | `SuperAdminReports.vue` | overview, cohorts, capacity, reports/summary, tenants | 200 | OK | **OK** |
| 6 | Tenants | `/super-admin/customers` | `platform/TenantsList.vue` | `GET/POST/PATCH/DELETE /platform/tenants/` | 200 | OK | **OK** |
| 7 | Tenant detail | `/super-admin/customers/:id` | `platform/TenantDetail.vue` | tenants CRUD, sync-stripe, manual-override, access-lock, feature-flags, audit-log | (subset 200) | OK | **OK** — impersonate uses `authStore` + `/platform/impersonate/` |
| 8 | All users | `/super-admin/users` | `SuperAdminUsers.vue` | `GET /users/` + tenants list | 200 | OK | **OK** |
| 9 | User manage | `/super-admin/users/:id` | `SuperAdminGlobalUserManage.vue` | `usersAPI` + impersonate | 200 users | OK | **OK** |
| 10 | Devices | `/super-admin/devices` | `SuperAdminDevices.vue` | `GET /screens/` + tenants | 200 | OK | **OK** — global screen list |
| 11 | Billing | `/super-admin/billing` | `SuperAdminBilling.vue` | overview, expenses list, checkout, portal, `licenseAPI.status` | 200 / Stripe deps | Partial | **Partial** — Stripe actions need keys; expenses **list only** |
| 12 | Pricing catalog | `/super-admin/pricing` | `SuperAdminPricing.vue` | plans, settings, promotions | 200 | OK | **Partial** — patch plans/promos; **no UI to create/delete plan** |
| 13 | Self-hosted licenses | `/super-admin/self-hosted-licenses` | `SuperAdminLicenses.vue` | `/platform/self-hosted-licenses/` + actions | 200 | OK | **OK** |
| 14 | Gateway instances | `/super-admin/gateway-instances` | `SuperAdminGatewayInstances.vue` | `GET /platform/gateway/instances/` | **403** | OK route | **Blocked** — set `PLATFORM_GATEWAY_ENABLED=true`; empty table if no instances |
| 15 | Ticket queue | `/super-admin/tickets` | `SuperAdminTicketQueue.vue` | `platformTicketsAPI` → `/platform/tickets/queue/` | 200 | OK | **OK** |
| 16 | Ticket detail | `/super-admin/tickets/:id` | `SuperAdminTicketDetail.vue` | queue assign/transition/reply/merge/upload | (not probed) | OK | **OK** |
| 17 | Ticket analytics | `/super-admin/tickets/analytics` | `SuperAdminTicketAnalytics.vue` | `GET /platform/tickets/analytics/` | 200 | OK | **OK** |
| 18 | Ticket settings | `/super-admin/tickets/settings` | `SuperAdminTicketSettings.vue` | queues, SLA, routing, canned, tags, roles | (not all probed) | OK | **OK** |
| 19 | Alerts & logs | `/super-admin/alerts` | `SuperAdminAlerts.vue` | `GET /platform/communications/` | 200 | OK | **OK** |
| 20 | Capacity | `/super-admin/capacity` | `SuperAdminCapacity.vue` | `GET /platform/capacity/` | 200 | OK | **OK** |
| 21 | Communications (SMTP) | `/super-admin/smtp` | `SystemEmailSettingsPanel.vue` | `GET/PATCH /api/core/...` (system email) | (core) | OK | **OK** — core, not saas_platform |
| 22 | Feature flags | `/super-admin/flags` | `SuperAdminFlags.vue` | `GET/PUT /platform/tenants/:id/feature-flags/` | 200 | OK | **OK** |
| 23 | Audit log | `/super-admin/audit-logs` | `core/AuditLogs.vue` (embedded) | `GET /api/core/audit-logs/` | 200 | OK | **OK** |
| 24 | Backups | `/super-admin/backups` | `core/Backups.vue` (embedded) | `GET/POST /api/core/backups/` | 200 | OK | **OK** |
| 25 | System health | `/super-admin/system` | `SuperAdminSystem.vue` | system-health, public deployment, license status, admin deploy | 200 platform health | OK | **OK** |

---

## Backend APIs with no Super Admin UI

These are defined in `frontend/src/services/api.js` (`platformAPI`) and/or `app/saas_platform/urls.py` but **not used** by any `super-admin` or `platform` page:

| API | Backend | Impact |
|-----|---------|--------|
| `GET /platform/integrations/api-keys/` | `integration_views.tenant_api_keys` | Probe **200** — no UI to manage tenant API keys |
| `POST /platform/integrations/api-keys/` | same | — |
| `POST .../api-keys/:id/revoke/` | same | — |
| `GET/POST /platform/integrations/webhooks/` | `tenant_webhooks` | Probe **200** — no UI for outbound webhooks |
| `GET/PUT /platform/tenants/:id/license/` | `license_views.tenant_license_view` | **No UI** — SaaS tenant license overrides (separate from self-hosted registry) |
| `GET .../license/enforcement-logs/` | same | — |
| `GET /platform/exports/users.xlsx` | `export_views.export_users_xlsx` | **No export button** on All users |
| `GET /platform/gateway/instances/:id/` | `gateway_instance_detail` | List UI only — **no detail/usage drill-down** |
| `GET .../instances/:id/usage/` | `gateway_instance_usage` | — |
| `platformTicketsAPI.exportCsv` | `ticket_export_csv` | **No export UI** in ticket queue/analytics |
| `platformTicketsAPI.agentPerformance` | `agent_performance` | **No UI** |
| `platformAPI.expenses` create/update/delete | `PlatformExpenseViewSet` | Billing shows **read-only** expense table |

---

## Frontend UI gaps (backend not fully used)

| Area | What UI does | What backend supports | Gap |
|------|----------------|----------------------|-----|
| Billing — expenses | Lists recent expenses | Full CRUD on `/platform/billing/expenses/` | No create/edit/delete in UI |
| Pricing | Edit existing plans & promotions | `POST/DELETE` plans, `DELETE` promotions | No “add plan” / delete in UI |
| Gateway | Table list | Detail + usage endpoints | No instance detail page |
| Tickets | Queue, analytics, settings | CSV export, agent performance | Export not wired |
| Tenants | Feature flags on dedicated page + tenant detail | Per-tenant license API | License API unused in tenant UI |

---

## Config / environment issues found

### 1. Gateway instances (403)

- **Cause:** `PLATFORM_GATEWAY_ENABLED=False` by default (`.env.example` line 109).
- **Backend:** `platform_gateway/admin_views._saas_and_gateway()` requires both `PLATFORM_SAAS_ENABLED` and `PLATFORM_GATEWAY_ENABLED`.
- **UI:** `SuperAdminGatewayInstances.vue` shows empty state or error message when load fails.
- **Fix (ops):** Set `PLATFORM_GATEWAY_ENABLED=true` and restart backend.

### 2. Stripe billing actions

- **UI:** Billing → “Stripe Checkout” / “Customer Portal”.
- **Backend:** `/platform/billing/checkout-session/`, `portal-session/` return 503 when Stripe not configured.
- **Overview/charts:** Still work from DB aggregates.

### 3. Blog AI generate

- **Backend:** `/platform/blog/ai/generate/` depends on AI settings and provider key.
- **UI:** Settings/logs load; generate may error without configuration.

### 4. `PLATFORM_SAAS_ENABLED=false`

- All `PlatformSaaSViewSet` and overview endpoints return **403** with message to enable SaaS.
- Super Admin nav still visible only for Developer; pages show errors.

---

## Duplicate / overlapping surfaces

| Feature | Super Admin | Tenant app (`/platform/*`) |
|---------|-------------|---------------------------|
| Tenants list/detail | `/super-admin/customers` | `/platform/tenants` (if routed) |
| Same `TenantsList.vue` / `TenantDetail.vue` with `embedded: true` | Yes | Same components |

Blog uses **Developer-only** platform blog API (`blog/views.py` — not gated by `PLATFORM_SAAS_ENABLED` for CRUD).

---

## Automated test coverage (reference)

| Suite | SaaS relevance |
|-------|----------------|
| `app/tests/test_saas_platform.py` | Extensive platform tenant/billing/pricing tests |
| `app/tests/test_tickets.py` | Platform ticket queue, analytics |
| `app/tests/test_platform_gateway.py` | Gateway (with flags enabled) |
| `app/tests/test_license_registry.py` | Self-hosted licenses |
| `app/tests/test_blog.py`, `test_blog_ai.py` | Blog + AI |
| E2E | No dedicated super-admin Playwright suite; `full-app-smoke` covers main tenant app routes only |

---

## Browser smoke (2026-05-18)

| Page | Result |
|------|--------|
| Login → `/super-admin` | OK — Platform Control Center renders |
| `/super-admin/gateway-instances` | OK shell; empty table (no instances / or 403 swallowed as empty — verify env) |

---

## Implementation status (2026-05-18)

The SaaS panel completion sprint addressed all backlog items above:

| Item | Status |
|------|--------|
| P0 Gateway env + UI banners | Done — `docker-compose.yml`, `.env.example`, `PlatformConfigBanner.vue`, gateway error link |
| P1 Tenant integrations UI | Done — platform APIs `/platform/tenants/:id/integrations/*` + Tenant detail tab |
| P1 Tenant license UI | Done — Tenant detail License tab |
| P2 Billing expenses CRUD | Done — modal in `SuperAdminBilling.vue` |
| P2 Ticket CSV + agent performance | Done — queue export + analytics table |
| P2 Gateway detail + usage chart | Done — `SuperAdminGatewayInstanceDetail.vue` |
| P3 Users XLSX export | Done — `exportUsersXlsx` |
| P3 Pricing create/delete plan & promo | Done — `SuperAdminPricing.vue` |
| P3 Playwright super-admin smoke | Done — `frontend/tests/e2e/super-admin-smoke.spec.js` |

Backend additions: `integration_helpers.py`, `platform_integration_views.py`, `openpyxl` in requirements, `platform_gateway_enabled` on public deployment payload.

---

## Operator checklist

1. Set `PLATFORM_SAAS_ENABLED=true` (or `DEPLOYMENT_MODE=saas`).
2. Set `PLATFORM_GATEWAY_ENABLED=true` if using CodeCanyon gateway admin screens.
3. Configure `STRIPE_*` for Checkout/Portal on Billing.
4. Configure OpenAI key on Blog AI for generation.
5. Ensure `openpyxl` is installed (included in `app/requirements.txt`) for user export.

---

## File references

- Navigation: `frontend/src/config/superAdminNav.js`
- Routes: `frontend/src/router/index.js` (`/super-admin` tree)
- API client: `frontend/src/services/api.js` → `platformAPI`, `platformTicketsAPI`
- Backend routes: `app/saas_platform/urls.py`, `app/tickets/platform_urls.py`, `app/blog/platform_urls.py`, `app/platform_gateway/admin_views.py`

---

*Audit updated after SaaS panel completion sprint.*
