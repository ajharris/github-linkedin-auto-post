# backend/services/verify_signature.py
import os
import hmac
import hashlib
import logging


def verifyGITHUB_signature(raw_payload: bytes, signature: str) -> bool:
    if not signature:
        logging.warning("[Signature Verification] Missing signature in request.")
        return False

    secret = os.environ.get("SECRET_GITHUB_WEBHOOK_SECRET", "").encode("utf-8")
    expected_signature = (
        "sha256=" + hmac.new(secret, raw_payload, hashlib.sha256).hexdigest()
    )

    if not hmac.compare_digest(expected_signature, signature):
        logging.warning("[Signature Verification] Signature mismatch.")
        return False

    return True
