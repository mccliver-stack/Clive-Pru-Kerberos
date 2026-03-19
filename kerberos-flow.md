# Kerberos Authentication — Interview Reference

## 30-Second Answer

Kerberos authenticates users without sending passwords over the network. It uses a trusted third party called the KDC to issue tickets. You get a TGT to prove who you are, exchange it for a Service Ticket to reach a specific resource, then present that ticket directly to the service.

---

## 3-Step Explanation

**Step 1 — Get your TGT (prove identity to the KDC)**
You send your username and an encrypted timestamp to the KDC. The KDC verifies it and hands back a Ticket-Granting Ticket (TGT) — your proof of identity — plus a session key you can use to talk to the KDC again.

**Step 2 — Get a Service Ticket (tell the KDC what you want)**
You hand the TGT back to the KDC along with the name of the service you want to reach. The KDC issues a Service Ticket for that specific resource, encrypted with the service's own key.

**Step 3 — Access the service (no KDC involved)**
You take the Service Ticket directly to the service. The service decrypts it with its own key, verifies you, and lets you in. The KDC is out of the picture from this point on.

---

## Key Points to Drop in an Interview

- Passwords never travel the network — only encrypted timestamps and tickets
- The TGT is encrypted with the `krbtgt` key; the client cannot read it
- Each Service Ticket is scoped to one service only
- Timestamps must be within 5 minutes — this prevents replay attacks
- Kerberos enables SSO: one TGT unlocks many services without re-authenticating

---

## Common Attack Names (know these)

- **Golden Ticket** — forging a TGT by stealing the `krbtgt` hash
- **Silver Ticket** — forging a Service Ticket by stealing a service account hash
- **Kerberoasting** — requesting a Service Ticket then cracking the service account hash offline
- **AS-REP Roasting** — cracking a user's hash when pre-authentication is disabled
