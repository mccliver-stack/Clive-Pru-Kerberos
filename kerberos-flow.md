# Kerberos Authentication Flow

## Overview

Kerberos is a network authentication protocol that uses secret-key cryptography to provide strong authentication for client/server applications. It relies on a trusted third party called the **Key Distribution Center (KDC)**.

---

## Key Components

| Component | Role |
|-----------|------|
| **Client** | The user or service requesting access |
| **KDC (Key Distribution Center)** | Trusted third party; consists of the AS and TGS |
| **AS (Authentication Server)** | Issues Ticket-Granting Tickets (TGTs) |
| **TGS (Ticket-Granting Server)** | Issues service tickets |
| **Service / Application Server** | The target resource the client wants to access |

---

## Authentication Flow (Step-by-Step)

### Phase 1: Initial Authentication (AS Exchange)

```
Client ──── AS-REQ ────► Authentication Server (AS)
       ◄─── AS-REP ────
```

1. **AS-REQ** — The client sends a request to the AS containing:
   - Client principal name (username)
   - Requested TGT lifetime
   - A timestamp encrypted with the client's long-term key (derived from password)

2. **AS-REP** — The AS responds with:
   - A **Ticket-Granting Ticket (TGT)** encrypted with the KDC's secret key
   - A **session key** encrypted with the client's long-term key

   The client decrypts the session key using its password-derived key. The TGT remains opaque to the client.

---

### Phase 2: Service Ticket Request (TGS Exchange)

```
Client ──── TGS-REQ ────► Ticket-Granting Server (TGS)
       ◄─── TGS-REP ────
```

3. **TGS-REQ** — The client sends:
   - The TGT (obtained in Phase 1)
   - An **Authenticator** (timestamp + client info) encrypted with the TGT session key
   - The **SPN** (Service Principal Name) of the target service

4. **TGS-REP** — The TGS responds with:
   - A **Service Ticket** encrypted with the service's long-term key
   - A new **service session key** encrypted with the TGT session key

---

### Phase 3: Service Access (AP Exchange)

```
Client ──── AP-REQ ────► Application / Service Server
       ◄─── AP-REP ────  (optional mutual authentication)
```

5. **AP-REQ** — The client sends to the target service:
   - The Service Ticket
   - An Authenticator encrypted with the service session key

6. **AP-REP** (optional) — The service responds with the client's timestamp encrypted with the service session key, confirming mutual authentication.

---

## Full Flow Diagram

```
   Client              AS (KDC)            TGS (KDC)          Service
     │                    │                    │                  │
     │──── AS-REQ ────────►│                   │                  │
     │◄─── AS-REP ─────────│                   │                  │
     │   (TGT + session key)                   │                  │
     │                                         │                  │
     │──── TGS-REQ ────────────────────────────►│                  │
     │◄─── TGS-REP ────────────────────────────│                  │
     │   (Service Ticket + service session key) │                  │
     │                                                            │
     │──── AP-REQ ─────────────────────────────────────────────►  │
     │◄─── AP-REP (optional) ──────────────────────────────────── │
     │   (Mutual authentication confirmed)                        │
```

---

## Key Concepts

### Ticket-Granting Ticket (TGT)
- Issued by the AS after successful authentication
- Valid for a configurable period (default: 10 hours in Active Directory)
- Contains: client identity, session key, timestamps, and policy flags
- Encrypted with the KDC's secret key — client cannot read it

### Service Ticket
- Issued by the TGS for access to a specific service
- Contains: client identity, service session key, authorization data (PAC in AD)
- Encrypted with the service's long-term key

### Authenticator
- A short-lived message (valid ~5 minutes) proving the client holds the session key
- Prevents replay attacks via the timestamp check

### Service Principal Name (SPN)
- Unique identifier for a service instance (e.g., `HTTP/webserver.domain.com`)
- Used by the TGS to look up the correct service key

---

## Active Directory Context

In an AD environment:
- The **Domain Controller (DC)** acts as the KDC
- User passwords are stored as NTLM hashes and used to derive Kerberos keys (RC4 or AES)
- The **PAC (Privilege Attribute Certificate)** is embedded in tickets and contains group membership and authorization data
- Default ticket lifetime: **10 hours** (TGT), **10 hours** (service ticket)
- Renewal period: **7 days**

---

## Common Kerberos Attacks

| Attack | Description |
|--------|-------------|
| **Pass-the-Ticket** | Reuse a stolen TGT or service ticket without knowing the password |
| **Kerberoasting** | Request service tickets for SPNs and crack them offline (targets weak service account passwords) |
| **AS-REP Roasting** | Target accounts with pre-authentication disabled; crack the AS-REP offline |
| **Golden Ticket** | Forge a TGT using the KRBTGT account hash (requires DC compromise) |
| **Silver Ticket** | Forge a service ticket using a service account hash (no KDC contact needed) |
| **Overpass-the-Hash** | Convert an NTLM hash into a Kerberos TGT |

---

## References

- [RFC 4120 — The Kerberos Network Authentication Service (V5)](https://www.rfc-editor.org/rfc/rfc4120)
- [Microsoft: How Kerberos Authentication Works](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview)
- [Microsoft: Kerberos PAC](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-pac)
