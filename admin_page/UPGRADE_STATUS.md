# CIRP upgrade status

## Project audit

The repository contains a Next.js 16 / React 19 TypeScript administration web app organized by domain modules. Existing screens cover reports, tasks, assets, departments, contractors, users, analytics, notifications, GIS, extensions, and audit history. TanStack Query and a typed API client are present. The README describes a separate Flutter client and a Django REST / PostgreSQL backend, but neither is present in this checkout. No database schema, migration framework, API route handlers, or server-side authorization layer was found.

Most screen data currently comes from `mock_storage.ts` and static browser-side records. These operations are in-memory and are lost on reload. The existing role selector changed client state directly, the initial role was the system administrator, and login accepted an arbitrary email as a fabricated system administrator when the API was unavailable. A configured API error also fell through to local mock data.

## Changes in this upgrade

- Unknown, inactive, or incorrectly credentialed demo accounts no longer receive a generated administrator identity. Demo login only accepts an active account in the listed sample-user set and the explicit demo password.
- A configured API is authoritative: request errors and empty responses now surface instead of silently returning mock results.
- Dashboard pages check the stored session before rendering, restore role and department scope from the session, redirect unauthenticated users, and route Department Admins away from global management pages.
- Department Admin navigation omits departments, users, system settings, and audit logs. The account role switcher was removed, and the initial client role is least-privileged.
- Logout clears the browser-side session and query cache.
- A persistent “Demo data” badge and login-page notice identify the sample data and demo credentials.
- Added focused tests for role navigation, the sample administrator set, public report projection, and coordinate validation.
- Added one demo account for each of the seven department domains. The sample list contains one active Super Admin; this is not a backend constraint.
- Added public report tracking that projects only report reference, category, public status, date, and generalized location. It uses a dedicated public API endpoint and a strict response schema.
- Updated the GIS view to plot valid coordinates from reports and assets in scope, and removed the drawn roads and sub-city labels. It now identifies itself as a coordinate plot because no basemap or boundary service is configured.
- AI insight labels describe the indicators as unverified suggestions and avoid presenting “no match” as proof of uniqueness.

These UI checks improve the current prototype but do not secure data or privileged operations. Browser storage and client-side role state can be changed by the user. The backend must validate identity, role, department and geographic scope on every request.

## Backend and production blockers

- **Authentication:** the repo has no server auth implementation. Demo sessions and the demo passwords (`password123` for City Admin; each department uses its name plus `CIRP321`) are not suitable for deployment. Connect the existing REST API before using real accounts; implement password hashing, HTTP-only secure sessions or short-lived JWTs, rotation/revocation, reset flows, and login throttling there.
- **Single Super Admin:** the local sample list contains one active `SYSTEM_ADMIN`, but there is no database constraint, transaction, or account-management API enforcing one active system administrator. Add a transactional invariant and protect against disabling the last active account in the backend database.
- **RBAC and scope:** navigation and dashboard checks run in the browser. The Django API must authorize every endpoint, reject role changes by Department Admins, and derive department/geographic scope from the authenticated principal rather than request query parameters.
- **Persistence and workflow:** report/task mutations currently modify a process-local mock singleton. No durable database operations, workflow transition validation, migrations, or tamper-evident audit log are implemented in this repository.
- **GIS:** the map plots report and asset markers with valid coordinate ranges, but has no basemap, boundaries, clustering, or authoritative location-based assignment. Those require backend and GIS data.
- **AI:** report records contain sample AI-shaped fields, but no model or AI service is configured. No real duplicate analysis or human review decisions are recorded.
- **Transparency and notifications:** the public tracking page is implemented, but its public API endpoint must be supplied by the backend and return only the strict public projection. Notification screens still use local sample data.
- **Department roles:** current data models distinguish `SYSTEM_ADMIN` and generic `DEPARTMENT_ADMIN`; the seven demo accounts are assigned to separate departments, but there are no distinct named role types, admin assignment management, geographic scopes, category mappings, or server endpoint permission tests.
- **Mobile application:** no Flutter/mobile project is present in this repository; this upgrade did not modify it.

## Configuration and migrations

- Existing configuration: `NEXT_PUBLIC_API_URL` selects the REST API base URL used by the typed client. It must point to a compatible API implementing the endpoint contracts used by the modules. API failures now remain visible to the user.
- No new secrets or production credentials were added. Do not treat the local demo credentials as real credentials.
- No database migration is included because there is no database or migration system in this checkout. Backend migrations are required for administrator roles/scopes, Super Admin uniqueness, report workflow history, audits, and indexes.
- No additional external AI, GIS, storage, or notification service has been configured.

## Verification

- Automated tests were added, but could not run because Bun is not installed in the environment (`bun` is not recognized).
- Lint, TypeScript compiler checks, and production builds were not run. The repository's `AGENTS.md` explicitly prohibits running those commands.
