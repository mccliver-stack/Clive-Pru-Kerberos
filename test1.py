"""
test1.py - Active Directory username lookup helper using Kerberos / LDAP.

Requires:
    pip install ldap3 gssapi

Environment / config:
    AD_SERVER   - LDAP server hostname or IP  (e.g. "dc01.corp.example.com")
    AD_BASE_DN  - Base DN for the search       (e.g. "DC=corp,DC=example,DC=com")

Authentication is attempted in this order:
    1. Kerberos (SASL GSSAPI) – uses the current Kerberos ticket (kinit first).
    2. Simple bind – uses AD_BIND_USER / AD_BIND_PASSWORD env vars when set.
"""

import os
from ldap3 import Server, Connection, SASL, GSSAPI, NTLM, ALL, SIMPLE
from ldap3.core.exceptions import LDAPException


# ---------------------------------------------------------------------------
# Configuration (override via environment variables)
# ---------------------------------------------------------------------------
AD_SERVER   = os.getenv("AD_SERVER",   "dc01.corp.example.com")
AD_BASE_DN  = os.getenv("AD_BASE_DN",  "DC=corp,DC=example,DC=com")
AD_BIND_USER = os.getenv("AD_BIND_USER", "")      # optional fallback
AD_BIND_PASS = os.getenv("AD_BIND_PASSWORD", "")  # optional fallback


def _get_connection() -> Connection:
    """Return an authenticated LDAP connection (Kerberos preferred)."""
    server = Server(AD_SERVER, get_info=ALL)

    # --- Try Kerberos first ---
    try:
        conn = Connection(server, authentication=SASL, sasl_mechanism=GSSAPI)
        if conn.bind():
            return conn
    except (LDAPException, Exception):
        pass  # fall through to simple bind

    # --- Fallback: simple bind with service account credentials ---
    if AD_BIND_USER and AD_BIND_PASS:
        conn = Connection(
            server,
            user=AD_BIND_USER,
            password=AD_BIND_PASS,
            authentication=SIMPLE,
        )
        if conn.bind():
            return conn

    raise ConnectionError(
        "Could not authenticate to AD. "
        "Ensure a valid Kerberos ticket exists (kinit) "
        "or set AD_BIND_USER / AD_BIND_PASSWORD env vars."
    )


def check_username_exists(username: str) -> bool:
    """
    Return True if *username* (sAMAccountName) exists in Active Directory,
    False otherwise.

    Args:
        username: The AD sAMAccountName to look up (e.g. "jsmith").

    Returns:
        bool: True if the account exists, False if not found.

    Raises:
        ConnectionError: If no authenticated connection can be established.
        LDAPException:   On unexpected LDAP errors.
    """
    if not username or not username.strip():
        raise ValueError("username must be a non-empty string")

    # Escape special LDAP filter characters to prevent injection
    safe_username = _escape_ldap_filter(username.strip())

    search_filter = f"(&(objectClass=user)(sAMAccountName={safe_username}))"
    attributes = ["sAMAccountName", "distinguishedName"]

    conn = _get_connection()
    try:
        conn.search(
            search_base=AD_BASE_DN,
            search_filter=search_filter,
            attributes=attributes,
        )
        return len(conn.entries) > 0
    finally:
        conn.unbind()


def _escape_ldap_filter(value: str) -> str:
    """Escape special characters in an LDAP filter value (RFC 4515)."""
    escape_map = {
        "\\": r"\5c",
        "*":  r"\2a",
        "(":  r"\28",
        ")":  r"\29",
        "\0": r"\00",
    }
    for char, escaped in escape_map.items():
        value = value.replace(char, escaped)
    return value
