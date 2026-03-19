# ADFS Authentication: Full Flow Between Active Directory, ADFS, and Entra ID

## Overview

Active Directory Federation Services (ADFS) acts as a bridge between on-premises identity infrastructure (Active Directory) and cloud identity providers (Microsoft Entra ID, formerly Azure AD). This document covers the complete authentication flow including token issuance, federation trust, and Single Sign-On (SSO) mechanics.

---

## Core Components

| Component | Role |
|-----------|------|
| **Active Directory (AD DS)** | On-premises identity store; holds user accounts, groups, and Kerberos tickets |
| **ADFS** | Federation server; issues security tokens (SAML, OAuth, WS-Federation) based on AD identities |
| **Entra ID (Azure AD)** | Cloud identity provider; federates with ADFS to extend on-premises identities to cloud services |
| **Web Application Proxy (WAP)** | Reverse proxy that publishes ADFS endpoints externally |
| **Relying Party (RP)** | Application or service that trusts and consumes tokens issued by ADFS |

---

## Authentication Protocols Supported by ADFS

- **WS-Federation** — used by SharePoint, older Microsoft apps
- **SAML 2.0** — used for third-party SaaS federation
- **OAuth 2.0 / OpenID Connect (OIDC)** — used by modern apps and Entra ID
- **Kerberos / NTLM** — used internally to authenticate users against AD

---

## Token Types

### 1. Kerberos Ticket (AD Layer)
- Issued by the **Key Distribution Center (KDC)** in Active Directory
- Used for internal network authentication
- Contains: user principal name (UPN), group memberships, session key
- Lifetime: typically 10 hours (configurable via Group Policy)

### 2. SAML Token (ADFS Layer)
- XML-based security assertion
- Issued by ADFS after validating the user's AD identity
- Contains **claims**: identity attributes mapped from AD (UPN, groups, email, custom attributes)
- Signed with ADFS token-signing certificate
- Types:
  - **Authentication assertion** — confirms user was authenticated
  - **Attribute assertion** — carries user attributes as claims
  - **Authorization assertion** — conveys access decisions

### 3. OAuth 2.0 / JWT Tokens (ADFS / Entra ID Layer)
- **Access Token** — short-lived (typically 1 hour); grants access to a resource
- **ID Token** — identity token used in OIDC flows; contains user claims
- **Refresh Token** — long-lived; used to obtain new access tokens without re-authentication

---

## Federation Trust: ADFS ↔ Entra ID

Entra ID and ADFS establish a **federated domain** relationship configured via Azure AD Connect or manual federation setup.

```
On-Premises                          Cloud
┌─────────────────┐                 ┌──────────────────────┐
│  Active          │                 │  Entra ID (Azure AD)  │
│  Directory       │◄───────────────►│                      │
│  (AD DS)         │  Azure AD       │  Federated Domain     │
└────────┬─────────┘  Connect Sync   │  (contoso.com)        │
         │                           └──────────┬───────────┘
         ▼                                      │ Federation
┌─────────────────┐  Federation Trust           │ Metadata /
│  ADFS           │◄────────────────────────────┘ WS-Federation
│  Federation     │   (Token-signing cert,          Endpoint
│  Server         │    metadata endpoint)
└─────────────────┘
```

### Federation Trust Setup
1. **Azure AD Connect** syncs user objects from AD to Entra ID (hash sync or pass-through)
2. The domain (e.g., `contoso.com`) is configured as **Federated** in Entra ID
3. ADFS publishes a **federation metadata endpoint** (`/FederationMetadata/2007-06/FederationMetadata.xml`)
4. Entra ID retrieves the ADFS **token-signing certificate** from this metadata
5. When a user with a federated UPN signs in to Entra ID, authentication is **redirected to ADFS**

---

## Complete Authentication Flow: Browser SSO to a Cloud App

This flow describes a user on a domain-joined machine signing in to a Microsoft 365 or Entra ID-protected application.

```
User Browser          ADFS                  Active Directory       Entra ID          Cloud App
     │                  │                          │                   │                  │
     │ 1. Access App    │                          │                   │                  │
     │─────────────────────────────────────────────────────────────────────────────────►│
     │                  │                          │                   │                  │
     │ 2. Redirect to Entra ID login               │                   │                  │
     │◄────────────────────────────────────────────────────────────────│                  │
     │                  │                          │                   │                  │
     │ 3. Entra ID detects federated domain        │                   │                  │
     │    Redirect to ADFS (WS-Fed/SAML endpoint)  │                   │                  │
     │─────────────────►│                          │                   │                  │
     │                  │                          │                   │                  │
     │ 4. ADFS checks for existing Kerberos ticket │                   │                  │
     │    (Windows Integrated Auth / NTLM)         │                   │                  │
     │                  │──────────────────────────►                   │                  │
     │                  │   Validate Kerberos/NTLM │                   │                  │
     │                  │◄──────────────────────────                   │                  │
     │                  │   AD confirms identity    │                   │                  │
     │                  │                          │                   │                  │
     │ 5. ADFS issues SAML token with claims       │                   │                  │
     │◄─────────────────│                          │                   │                  │
     │                  │                          │                   │                  │
     │ 6. Browser POSTs SAML token to Entra ID     │                   │                  │
     │─────────────────────────────────────────────────────────────────►                  │
     │                  │                          │                   │                  │
     │ 7. Entra ID validates SAML token signature  │                   │                  │
     │    Issues Entra ID access token + ID token  │                   │                  │
     │◄────────────────────────────────────────────────────────────────│                  │
     │                  │                          │                   │                  │
     │ 8. Access token presented to Cloud App      │                   │                  │
     │─────────────────────────────────────────────────────────────────────────────────►│
     │                  │                          │                   │                  │
     │ 9. Cloud App validates token, grants access │                   │                  │
     │◄────────────────────────────────────────────────────────────────────────────────│
```

### Step-by-Step Detail

#### Step 1-2: Initial Access and Entra ID Redirect
- User navigates to a cloud app (e.g., Microsoft 365, custom app registered in Entra ID)
- App redirects to Entra ID's authorization endpoint
- Entra ID receives the user's UPN hint or tenant domain

#### Step 3: Home Realm Discovery (HRD)
- Entra ID checks the user's domain (e.g., `user@contoso.com`)
- If `contoso.com` is a **federated domain**, Entra ID redirects to the ADFS endpoint:
  ```
  https://adfs.contoso.com/adfs/ls/?client-request-id=...&pullStatus=0&wa=wsignin1.0&wtrealm=urn:federation:MicrosoftOnline&wctx=...
  ```
- The `wtrealm` parameter identifies Entra ID as the relying party

#### Step 4: ADFS Authenticates Against Active Directory
- ADFS receives the WS-Federation sign-in request
- On domain-joined machines (intranet zone), ADFS attempts **Windows Integrated Authentication**:
  - **Kerberos**: Browser automatically presents Kerberos Service Ticket for the ADFS SPN (`HTTP/adfs.contoso.com`)
  - **NTLM fallback**: Used when Kerberos is not available
- On external/non-domain-joined machines:
  - ADFS presents a **forms-based login page**
  - Credentials validated against AD via LDAP or Kerberos

#### Step 5: ADFS Issues SAML Token
ADFS constructs a SAML 2.0 assertion containing **claims** mapped from AD attributes:

```xml
<saml:Assertion>
  <saml:AttributeStatement>
    <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn">
      <saml:AttributeValue>user@contoso.com</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="http://schemas.microsoft.com/ws/2008/06/identity/claims/groups">
      <saml:AttributeValue>Domain Users</saml:AttributeValue>
    </saml:Attribute>
    <!-- Additional claims -->
  </saml:AttributeStatement>
</saml:Assertion>
```

The assertion is **signed** with the ADFS token-signing certificate (private key) and optionally **encrypted** for the relying party.

#### Step 6: SAML Token Posted to Entra ID
- Browser receives an HTML auto-submit form (HTTP POST binding)
- SAML response is POSTed to Entra ID's consumer endpoint:
  ```
  https://login.microsoftonline.com/login.srf
  ```

#### Step 7: Entra ID Validates and Issues Tokens
- Entra ID verifies the SAML assertion's **XML signature** using the ADFS token-signing certificate (obtained from federation metadata)
- Validates: issuer, audience, timestamps (NotBefore, NotOnOrAfter), signature
- Matches the incoming UPN claim to the synced user object in Entra ID
- Issues:
  - **ID Token** (JWT) — for the client application
  - **Access Token** (JWT) — for the target resource (e.g., Microsoft Graph)
  - **Refresh Token** — for session continuity

#### Step 8-9: Application Access
- Application receives the access token (via authorization code exchange or direct)
- Validates the token's signature, audience (`aud` claim), and expiration
- Grants access based on claims (roles, groups, scopes)

---

## SSO Session Management

### On-Premises SSO (ADFS)
- ADFS creates a **persistent SSO cookie** (`MSISAuthenticated`) after first authentication
- Cookie lifetime configurable (default: session-based; persistent up to 7 days)
- Subsequent requests to ADFS-protected apps skip re-authentication
- SSO cookie is tied to the ADFS server (or farm via shared DKM key in AD)

### Cloud SSO (Entra ID)
- Entra ID issues a **Primary Refresh Token (PRT)** to Entra ID-joined or hybrid-joined devices
- PRT is stored securely in the device's TPM (via Windows Hello for Business)
- Used to silently obtain access tokens for cloud apps without prompting the user
- **Seamless SSO** (Azure AD Connect feature): Entra ID automatically issues a Kerberos ticket to domain-joined machines via a computer account (`AZUREADSSOACC`) in AD, enabling silent cloud sign-in

### SSO Token Lifetime Summary

| Token | Default Lifetime | Configurable |
|-------|-----------------|--------------|
| Kerberos TGT | 10 hours | Yes (GPO) |
| ADFS SAML Assertion | 1 hour | Yes (ADFS rules) |
| ADFS SSO Cookie | 8 hours (session) / 7 days (persistent) | Yes |
| Entra ID Access Token | 1 hour | Yes (Token Lifetime Policy) |
| Entra ID Refresh Token | 90 days (inactive) / 365 days max | Yes |
| Primary Refresh Token (PRT) | 14 days (renewable) | Limited |

---

## Claims Transformation Pipeline

ADFS uses **Claims Rules** to transform AD attributes into claims for each relying party:

```
Active Directory Attribute Store
        │
        ▼
┌───────────────────────────┐
│  Acceptance Transform     │  ← Rules applied when claims enter ADFS
│  Rules (Incoming Claims)  │
└───────────────┬───────────┘
                │
                ▼
┌───────────────────────────┐
│  Issuance Transform       │  ← Rules applied per Relying Party Trust
│  Rules (Outgoing Claims)  │
└───────────────┬───────────┘
                │
                ▼
┌───────────────────────────┐
│  Issuance Authorization   │  ← Rules that permit or deny token issuance
│  Rules                    │
└───────────────────────────┘
```

Example claims rule (ADFS rule language):
```
// Send UPN as NameIdentifier
c:[Type == "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn"]
=> issue(Type = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",
         Issuer = c.Issuer,
         Value = c.Value);

// Send group membership
c:[Type == "http://schemas.microsoft.com/ws/2008/06/identity/claims/groups",
   Value =~ "^Domain Admins$"]
=> issue(Type = "http://schemas.microsoft.com/ws/2008/06/identity/claims/role",
         Value = "Admin");
```

---

## Hybrid Identity: Azure AD Connect Sync

Azure AD Connect synchronizes on-premises objects to Entra ID and configures federation:

```
On-Premises AD                                    Entra ID
─────────────────────────────────────────────────────────────
User: user@contoso.com  ──── Object Sync ────►  User: user@contoso.com
  ├── sAMAccountName                               ├── userPrincipalName
  ├── mail                                         ├── mail
  ├── objectGUID (sourceAnchor) ────────────────►  ├── onPremisesImmutableId
  └── pwdHash (optional) ────────────────────────► └── passwordHash (for fallback)
```

### Sync Modes
| Mode | Description | Password Writeback |
|------|-------------|-------------------|
| **Password Hash Sync (PHS)** | Syncs password hashes to Entra ID; cloud auth possible without ADFS | Supported |
| **Pass-Through Authentication (PTA)** | Entra ID delegates auth to on-premises agent; no ADFS required | Supported |
| **Federation (ADFS)** | All authentication redirected to ADFS; Entra ID never validates passwords | Supported |

---

## Security Considerations

### Certificate Management
- ADFS uses two certificates: **token-signing** and **token-decryption**
- Certificates must be rotated before expiry; Entra ID must be updated with new certificates
- Auto-certificate rollover is supported (self-signed certs); manual update required for CA-issued certs

### Token Validation Requirements
Applications and relying parties must validate:
- **Signature**: Verify using issuer's public key/certificate
- **Issuer (`iss`)**: Must match expected ADFS or Entra ID issuer URL
- **Audience (`aud`)**: Must match the application's identifier
- **Expiration (`exp`)**: Token must not be expired
- **Not Before (`nbf`)**: Token must not be used before this time
- **Nonce**: Replay attack prevention (OIDC flows)

### Common Attack Vectors and Mitigations
| Attack | Mitigation |
|--------|-----------|
| Token replay | Short token lifetimes; nonce validation |
| SAML signature wrapping | Use strict XML canonicalization; validate signature covers entire assertion |
| Credential stuffing | Entra ID Smart Lockout; ADFS Extranet Lockout |
| Pass-the-ticket (Kerberos) | Privileged Access Workstations; Protected Users group |
| Token theft | Continuous Access Evaluation (CAE); PRT binding to device |

---

## Troubleshooting Common Issues

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Loop between Entra ID and ADFS | HRD misconfiguration | Verify federated domain settings in Entra ID |
| ADFS returns `MSIS7012` | Relying Party Trust not found | Check RP trust identifier matches `wtrealm` |
| Kerberos fails, NTLM fallback | SPN not registered or firewall blocking port 88 | Register `HTTP/adfs.contoso.com` SPN; open UDP/TCP 88 |
| Token signing cert mismatch | ADFS cert rolled over; Entra ID not updated | Run `Update-MsolFederatedDomain` or re-run Azure AD Connect |
| Claims missing in token | Claims rules not configured for RP | Add issuance transform rules in ADFS Management Console |
| SSO not working from external | WAP not publishing ADFS endpoints | Verify WAP proxy trust and published endpoints |

---

## Key Endpoints Reference

| Endpoint | URL Pattern | Protocol |
|----------|-------------|----------|
| ADFS Federation Metadata | `https://adfs.domain.com/FederationMetadata/2007-06/FederationMetadata.xml` | WS-Federation |
| ADFS WS-Federation Sign-in | `https://adfs.domain.com/adfs/ls/` | WS-Federation |
| ADFS SAML SSO | `https://adfs.domain.com/adfs/ls/IdpInitiatedSignOn.aspx` | SAML 2.0 |
| ADFS OAuth Token | `https://adfs.domain.com/adfs/oauth2/token` | OAuth 2.0 |
| ADFS OAuth Authorize | `https://adfs.domain.com/adfs/oauth2/authorize` | OAuth 2.0 |
| ADFS OpenID Config | `https://adfs.domain.com/adfs/.well-known/openid-configuration` | OIDC |
| Entra ID Authorization | `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize` | OAuth 2.0 / OIDC |
| Entra ID Token | `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token` | OAuth 2.0 |
| Entra ID Federation Metadata | `https://login.microsoftonline.com/{tenant}/federationmetadata/2007-06/federationmetadata.xml` | WS-Federation |

---

## Summary

The ADFS authentication chain establishes a trust hierarchy that allows on-premises Active Directory identities to be seamlessly used in cloud environments:

1. **Active Directory** issues Kerberos tickets to authenticated domain users
2. **ADFS** validates those tickets and issues standards-based tokens (SAML, JWT) with configurable claims
3. **Entra ID** trusts ADFS as an identity provider for federated domains, validates inbound SAML tokens, and re-issues OAuth 2.0/OIDC tokens for cloud resources
4. **SSO** is maintained through a combination of Kerberos (intranet), ADFS session cookies, Entra ID refresh tokens, and Primary Refresh Tokens (PRT) on managed devices

This layered federation model enables organizations to maintain on-premises identity governance while providing seamless access to cloud services without requiring users to maintain separate credentials.
