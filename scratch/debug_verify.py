import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from api import verify, VerificationRequest

try:
    req = VerificationRequest(
        state="0",
        attack="NONE",
        verifier="Bob",
        shots=1000
    )
    res = verify(req)
    print("SUCCESS:", res)
except Exception as e:
    print("EXCEPTIONS TRACEBACK:")
    traceback.print_exc()
