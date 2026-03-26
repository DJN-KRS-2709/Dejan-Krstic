# Best Practices Reference

Reference tables for `/systems-inventory` audits. The skill auto-detects the tech stack and applies the relevant checks.

---

## Universal Checks (all repos)

These checks apply regardless of tech stack.

| Check | Method | What It Detects | Gap If Missing |
|-------|--------|----------------|----------------|
| README.md | `search_code(query="f:^README.md$", repo=...)` | Documentation exists | Discoverability, onboarding friction |
| CODEOWNERS | `search_code(query="f:CODEOWNERS$", repo=...)` | Review enforcement | No team-specific code review. Blocks "Ready" rating. |
| service-info.yaml | `search_code(query="f:service-info.yaml$", repo=...)` + read lifecycle | Service registration, lifecycle | Not registered in Backstage |
| AGENTS.md | `search_code(query="f:^AGENTS.md$", repo=...)` | Agentic readiness | Blocks agentic-first mandate |
| CLAUDE.md | `search_code(query="f:^CLAUDE.md$", repo=...)` | Agentic readiness | Blocks agentic-first mandate |
| build-info.yaml | `search_code(query="f:build-info.yaml$", repo=...)` | CI/CD configuration | Informational only |
| Tests | `search_code(query="f:test", repo=...)` | Test coverage exists | No automated validation |

---

## Stack Detection

Auto-detect the tech stack from repo contents, then apply the relevant stack-specific checks.

| Stack | Detection Signal | Detection Query |
|-------|-----------------|-----------------|
| Java/Apollo | `com.spotify.apollo` in code | `search_code(query="com.spotify.apollo", repo=...)` |
| Java/Spring | `org.springframework` or `SpringBootApplication` | `search_code(query="org.springframework", repo=...)` |
| Python | `pyproject.toml` or `setup.py` at root | `search_code(query="f:^pyproject.toml$", repo=...)` |
| TypeScript/React | `package.json` + `react` dependency | `search_code(query="f:^package.json$", repo=...)` then read for `react` |
| Markdown/Scripts | No build system detected | Fallback: classify as non-service repo |

---

## Java/Apollo Stack Checks

Spotify's standard backend stack. Applies when Apollo or Spring is detected.

| Dimension | Best Practice | Non-Standard (flag as gap) | Detection Query |
|-----------|--------------|---------------------------|-----------------|
| Framework | Spotify Apollo (`com.spotify.apollo`) | Spring Boot (`SpringBootApplication`) | See stack detection above |
| Storage | CloudSQL/JDBI, BigTable/Decibel, or Spanner | Cassandra (deprecated/EOL), Hibernate/JPA | `search_code(query="jdbi", repo=...)`, `search_code(query="hibernate", repo=...)`, `search_code(query="cassandra", repo=...)` |
| ORM / Data Access | JDBI (preferred) or direct JDBC | Hibernate/JPA (non-standard) | `search_code(query="javax.persistence", repo=...)`, `search_code(query="jakarta.persistence", repo=...)` |
| Java version | Java 25 (current standard) | Below 25 = gap. Below 21 = critical. | `search_code(query="maven.compiler.release", repo=...)` or `search_code(query="java_version", repo=...)` |
| Build (polyrepo) | Maven (pom.xml) | Gradle, Ant | `search_code(query="f:^pom.xml$", repo=...)` |
| Build (monorepo) | Bazel (BUILD.bazel) | Maven in monorepo is non-standard | `search_code(query="f:BUILD.bazel$", repo=...)` |
| Communication | gRPC with Protobuf | REST-only or legacy HTTP | `search_code(query="grpc", repo=...)` |
| Quality gates (monorepo) | warnings_as_errors=True, nullaway=True | Any disabled = gap | `search_code(query="warnings_as_errors = False", repo=...)` |

---

## Python Stack Checks

Applies when `pyproject.toml` or `setup.py` is detected.

| Dimension | Best Practice | Non-Standard (flag as gap) | Detection Query |
|-----------|--------------|---------------------------|-----------------|
| Package config | pyproject.toml | setup.py only (legacy) | `search_code(query="f:^setup.py$", repo=...)` |
| Python version | Python 3.12+ | Below 3.11 = gap | `search_code(query="python_requires", repo=...)` or `search_code(query="python-version", repo=...)` |
| Framework | FastAPI (preferred for new services) | Flask or Django (not wrong, but note it) | `search_code(query="fastapi", repo=...)`, `search_code(query="flask", repo=...)` |
| Linting | ruff (preferred) | flake8/pylint only (legacy) | `search_code(query="f:ruff.toml", repo=...)`, `search_code(query="ruff", repo=...)` |
| Type checking | mypy or pyright configured | No type checking | `search_code(query="mypy", repo=...)` or `search_code(query="f:pyrightconfig", repo=...)` |

---

## TypeScript/React Stack Checks

Applies when `package.json` with `react` dependency is detected.

| Dimension | Best Practice | Non-Standard (flag as gap) | Detection Query |
|-----------|--------------|---------------------------|-----------------|
| Node version | Node 22+ | Below 20 = gap | `search_code(query="f:.nvmrc$", repo=...)` or check `engines` in package.json |
| Framework | Next.js or Vite (modern bundlers) | Webpack-only (legacy) | `search_code(query="next", repo=...)`, `search_code(query="vite", repo=...)` |
| Test runner | Jest or Playwright (or both) | No test runner configured | `search_code(query="f:jest.config", repo=...)`, `search_code(query="f:playwright.config", repo=...)` |
| TypeScript | TypeScript configured | JavaScript only | `search_code(query="f:tsconfig", repo=...)` |
| Linting | ESLint configured | No linting | `search_code(query="f:eslint", repo=...)` |

---

## Readiness Rating Logic

| Rating | Criteria |
|--------|----------|
| **Ready** | Has tests + CI/build + CODEOWNERS + clear README + production lifecycle |
| **Read-only** | Missing one+ of above but active and structured enough for PR summaries |
| **Not ready** | Archived, deprecated, or insufficient infrastructure |

Missing AGENTS.md/CLAUDE.md does NOT downgrade the rating but is always flagged as a gap.

---

## Monorepo-Specific Checks

For services in shared monorepos (e.g., `spotify/services-pilot`):

1. **Path-scoped searches:** All file existence checks must be scoped to the service's path prefix
2. **CODEOWNERS path entries:** Check if the team has explicit path entries in the monorepo CODEOWNERS (not just generic fallthrough)
3. **Quality gates:** Check BUILD.bazel for disabled `warnings_as_errors`, `nullaway`, `proto_lint_disable`
4. **Root CLAUDE.md:** Note if the monorepo root has a CLAUDE.md but the service path does not
