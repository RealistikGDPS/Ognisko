from __future__ import annotations


from rgdps.utilities.enum import StrEnum

class MessageDirection(StrEnum):
    # NOTE: message direction is relative to the user who is
    # making the request.
    SENT = "sent"
    RECEIVED = "received"
