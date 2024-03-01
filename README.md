# sage

This app is like Mint, but better. It collects all of your personal financial data. The data is collected from alert emails sent from your financial institutions. The bank alert emails can be directed to your personal email account, such as a Gmail account. Then setup your account to forward the alert emails to a self-hosted mail server. The financial data in the emails is extracted, stored, and made viewable. 

Thank you @nhopkinson and @whosgonna for their ongoing feedback on this project.

## Production Setup Instructions
*This app is actively under development. It isn't ready to be used.*

1. Globally install the following software:
  <br> Python 3.7 or higher
2. Run the first setup script. This will create a .env file using the file .env-example as a template. 
  <br>`bash setup/1_setup_sage_directory.sh`
3. Define the following environment variables in the .env file:
  <br> `ISDEV`: Change to "False"
  <br> `DOMAIN`: Buy a domain name.
  <br> `FORWARDING_EMAIL`: Set up the email account that receives the transaction alert emails. This account needs to forward all emails to the receiving email address on the mail server. The default receiving email address is incoming@DOMAIN. So if you purchased the domain example.com, the receiving email address would me incoming@example.com
  <br> `DO_API_TOKEN`: Create a Digital Ocean API Key. It's located in the "API" portion of their menu.
  <br> `PROD_SSH_PUBLIC_KEY`: Create SSH keys for the production server. Ensure the private key permissions are restricted.For help see the section "Production Setup Troubleshooting." Copy/paste the public key here.
  <br> `PROD_SSH_PRIVATE_KEY_FILE_PATH`: Copy/paste the path to the private key file here.
  <br> `SERVER_USER`: Your user the production server.
  <br> `SERVER_USER_PASSWORD`: Your user's password on the production server.
  <br> `SSH_ALLOWED_PUBLIC_IPS`: List the public IPs that can access to the production server.
4. **WARNING: RUNNING THIS SCRIPT CAUSES DIGITAL OCEAN TO START CHARGING YOU MONEY ON A MONTHLY BASIS FOR YOUR PRODUCTION SERVER.**
<br> Run the script to create a production Digital Ocean Droplet server that runs the application.
<br> `bash setup/2_create_prod_server.sh`
<br> If an error occurs, go to Digital Ocean and delete the Droplet and firewall before running the script again.
<br> It will prompt you for `BECOME password:`; enter your sudo password.
4. Run the script to configure the production Digital Ocean Droplet server.
<br> `bash setup/3_configure_prod_server.sh`
<br> This script is idempotent: no matter how many times you run it, the result will be the same. So if an error occurs, simply troubleshoot and run the script again until the error is resolved.


# Troubleshooting
## Logging
Shows email parsing info and errors.

`~/sage/sage_main.log`

Shows cron job info errors.

`~/sage/cron.log`


Shows cron errors in the case that it fails to execute a job.

`sudo tail /var/log/syslog`


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


# Local Development
## Setup Instructions
1. Globally install the following software:
  - Docker
    - Use [these instructions](https://docs.docker.com/engine/install/) to install 
  - Python 3.7 or higher
2. Run the first setup script. This will create a .env file using the file .env-example as a template. 
  <br>`bash setup/1_setup_sage_directory.sh`
3. Run a setup script for setting up the virtual environment and Python dependencies.
  <br>`source setup/local_development/1_setup_venv.sh`
4. Start Docker
`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d`
5. Manually kick off the script to parse transactions from emails. Execute the command from the project root. For example, if the project is located in `/home/kfike/Projects/` then execute `(.venv) kfike@pop-os:~/Projects/sage$ python3 -m sage`. 


### Creating/Deleting an ephemeral server instance
1. **WARNING: RUNNING THIS SCRIPT CAUSES DIGITAL OCEAN TO START CHARGING YOU MONEY ON A MONTHLY BASIS (IF YOU DON'T DELETE THE SERVER).**
<br> Run the script to create an ephemeral Digital Ocean Droplet server that runs the application. The server is emphemeral in that it is intended to be created and deleted rapidly.
<br> `bash setup/local_development/2_create_sageEphem_server.sh`
<br> It will prompt you for `BECOME password:`; enter your sudo password.
2. Run the script to configure the server.
<br> `bash setup/local_development/3_configure_sageEphem_server.sh`
3. Run the script to delete the server.
<br> `bash server/setup_scripts/ansible_delete_droplet_ephem.sh`

### Pytest
Run the full test suite, stop after the first failure. Docker must be started for pytests to be successful.

`(venv) $ pytest -xv`


See code coverage of the tests

`(venv) $ coverage run --source=sage -m pytest -v tests/ && coverage report -m`

## Mailserver Container
Enter the mailserver container

`docker exec -it sage-mailserver bash`

Copy Postfix and Dovecot Config files to docker/mailserver/configs/ to easily inspect them
```
docker cp sage-mailserver:/etc/postfix/main.cf ./docker/mailserver/configs/postfix_main.cf \
&& docker cp sage-mailserver:/etc/postfix/master.cf ./docker/mailserver/configs/postfix_master.cf \
&& docker cp sage-mailserver:/etc/dovecot/dovecot.conf ./docker/mailserver/configs/dovecot.conf
```

## Send Emails Locally 
Test that the dockerized mail server works by sending an email locally (i.e. from outside of the mail server container). Doing so is different depending on the environment. In production, send via openSSL `s_client` or an email service like Gmail. In development, send via `telnet`. TThe methods are dependent on environment because your production MX is configured with `smtpd_tls_security_level=encrypt`, which enforces TLS for incoming email (SMTPD).

### Development
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

### Production
```
kfike@pop-os:~$ openssl s_client -starttls smtp -ign_eof -crlf -connect prod.example.dev:25
CONNECTED(00000003)
ehlo prod.example.devdepth=2 C = US, O = Internet Security Research Group, CN = ISRG Root X1
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
RCPT TO: <kfike@prod.example.dev>
250 2.1.5 Ok
data
354 End data with <CR><LF>.<CR><LF>
Subject: Test email open_ssl 25
Test email open_ssl 25             
.
250 2.0.0 Ok: queued as AA8B54047C
quit
```

### Retrieving emails 
Retrieve emails on your MX in development (locally) and production (on the DO droplet host). 
```(.venv) kfike@prod:~/sage$ python3 scripts/get_all_emails.py 
UID: 1
Date: 1900-01-01 00:00:00
To: ()
From: 
Text: Test email open_ssl 25

UID: 2
Date: 2024-03-01 09:45:23+07:00
To: ('kfike@prod.example.dev',)
From: example@gmail.com
Text: Test email gmail 25

2 emails were retrieved.

```

### Getting mbox files from your Gmail account
For local development, you can use your real forwaded alert emails by downloading an mbox file from your email provider. [Google has instructions on how to get the mbox files from your gmail account.](https://support.google.com/accounts/answer/3024190)

If mbox files are changed, don't forget to restart the mail server docker container; the mbox file's emails are loaded into the server on docker compose up when docker/mailserver/entrypoint.sh runs.

# Useful Commands
## Server
SSH to the server

`ssh root@<ipv4 address> -i ~/.ssh/<private key file>`


### Dovecot
Show dovecot errors

`doveadm log errors`


Delete all emails from a mailbox

`doveadm expunge -u incoming mailbox 'INBOX' all`



## Postgres Container
Enter the database container and access the database.

`docker exec -it sage-db psql -h localhost -U postgres sage`


Remove all containers and volumes after a schema change.

`docker rm -f $(docker ps -a -q) && docker volume rm $(docker volume ls -q)`

## Docker
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

## Python
Install dependencies

`(venv) $ python3 -m pip install -r requirements.txt`
