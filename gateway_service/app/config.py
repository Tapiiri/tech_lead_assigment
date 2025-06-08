import os

SERVICES = {
    "members": {
        "url": os.getenv("MEMBER_SERVICE_URL", "http://member_service:8001"),
        "prefix": "/api/members",
        "strip_prefix": "/members",
    },
    "feedback": {
        "url": os.getenv("FEEDBACK_SERVICE_URL", "http://feedback_service:8002"),
        "prefix": "/api/feedback",
        "strip_prefix": "/feedback",
    },
}
