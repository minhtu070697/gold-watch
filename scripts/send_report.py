#!/usr/bin/env python3
"""Send the daily gold report by email over an HTTPS API.

Raw SMTP (ports 25/465/587) is blocked in the Claude Code cloud sandbox, but
outbound HTTPS (443) works, so we deliver mail through a transactional email
API instead. No third-party Python packages required (stdlib only).

Provider is chosen automatically from whichever API key env var is present:
  - RESEND_API_KEY    -> https://api.resend.com   (recommended, simplest)
  - SENDGRID_API_KEY  -> https://api.sendgrid.com

Env vars:
  RESEND_API_KEY / SENDGRID_API_KEY   API key (one is required)
  MAIL_TO     recipient(s), comma-separated   (default: tusvo.dev@gmail.com)
  MAIL_FROM   sender                           (default: onboarding@resend.dev)

Usage:
  python3 scripts/send_report.py --subject "..." --body-file report.txt
  python3 scripts/send_report.py --subject "..." --body-file report.txt --html-file report.html
  echo "body" | python3 scripts/send_report.py --subject "..."
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

DEFAULT_TO = "tusvo.dev@gmail.com"
DEFAULT_FROM = "Gold Watch <onboarding@resend.dev>"


def _post(url, headers, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def send_resend(api_key, sender, recipients, subject, text, html):
    payload = {"from": sender, "to": recipients, "subject": subject, "text": text}
    if html:
        payload["html"] = html
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return _post("https://api.resend.com/emails", headers, payload)


def send_sendgrid(api_key, sender, recipients, subject, text, html):
    content = [{"type": "text/plain", "value": text}]
    if html:
        content.append({"type": "text/html", "value": html})
    payload = {
        "personalizations": [{"to": [{"email": r} for r in recipients]}],
        "from": {"email": sender},
        "subject": subject,
        "content": content,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return _post("https://api.sendgrid.com/v3/mail/send", headers, payload)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body-file", help="plain-text body file (default: stdin)")
    ap.add_argument("--html-file", help="optional HTML body file")
    ap.add_argument("--to", default=os.environ.get("MAIL_TO", DEFAULT_TO))
    ap.add_argument("--from", dest="sender", default=os.environ.get("MAIL_FROM", DEFAULT_FROM))
    args = ap.parse_args()

    if args.body_file:
        with open(args.body_file, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    html = None
    if args.html_file:
        with open(args.html_file, encoding="utf-8") as f:
            html = f.read()

    recipients = [x.strip() for x in args.to.split(",") if x.strip()]

    resend_key = os.environ.get("RESEND_API_KEY")
    sendgrid_key = os.environ.get("SENDGRID_API_KEY")

    if resend_key:
        status, body = send_resend(resend_key, args.sender, recipients, args.subject, text, html)
        provider = "resend"
    elif sendgrid_key:
        status, body = send_sendgrid(sendgrid_key, args.sender, recipients, args.subject, text, html)
        provider = "sendgrid"
    else:
        sys.exit("ERROR: no email API key found. Set RESEND_API_KEY or SENDGRID_API_KEY.")

    ok = 200 <= status < 300
    print(f"[{provider}] HTTP {status} -> {'SENT' if ok else 'FAILED'}: {body[:500]}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
