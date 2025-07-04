# Prod Troubleshooting
## Logging
Shows additional errors from when cron invokes Sage.
`~/sage/cron.log`

Shows errors for generating TLS certs.
`/var/log/certbot_cronjob.log`

## _Help!_ Scenarios
### _"Help! Ansible won't connect to my production server prod!"_
- Ensure the permissions are correct. Typically the permissions are:
  - `700` on the `.ssh` directory
  - `644` on the public key file (.pub)
  - `600` on the private key file.
- Try to `ssh` from command line. Fill in the public IP from the file `ansible/imported_playbooks/droplet_hosts`. Below is the error message given when the permissions on the private key file are too open. 
```
(.venv) kfike@cutie:~/.ssh$ ssh root@< public ip >  -i ~/.ssh/sage_prod
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0664 for '/home/kfike/.ssh/sage_prod' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "/home/kfike/.ssh/sage_prod": bad permissions
root@< public ip >: Permission denied (publickey).
```

## MX (Mailserver) Operations
### Send Emails Locally 
Test that the dockerized MX works by sending an email locally (i.e. from outside of the MX container). Doing so is different depending on the environment. In production, send via openSSL `s_client` or an email service like Gmail. In development, send via `telnet`. The methods are dependent on environment because your production MX is configured with `smtpd_tls_security_level=encrypt`, which enforces TLS for incoming email (SMTPD).

#### Production
```
kfike@pop-os:~$ openssl s_client -starttls smtp -ign_eof -crlf -connect localhost:25
CONNECTED(00000003)
ehlo localhost
depth=2 C = US, O = Internet Security Research Group, CN = ISRG Root X1
verify return:1
depth=1 C = US, O = Let's Encrypt, CN = R3
[...]
---
SSL handshake has read 2945 bytes and written 437 bytes
---
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
[...]
---
250 SMTPUTF8
---
Post-Handshake New Session Ticket arrived:
SSL-Session:
    Protocol  : TLSv1.3
[...]
---
read R BLOCK
[...]
250-prod

MAIL FROM: <support@port25.com>
250 2.1.0 Ok
RCPT TO: <kfike@localhost>
250 2.1.5 Ok
data
354 End data with <CR><LF>.<CR><LF>
Subject: Test email open_ssl 25
Test email open_ssl 25             
.
250 2.0.0 Ok: queued as AA8B54047C
quit
```