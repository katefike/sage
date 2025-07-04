# Local Development Troubleshooting

## Environment Variables
**Use `export ISDEV=True && <insert command here>` before most every command.**

Exporting `ISDEV` causes `sage/config.py` to instantiate the env vars in `.env-example` instead of `.env`. 
- The `.env` file is only used when creating prod infrastructure via ansible, or on prod itself. 
- The `.env-example` file is used when doing any local development work. It is used by Docker, pytest and every module of `sage/`.
- If `ISDEV` is not set, you may see the following errors:
```
(.venv) kfike@pop-os:~/Projects/sage$ python3 -m sage
2024-07-30 23:14:15.215 | INFO     | __main__:main:27 - STARTING SAGE
Traceback (most recent call last):
  File "/home/kfike/Projects/sage/sage/mx/get_emails.py", line 66, in open_mailbox
    ENV["RECEIVING_EMAIL_USER"], ENV["RECEIVING_EMAIL_PASSWORD"]
KeyError: 'RECEIVING_EMAIL_USER'
```
```
(.venv) kfike@pop-os:~/Projects/sage$ pytest -xv
ImportError while loading conftest '/home/kfike/Projects/sage/tests/conftest.py'.
tests/conftest.py:21: in <module>
    POSTGRES_HOST = ENV["POSTGRES_HOST"]
E   KeyError: 'POSTGRES_HOST'
```

## MX (Mailserver) Operations
### Send Emails
Test that the dockerized MX works by sending an email locally (i.e. from outside of the MX container). Doing so is different depending on the environment. In production, send via openSSL `s_client` or an email service like Gmail. In development, send via `telnet`. The methods are dependent on environment because your production MX is configured with `smtpd_tls_security_level=encrypt`, which enforces TLS for incoming email (SMTPD).

```
telnet localhost 25

ehlo mail.localdomain
mail from: root@localhost
rcpt to: incoming@localhost
data
Subject: Test email 
This is a test email.
.
quit
```