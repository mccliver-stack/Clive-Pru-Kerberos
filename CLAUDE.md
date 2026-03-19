# CLAUDE.md — AI Assistant Guide for Clive-Pru-Kerberos

## Project Overview

This is a **learning and documentation repository** focused on enterprise authentication systems:
- **Kerberos** — the core authentication protocol (RFC 4120)
- **Active Directory (AD)** — Microsoft's directory service and Kerberos KDC implementation
- **Active Directory Federation Services (ADFS)** — Microsoft's federation/SSO layer
- **Entra ID** (formerly Azure AD) — Microsoft's cloud identity platform

The goal is to map authentication flows, explain concepts step-by-step, and document real-world enterprise scenarios for learning purposes.

---

## Repository Structure

```
Clive-Pru-Kerberos/
├── CLAUDE.md          # This file — AI assistant guidance
├── Readme.md          # Project overview and goals
└── (future content)   # Documentation files to be added
```

This repository is in its **early stage**. No source code, build system, or CI/CD pipeline exists. All contributions are expected to be documentation (Markdown files, diagrams, reference materials).

---

## Technology Stack

| Layer | Technology |
|---|---|
| Content format | Markdown (`.md`) |
| Diagrams | Mermaid (preferred), ASCII art, or linked images |
| Version control | Git |
| Hosting | GitHub (mccliver-stack/Clive-Pru-Kerberos) |

No programming language runtime, package manager, or test framework is required.

---

## Git Workflow

### Branch Naming
- Feature/content branches: `claude/<short-description>-<session-id>`
- Main branch: `master` (local) / `main` (remote origin)

### Commit Convention
Use clear, descriptive commit messages in the imperative mood:
```
Add Kerberos AS-REQ/AS-REP flow documentation
Update ADFS token issuance sequence diagram
Fix typo in Entra ID section
```

### Push
Always push with upstream tracking:
```bash
git push -u origin <branch-name>
```

Branches must begin with `claude/` to avoid 403 errors on push.

---

## Documentation Conventions

### File Naming
- Use lowercase, hyphen-separated filenames: `kerberos-basics.md`, `adfs-flow.md`
- Group related topics into subdirectories when content grows (e.g., `kerberos/`, `entra-id/`, `adfs/`)

### Markdown Style
- Use `#` for top-level title (one per file)
- Use `##` and `###` for section and subsection headers
- Wrap protocol field names, commands, and technical terms in backticks: `TGT`, `AS-REQ`, `krb5.conf`
- Use fenced code blocks with language tags for any code or config samples:
  ````
  ```bash
  kinit user@REALM.COM
  ```
  ````
- Prefer Mermaid sequence diagrams for authentication flows:
  ````
  ```mermaid
  sequenceDiagram
      Client->>KDC: AS-REQ
      KDC-->>Client: AS-REP (TGT)
  ```
  ````

### Content Structure for Authentication Flows
When documenting a protocol or flow, use this structure:
1. **Overview** — what the mechanism does and why it exists
2. **Components** — entities involved (client, KDC, service, etc.)
3. **Step-by-step flow** — numbered steps with message names
4. **Diagram** — Mermaid sequence or flow diagram
5. **Key fields** — important protocol fields or tokens explained
6. **Real-world context** — enterprise use cases, gotchas, common misconfigurations

---

## Subject Matter Guidance

### Kerberos
- Focus on RFC 4120 concepts: AS exchange, TGS exchange, AP exchange
- Key message types: `AS-REQ`, `AS-REP`, `TGS-REQ`, `TGS-REP`, `AP-REQ`, `AP-REP`
- Key artifacts: Ticket Granting Ticket (TGT), Service Ticket (ST), session keys
- Common extensions: PKINIT, S4U2Self, S4U2Proxy, Kerberos constrained delegation

### Active Directory
- AD acts as both Kerberos KDC and LDAP directory
- Domain Controllers issue tickets; the realm maps to the AD domain (e.g., `CORP.EXAMPLE.COM`)
- Important: PAC (Privilege Attribute Certificate) is Microsoft's extension to Kerberos tickets

### ADFS
- Federation server that bridges on-prem AD with external relying parties
- Issues SAML 2.0 tokens, WS-Federation tokens, and OAuth/OIDC tokens
- Key flows: WS-Federation passive, SAML 2.0 POST/Redirect, OAuth 2.0 authorization code

### Entra ID (formerly Azure AD)
- Cloud identity provider supporting OIDC, OAuth 2.0, SAML 2.0
- Hybrid identity: synced with on-prem AD via Entra Connect (formerly AAD Connect)
- Key concepts: Primary Refresh Token (PRT), Seamless SSO, Pass-through Authentication (PTA), ADFS federation

---

## AI Assistant Behavioral Guidelines

### Do
- Add content as Markdown files following the naming and structure conventions above
- Use precise, technically accurate terminology for Kerberos and identity protocols
- Cite RFC numbers or Microsoft documentation when referencing specifications
- Create or update Mermaid diagrams to illustrate flows visually
- Keep documentation concise but complete — avoid padding

### Do Not
- Add source code, build scripts, or CI/CD configuration unless explicitly requested
- Introduce dependencies or package managers — this is a docs-only repo
- Create files outside of Markdown unless there is a clear documented need
- Push to `master` or `main` directly — always use a feature branch

### When Adding New Topics
1. Create a new `.md` file following naming conventions
2. Follow the content structure defined above
3. Link from `Readme.md` if appropriate
4. Commit with a descriptive message and push to the working branch

---

## Current State (as of March 2026)

- [x] Repository initialized
- [x] Readme.md created with project goals
- [x] CLAUDE.md created (this file)
- [ ] Kerberos basics documentation
- [ ] AD authentication flow diagrams
- [ ] ADFS federation flows
- [ ] Entra ID hybrid identity documentation
