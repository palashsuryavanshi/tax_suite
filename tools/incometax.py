TOOL = {
    "key": "incometax",
    "name": "Income Tax",
    "description": "Income Tax e-filing portal login",
    "portal": "https://eportal.incometax.gov.in/",
    "load_wait": 8000,
    "fields": [
        {
            "label": "User ID",
            "kind": "username",
            "selectors": [
                "#panAdhaarUserId",
                "input[name='panAdhaarUserId']",
                "input[placeholder*='User ID' i]",
            ],
        },
        {
            "label": "Password",
            "kind": "password",
            "selectors": [
                "#loginPasswordField",
                "input[name='loginPasswordField']",
                "#password",
                "input[type='password']",
            ],
        },
    ],
    "advance": {
        "label": "Continue",
        "selectors": [
            "button:has-text('Continue')",
            "text=Continue",
        ],
    },
    "checkbox": {
        "label": "Secure access confirmation",
        "selectors": [
            "#passwordCheckBox-input",
            "input[type='checkbox']",
        ],
    },
    "submit": {
        "label": "Continue",
        "selectors": [
            "button.large-button-primary:has-text('Continue')",
            "button.large-button-primary",
        ],
    },
    "captcha_selectors": [
        "#captcha",
        "input[name='captcha']",
        "input[id*='captcha' i]",
    ],
}