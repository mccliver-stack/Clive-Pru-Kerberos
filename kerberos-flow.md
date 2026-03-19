# Kerberos Authentication Flow in Active Directory

## Overview

Kerberos is a network authentication protocol that uses secret-key cryptography and a trusted third party (the Key Distribution Center) to authenticate users and services without transmitting passwords over the network.

## Key Components

| Component | Description |
|-----------|-------------|
| **KDC (Key Distribution Center)** | Runs on the Domain Controller; consists of the AS and TGS |
| **AS (Authentication Service)** | Issues Ticket-Granting Tickets (TGTs) |
| **TGS (Ticket-Granting Service)** | Issues service tickets |
| **TGT (Ticket-Granting Ticket)** | Proof of identity; used to request service tickets |
| **Service Ticket (ST)** | Grants access to a specific service |
| **Client** | The user or machine requesting access |
| **Service Principal (SP)** | The resource the client wants to access |

---

## Step-by-Step Authentication Flow

### Phase 1: Initial Authentication (AS Exchange)

**Step 1 — Client sends an Authentication Request (AS-REQ)**

The client sends a plaintext request to the KDC's Authentication Service containing:
- The client's username
- The target service name (`krbtgt`)
- A timestamp encrypted with the client's secret key (derived from the user's password)

```
Client → KDC (AS):  AS-REQ
  - Username (plaintext)
  - Encrypted timestamp (key = hash of user's password)
```

**Step 2 — KDC validates and issues a TGT (AS-REP)**

The KDC looks up the user's password hash, decrypts the timestamp, and checks for freshness (to prevent replay attacks). If valid, the KDC responds with:
- A **TGT** encrypted with the KDC's own secret key (`krbtgt` account hash) — the client cannot read this
- A **session key** encrypted with the client's secret key — the client can decrypt this

```
KDC (AS) → Client:  AS-REP
  - TGT (encrypted with krbtgt key)
  - Session Key (encrypted with client's key)
```

The client decrypts its session key and stores the TGT in its credential cache. The TGT typically has a default lifetime of **10 hours** in Active Directory.

---

### Phase 2: Service Ticket Request (TGS Exchange)

**Step 3 — Client requests a Service Ticket (TGS-REQ)**

When the client wants to access a service (e.g., a file server), it sends a request to the KDC's Ticket-Granting Service containing:
- The **TGT** (proving identity to the KDC)
- An **authenticator** (timestamp encrypted with the session key from Phase 1)
- The **Service Principal Name (SPN)** of the target service

```
Client → KDC (TGS):  TGS-REQ
  - TGT (opaque to client)
  - Authenticator (timestamp encrypted with session key)
  - Requested SPN (e.g., cifs/fileserver.corp.local)
```

**Step 4 — KDC issues a Service Ticket (TGS-REP)**

The KDC decrypts the TGT using the `krbtgt` key to retrieve the session key, then uses it to verify the authenticator. If valid, the KDC responds with:
- A **Service Ticket (ST)** encrypted with the target service's secret key — the client cannot read this
- A **service session key** encrypted with the client's session key — the client can decrypt this

```
KDC (TGS) → Client:  TGS-REP
  - Service Ticket (encrypted with service's key)
  - Service Session Key (encrypted with client's session key)
```

---

### Phase 3: Service Authentication (AP Exchange)

**Step 5 — Client presents the Service Ticket (AP-REQ)**

The client contacts the target service directly and sends:
- The **Service Ticket** (which it cannot read)
- An **authenticator** encrypted with the service session key

```
Client → Service:  AP-REQ
  - Service Ticket (encrypted with service's key)
  - Authenticator (encrypted with service session key)
```

**Step 6 — Service validates the ticket (AP-REP)**

The service decrypts the Service Ticket using its own secret key (retrieved from Active Directory via its machine account). It then:
1. Extracts the service session key from the ticket
2. Uses it to decrypt and verify the authenticator
3. Checks the timestamp to prevent replay attacks

If mutual authentication is requested, the service responds with:
- A timestamp from the authenticator, encrypted with the service session key (proving it possesses the key)

```
Service → Client:  AP-REP (optional, for mutual auth)
  - Encrypted timestamp (confirming service identity)
```

The client is now authenticated and the session begins.

---

## Complete Flow Diagram

```
  Client                    KDC (Domain Controller)               Service
    |                        |         |                              |
    |------- AS-REQ -------->|         |                              |
    |    (username +         |   AS    |                              |
    |     enc. timestamp)    |         |                              |
    |                        |         |                              |
    |<------ AS-REP ---------|         |                              |
    |    (TGT + session key) |         |                              |
    |                        |         |                              |
    |                        |         |                              |
    |------- TGS-REQ --------|-------->|                              |
    |    (TGT + authenticator|   TGS   |                              |
    |     + target SPN)      |         |                              |
    |                        |         |                              |
    |<------ TGS-REP --------|---------|                              |
    |    (Service Ticket +   |         |                              |
    |     service session key)         |                              |
    |                                  |                              |
    |------- AP-REQ ---------------------------------------------------------------->|
    |    (Service Ticket + authenticator)                             |
    |                                                                 |
    |<------ AP-REP (optional) -------------------------------------<-|
    |    (mutual auth confirmation)                                   |
    |                                                                 |
    |===================== Authenticated Session =====================|
```

---

## Key Security Properties

- **No password transmission** — passwords never travel over the network; only hashes are used to encrypt/decrypt
- **Mutual authentication** — both client and service can verify each other's identity
- **Replay protection** — timestamps and short validity windows prevent reuse of captured tickets
- **Ticket delegation** — services can request tickets on behalf of users (with appropriate delegation settings)

## Active Directory-Specific Notes

- The `krbtgt` account's password hash is the KDC's master secret; compromising it enables **Golden Ticket** attacks
- SPNs must be registered in AD for Kerberos to locate services (falls back to NTLM if no SPN is found)
- **Pre-authentication** is enabled by default; disabling it allows **AS-REP Roasting** attacks
- Default ticket lifetimes: TGT = 10 hours, max renewal = 7 days, service tickets = 10 hours
- **Kerberoasting** targets service accounts by requesting service tickets and cracking them offline
