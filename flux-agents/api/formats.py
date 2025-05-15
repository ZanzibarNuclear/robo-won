response_format = {
    "type": "object",
    "properties": {
        "reply": {
            "type": "string"
        }
    },
    "required": [
        "reply"
    ]
}

rating_format = {
    "type": "object",
    "properties": {
        "rating": {
            "type": "string",
            "enum": ["safe", "edgy", "strong", "naughty"]
        },
        "reason": {
            "type": "string"
        }
    },
    "required": [
        "rating",
        "reason"
    ]
}
