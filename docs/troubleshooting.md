# Troubleshooting
## Environment Variables
If you're in the local development environment, use `export ISDEV=True && <insert command here>` before most every command. Exporting `ISDEV` causes `sage/config.py` to instantiate the env vars in `.env-example` instead of `.env`. 
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

## Logging
Shows Sage's attempts to parse batches of emails in the MX and insert them as transactions into the DB. 
`~/sage/sage_main.log`

Shows additional errors from when cron invokes Sage.
`~/sage/cron.log`

Shows errors for generating TLS certs.
`/var/log/certbot_cronjob.log`


## Scenarios
### "Ansible gives the error [WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all' or [WARNING]: Could not match supplied host pattern"
- Ensure that the setup script `1_setup_sage_directory.sh` was run using the command `bash setup/1_setup_sage_directory.sh`. 
  - This script creates the populated file `droplet_hosts`, which is read by the ansible playbook.

### "Ansible won't connect to my production server prod!"
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

#### Development
```
telnet localhost 25

ehlo mail.localdomain
mail from: root@localhost
rcpt to: incoming@example.com
data
Subject: Test email 
This is a test email.
.
quit
```

#### Production
```
kfike@pop-os:~$ openssl s_client -starttls smtp -ign_eof -crlf -connect example.com:25
CONNECTED(00000003)
ehlo example.com
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
RCPT TO: <kfike@example.com>
250 2.1.5 Ok
data
354 End data with <CR><LF>.<CR><LF>
Subject: Test email open_ssl 25
Test email open_ssl 25             
.
250 2.0.0 Ok: queued as AA8B54047C
quit
```

### Retrieving Emails
Below are the primary ways `main()` in `sage.mx.get_emails.py` can be called. Some possibilities aren't shown.
The module connects to the dockerized MX that receives the forwarded txn emails.
The entrypoint of Sage, `/sage/__main__.py`, also uses the module `sage.mx.get_emails.py` to retrieve all emails
from the forwarding email.

Retrieve and print all emails. 
```
(.venv) kfike@prod:~/sage$ python3 -c 'from sage.mx import get_emails ; get_emails.main(pls_print=True)'
```

Retrieve and print all emails forwarded by the email associated with the env var `FORWARDING_EMAIL`. 
```
(.venv) kfike@prod:~/sage$ python3 -c 'from sage.mx import get_emails ; get_emails.main(filter="forwarded", pls_print=True)'
```

Retrieve and print all unparsed emails.
```
(.venv) kfike@prod:~/sage$ python3 -c 'from sage.mx import get_emails ; get_emails.main(filter="unparsed", pls_print=True)'
```

Retrieve and print an email by UID.
Below is an example for email UID 77. 
The string must have the syntax below because it's used to identify the filter _and_ integer.
```
(.venv) kfike@prod:~/sage$ python3 -c 'from sage.mx import get_emails ; get_emails.main(filter="uid=77", pls_print=True)'
```

### Getting an mbox file from your Gmail account
For local development, you can use your real forwaded alert emails by downloading an mbox file from your email provider. [Google has instructions on how to get the mbox files from your gmail account.](https://support.google.com/accounts/answer/3024190)

1. Add the mbox file to the directory `docker/mailserver/test_data/real-data/` (gitignored). 
2. Change the environment variable `PRE_LOAD_MBOX`. Note that the MX only loads a single mbox file.
3. Rebuild the MX docker container.
4. Run sage: `python3 -m sage`
5. Verify that the transaction emails were parsed as expected.

### Useful Commands
#### Server
SSH to the server

`ssh root@<ipv4 address> -i ~/.ssh/<private key file>`


#### Postfix

#### Dovecot
Show dovecot errors

`doveadm log errors`


Delete all emails from a mailbox

`doveadm expunge -u incoming mailbox 'INBOX' all`

#### MX Container
Enter the mx container

`docker exec -it sage-mailserver bash`

Copy Postfix and Dovecot Config files to docker/mailserver/configs/ to easily inspect them
```
docker cp sage-mailserver:/etc/postfix/main.cf ./docker/mailserver/configs/postfix_main.cf \
&& docker cp sage-mailserver:/etc/postfix/master.cf ./docker/mailserver/configs/postfix_master.cf \
&& docker cp sage-mailserver:/etc/dovecot/dovecot.conf ./docker/mailserver/configs/dovecot.conf
```

#### Postgres Container
Enter the database container and access the database.

`docker exec -it sage-db psql -h localhost -U postgres sage`


Remove all containers and volumes after a schema change.

`docker rm -f $(docker ps -a -q) && docker volume rm $(docker volume ls -q)`

#### Docker
Show the names of all docker containers (active and inactive)

`docker ps -a --format '{{.Names}}'`


Stop the docker containers

`docker compose down`


Remove all containers

`docker rm -f $(docker ps -a -q)`


Remove all volumes

`docker volume rm $(docker volume ls -q)`


Remove all images

`docker rmi $(docker images -q)`


Access the postgres interactive CLI within the database container

`docker exec -it  sage-db psql -U admin sage`

#### Python
Install dependencies

`(venv) $ python3 -m pip install -r requirements.txt`