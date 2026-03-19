"""
check_ad_username.py - CLI tool to check if a username exists in Active Directory.

Usage:
    python check_ad_username.py <username> [<username2> ...]

    # or read from stdin (one username per line)
    echo "jsmith" | python check_ad_username.py

Examples:
    python check_ad_username.py jsmith
    python check_ad_username.py jsmith adoe bwayne

Environment variables (passed through to test1.py):
    AD_SERVER          LDAP server hostname  (default: dc01.corp.example.com)
    AD_BASE_DN         Search base DN        (default: DC=corp,DC=example,DC=com)
    AD_BIND_USER       Service-account UPN   (optional, for simple bind fallback)
    AD_BIND_PASSWORD   Service-account pass  (optional, for simple bind fallback)
"""

import sys

from test1 import check_username_exists


# ANSI colours (disabled automatically when output is not a TTY)
_USE_COLOUR = sys.stdout.isatty()
_GREEN  = "\033[32m" if _USE_COLOUR else ""
_RED    = "\033[31m" if _USE_COLOUR else ""
_YELLOW = "\033[33m" if _USE_COLOUR else ""
_RESET  = "\033[0m"  if _USE_COLOUR else ""


def _check_and_print(username: str) -> bool:
    """Check one username and print a formatted result. Returns True if found."""
    username = username.strip()
    if not username:
        return False

    try:
        found = check_username_exists(username)
        if found:
            print(f"{_GREEN}[FOUND]   {username}{_RESET}")
        else:
            print(f"{_RED}[NOT FOUND] {username}{_RESET}")
        return found
    except ValueError as exc:
        print(f"{_YELLOW}[SKIP]    {username!r} — {exc}{_RESET}")
        return False
    except ConnectionError as exc:
        print(f"{_RED}[ERROR]   Cannot connect to AD: {exc}{_RESET}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"{_RED}[ERROR]   {username!r} — unexpected error: {exc}{_RESET}", file=sys.stderr)
        return False


def main() -> None:
    usernames: list[str] = []

    # Accept usernames from CLI arguments
    if len(sys.argv) > 1:
        usernames = sys.argv[1:]

    # Or from stdin when no arguments are given (pipe / redirect)
    elif not sys.stdin.isatty():
        usernames = [line.strip() for line in sys.stdin if line.strip()]

    else:
        print(
            "Usage: python check_ad_username.py <username> [<username2> ...]\n"
            "       echo 'jsmith' | python check_ad_username.py",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Checking {len(usernames)} username(s) against Active Directory …\n")

    found_count = sum(_check_and_print(u) for u in usernames)

    print(f"\nResult: {found_count}/{len(usernames)} username(s) found in AD.")


if __name__ == "__main__":
    main()
