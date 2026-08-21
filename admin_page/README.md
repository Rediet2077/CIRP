# CIRP Platform — Architecture & Guidelines

A modular, domain-driven municipal operations platform built with Next.js (App Router), TanStack Query, Zustand, and Better Fetch.

---

## 1. Modular Directory Structure

The project follows a **strict domain-driven modular structure** under `src/`:

```
src/
├── app/                        # Next.js App Router (Routing & Layouts only)
│   └── (dashboard)/            # Route groups and page entrypoints
│
├── modules/                    # Self-contained domain modules
│   ├── <feature>/              # Example: assets, reports, tasks, departments
│   │   ├── components/         # UI views and centralized dialogs/
│   │   ├── hooks/              # Data-fetching hooks grouped by action
│   │   ├── services/           # Module-specific client utilities
│   │   ├── store/              # Zustand UI stores (modals, active filters)
│   │   └── types/              # Zod schemas and derived TypeScript types
│   │
│   └── shared/                 # Code shared across 2+ feature modules
│       ├── components/         # Shell components, navigation, topbar
│       ├── services/           # API client & storage layer
│       ├── store/              # Global navigation & session state
│       └── types/              # Global schemas, enums, and DTOs
│
├── shared/                     # Design system & shadcn UI primitives
└── lib/                        # Low-level utilities (e.g., cn helper)
```

---

## 2. Core Architectural Principles

### The Unplug Test
Every feature module must be completely self-contained. If you delete any module under `src/modules/<feature>/`, every other module in the system must continue to work without broken imports.

### Dependency Direction
Dependencies flow strictly in one direction:
$$\text{Feature Module} \longrightarrow \text{Shared Module} \longrightarrow \text{Lib}$$

- **No Cross-Feature Imports**: A feature module must **never** import directly from another feature module.
- If code or types are needed by two or more modules, move them to `src/modules/shared/`.

### Two-File Hook Pairing Pattern
Every data operation is decoupled into two complementary files:
1. `<action>.ts`: Pure TypeScript fetcher/mutation using `@better-fetch/fetch` (zero React dependencies), co-locating the query key array and output Zod validation schema.
2. `use_<action>.ts`: React Query hook (`"use client"`) providing caching, loading states, and automatic cache invalidation.

### State Separation
- **Server State**: Managed exclusively by **TanStack Query** (automatic caching, background revalidation, optimistic updates).
- **Client UI State**: Managed via **Zustand** stores (modal open/close states, active filters, transient view state).

### TypeScript & Schema Validation
- **Zero `any` / Zero `never`**: Everything is strictly and explicitly typed.
- **Single Source of Truth**: All domain models and DTOs are defined with **Zod** schemas and inferred via `z.infer<typeof Schema>`.

### UI Component Standards
- Always use **shadcn/ui primitives** (`Button`, `Input`, `Select`, `Dialog`, `Table`, `Card`) rather than raw HTML elements.
- Centralize all modal popups inside `src/modules/<feature>/components/dialogs/`.

---

## 3. Development & Workflow

Use **Bun** exclusively across the project:

```bash
# Install dependencies
bun install

# Start development server
bun run dev

# Typecheck
bunx tsc --noEmit

# Lint
bun run lint
```
