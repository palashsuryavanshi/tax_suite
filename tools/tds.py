SUBTYPES = [
    {
        "key": "tds",
        "name": "TDS Login",
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
    },
    {
        "key": "traces",
        "name": "TRACES Login",
        "portal": "https://traces.tdscpc.gov.in/auth/login/loginScreen",
        "load_wait": 4000,
        "fields": [
            {
                "label": "Username",
                "kind": "username",
                "selectors": [
                    "#txtLoginId",
                    "input[name*='user' i]",
                    "input[placeholder*='user' i]",
                ],
            },
            {
                "label": "Password",
                "kind": "password",
                "selectors": [
                    "#txtPwd",
                    "input[type='password']",
                ],
            },
        ],
        "captcha_selectors": [
            "#txtCaptcha",
            "input[id*='captcha' i]",
            "input[name*='captcha' i]",
        ],
    },
]

TOOL = {
    "key": "tds",
    "name": "Income Tax TDS",
    "description": "TDS and TRACES portal logins",
    "subtypes": SUBTYPES,
}