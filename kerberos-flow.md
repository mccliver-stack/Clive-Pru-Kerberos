# Kerberos Authentication Flow in Active Directory

> **Interview tip:** Think of Kerberos like a concert venue. You show your ID at the gate (AS exchange) to get a wristband (TGT). Then you show the wristband at the bar (TGS exchange) to get a drink token (Service Ticket). Finally, you hand the drink token to the bartender (AP exchange) to get your drink — no one ever asks for your ID again.

---

## Key Players

| Who | What They Do |
|-----|-------------|
| **Client** | The user or machine that wants access |
| **KDC** | Key Distribution Center — lives on the Domain Controller; the trusted middleman |
| **AS** | Authentication Service — part of KDC; hands out TGTs |
| **TGS** | Ticket-Granting Service — part of KDC; hands out Service Tickets |
| **TGT** | Ticket-Granting Ticket — your "wristband"; proves who you are to the KDC |
| **Service Ticket (ST)** | Your "drink token"; grants access to one specific service |
| **Service / SPN** | The resource you want to reach (file server, web app, etc.) |

---

## The Big Picture

```
                        ┌─────────────────────────┐
                        │   KDC (Domain Controller)│
                        │  ┌──────┐   ┌─────────┐  │
         1. AS-REQ ───► │  │  AS  │   │   TGS   │  │ ◄─── 3. TGS-REQ
         2. AS-REP ◄─── │  │      │   │         │  │ ───► 4. TGS-REP
                        │  └──────┘   └─────────┘  │
                        └─────────────────────────┘
  ┌────────┐                                              ┌─────────┐
  │ Client │ ──────────────── 5. AP-REQ ───────────────► │ Service │
  └────────┘ ◄──────────────── 6. AP-REP ─────────────── └─────────┘
                           (optional — mutual auth)
```

---

## Memorization Cheat Sheet

> **6 steps. 3 actors. Remember: KDC twice, Service once.**

```
 ┌──────────────────────────────────────────────────────────────────┐
 │                                                                  │
 │   CLIENT            KDC (AS)         KDC (TGS)       SERVICE    │
 │     │                  │                  │               │      │
 │     │                  │                  │               │      │
 │  1. │── AS-REQ ───────►│                  │               │      │
 │     │   "Who I am"     │                  │               │      │
 │     │                  │                  │               │      │
 │  2. │◄─ AS-REP ────────│                  │               │      │
 │     │   TGT + Sess.Key │                  │               │      │
 │     │                  │                  │               │      │
 │  3. │── TGS-REQ ───────┼─────────────────►│               │      │
 │     │   TGT + SPN      │                  │               │      │
 │     │                  │                  │               │      │
 │  4. │◄─ TGS-REP ───────┼──────────────────│               │      │
 │     │   Svc Ticket     │                  │               │      │
 │     │   + Svc Sess.Key │                  │               │      │
 │     │                  │                  │               │      │
 │  5. │── AP-REQ ────────┼──────────────────┼──────────────►│      │
 │     │   Svc Ticket     │                  │               │      │
 │     │                  │                  │               │      │
 │  6. │◄─ AP-REP ────────┼──────────────────┼───────────────│      │
 │     │   (optional)     │                  │               │      │
 │     │                  │                  │               │      │
 │     │════════ You're in! Session begins ══════════════════│      │
 │                                                                  │
 └──────────────────────────────────────────────────────────────────┘
```

### The 6 steps in one sentence each

| # | Message | One-liner |
|---|---------|-----------|
| 1 | **AS-REQ** | Client proves identity to KDC with an encrypted timestamp |
| 2 | **AS-REP** | KDC hands back a TGT (opaque) + Session Key (readable) |
| 3 | **TGS-REQ** | Client gives TGT back + asks for a ticket to a specific service |
| 4 | **TGS-REP** | KDC hands back a Service Ticket (opaque) + Service Session Key |
| 5 | **AP-REQ** | Client gives Service Ticket directly to the service |
| 6 | **AP-REP** | Service confirms it decrypted the ticket *(mutual auth only)* |

---

## Phase 1 — Prove Who You Are (AS Exchange)

**Goal:** Get a TGT from the KDC.

### Step 1 › Client → KDC: `AS-REQ`

The client asks the KDC to authenticate it.

```
AS-REQ contains:
  ├── Username          (plaintext)
  └── Encrypted timestamp  (encrypted with the user's password hash)
```

> The password hash is never sent — only a timestamp locked with it. This is called **pre-authentication**.

### Step 2 › KDC → Client: `AS-REP`

The KDC looks up the user's password hash, decrypts the timestamp to verify it's fresh, then replies with two things:

```
AS-REP contains:
  ├── TGT               (encrypted with the krbtgt key — client CANNOT read this)
  └── Session Key       (encrypted with the client's password hash — client CAN read this)
```

The client stores the TGT and Session Key in its **credential cache** (e.g., `klist`).

> TGT default lifetime: **10 hours** in Active Directory.

---

## Phase 2 — Get a Ticket for a Specific Service (TGS Exchange)

**Goal:** Trade your TGT for a Service Ticket to reach a specific resource.

### Step 3 › Client → KDC: `TGS-REQ`

```
TGS-REQ contains:
  ├── TGT               (client hands this back to the KDC)
  ├── Authenticator     (timestamp encrypted with the Session Key)
  └── Target SPN        (e.g., cifs/fileserver.corp.local)
```

The KDC decrypts the TGT with its own `krbtgt` key, retrieves the Session Key inside it, then uses that to verify the Authenticator.

### Step 4 › KDC → Client: `TGS-REP`

```
TGS-REP contains:
  ├── Service Ticket    (encrypted with the service's key — client CANNOT read this)
  └── Service Session Key (encrypted with the client's Session Key — client CAN read this)
```

---

## Phase 3 — Access the Service (AP Exchange)

**Goal:** Prove to the service that you have a valid ticket.

### Step 5 › Client → Service: `AP-REQ`

The client goes directly to the service — no KDC involved here.

```
AP-REQ contains:
  ├── Service Ticket    (still opaque to the client)
  └── Authenticator     (timestamp encrypted with Service Session Key)
```

The service decrypts the ticket with its own key (from its AD machine account), extracts the Service Session Key, and uses it to verify the Authenticator.

### Step 6 › Service → Client: `AP-REP` *(optional)*

If mutual authentication is requested, the service proves it decrypted the ticket by sending back a signed response.

```
AP-REP contains:
  └── Timestamp from the Authenticator (encrypted with Service Session Key)
```

**Both sides are now authenticated. The session begins.**

---

## Full Sequence at a Glance

```
Client                    KDC (AS)          KDC (TGS)              Service
  │                          │                   │                     │
  │──── 1. AS-REQ ──────────►│                   │                     │
  │       username            │                   │                     │
  │       enc. timestamp      │                   │                     │
  │                           │                   │                     │
  │◄─── 2. AS-REP ────────────│                   │                     │
  │       TGT (opaque)        │                   │                     │
  │       Session Key         │                   │                     │
  │                           │                   │                     │
  │──── 3. TGS-REQ ───────────────────────────►   │                     │
  │       TGT + Authenticator │                   │                     │
  │       target SPN          │                   │                     │
  │                           │                   │                     │
  │◄─── 4. TGS-REP ───────────────────────────────│                     │
  │       Service Ticket (opaque)                 │                     │
  │       Service Session Key                     │                     │
  │                                                                     │
  │──── 5. AP-REQ ──────────────────────────────────────────────────►  │
  │       Service Ticket + Authenticator                                │
  │                                                                     │
  │◄─── 6. AP-REP (optional) ───────────────────────────────────────── │
  │       Mutual auth confirmation                                      │
  │                                                                     │
  │═══════════════════════ Authenticated Session ═══════════════════════│
```

---

## Key Security Properties

| Property | How Kerberos Achieves It |
|----------|--------------------------|
| **No password on the wire** | Only hashes are used; the password itself is never transmitted |
| **Mutual authentication** | Both client and service can verify each other |
| **Replay protection** | Timestamps must be within 5 minutes of the KDC clock |
| **Single Sign-On (SSO)** | One TGT gives access to many services without re-entering a password |
| **Least privilege** | Each service ticket is scoped to one specific service |

---

## Active Directory Notes (Common Interview Topics)

| Topic | Key Point |
|-------|-----------|
| **Golden Ticket** | Compromise of `krbtgt` hash lets an attacker forge TGTs for any user |
| **Silver Ticket** | Compromise of a service account hash lets an attacker forge Service Tickets for that service (no KDC contact needed) |
| **Kerberoasting** | Request a service ticket for any SPN, then crack the service account's hash offline |
| **AS-REP Roasting** | If pre-authentication is disabled, anyone can request an AS-REP and crack the hash offline |
| **NTLM fallback** | If no SPN is registered for a service, Windows falls back to NTLM |
| **Ticket lifetimes** | TGT = 10 hrs, max renewal = 7 days, Service Ticket = 10 hrs |
| **Clock skew** | Kerberos requires clocks to be within **5 minutes** of each other (prevents replay) |
