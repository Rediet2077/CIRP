# Local Agent Rules & Project Directives

## Component Line Count Limit & Refactoring
- **Maximum 205 Lines of Code (LOC) per File**: If a component or file reaches or exceeds 205 LOC, you CANNOT add anything directly to it. You MUST refactor it into smaller sub-components or helpers using dedicated sub-folders (e.g. `components/`, `dialogs/`, `subcomponents/`, `menu/`) before adding new functionality.

## Verification & Commands Constraint
- **NEVER run `bun run lint`, `eslint`, or any linting commands.**
- **NEVER run `tsc --noEmit`, `bunx tsc --noEmit`, or TypeScript compiler checks.**
- **NEVER run `bun run build`, `npm run build`, or any build commands.**
- Package manager: Use **Bun exclusively** (`bun`, `bunx`).

<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
