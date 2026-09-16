TOOL = {
    "key": "gst",
    "name": "GST",
    "description": "Goods and Services Tax portal login",
    "portal": "https://services.gst.gov.in/services/login",
    "load_wait": 3000,
    "fields": [
        {
            "label": "Username",
            "kind": "username",
            "selectors": ["#username", "input[name='username']"],
        },
        {
            "label": "Password",
            "kind": "password",
            "selectors": [
                "#user_pass",
                "input[name='password']",
                "input[type='password']",
            ],
        },
    ],
    "captcha_selectors": [
        "#captcha",
        "input[id*='captcha' i]",
        "input[name*='captcha' i]",
    ],
}