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
            "enum": ["Safe", "Edgy", "Harsh", "Violation"]
        },
        "reason": {
            "type": "string"
        },
        "think": {
            "type": "string"
        }
    },
    "required": [
        "rating",
        "reason",
        "think"
    ]
}
