# sage

This app is like Mint, but better. It collects all of your personal financial data. The data is collected from alert emails sent from your financial institutions. The bank alert emails can be directed to your personal email account, such as a Gmail account. Then setup your account to forward the alert emails to a self-hosted email server. The financial data in the emails is extracted, stored, and made viewable. 

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
  <br> `FORWARDING_EMAIL`: Set up the email account that receives the transaction alert emails. This account needs to forward all emails to the receiving email address on the mailserver. The default receiving email address is incoming@DOMAIN. So if you purchased the domain example.com, the receiving email address would me incoming@example.com
  <br> `DO_API_TOKEN`: Create a Digital Ocean API Key. It's located in the "API" portion of their menu.
  <br> `PROD_SSH_PUBLIC_KEY`: Create SSH keys for the production server. Ensure the private key permissions are restricted.For help see the section "Production Setup Troubleshooting." Copy/paste the public key here.
  <br> `PROD_SSH_PRIVATE_KEY_FILE_PATH`: Copy/paste the path to the private key file here.
  <br> `SERVER_USER`: Your user the production server.
  <br> `SERVER_USER_PASSWORD`: Your user's password on the production server.
  <br> `SSH_ALLOWED_PUBLIC_IPS`: List the public IPs that can access to the production server.
4. **WARNING: RUNNING THIS SCRIPT CAUSES DIGITAL OCEAN TO START CHARGING YOU MONEY ON A MONTHLY BASIS FOR YOUR PRODUCTION SERVER.**
<br> Run the script to create a production Digital Ocean Droplet server that runs the application.
<br> `bash setup/2_create_SageProd_server.sh`
<br> It will prompt you for `BECOME password:`; enter your sudo password.

## Production Setup Troubleshooting
### "Ansible won't connect to my production server sageProd!"
- Ensure the permissions are correct. Typically the permissions are:
  - `700` on the `.ssh` directory
  - `644` on the public key file (.pub)
  - `600` on the private key file.
- Try to `ssh` from command line. Fill in the public IP from the file `server/ansible/imported_playbooks/droplet_hosts`. Below is the error message given when the permissions on the private key file are too open. 
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
  <br>`bash setup/local_development/1_setup_venv.sh`
4. Start Docker
`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d`

## Testing Methods
### Creating/Deleting an ephemeral server instance
1. **WARNING: RUNNING THIS SCRIPT CAUSES DIGITAL OCEAN TO START CHARGING YOU MONEY ON A MONTHLY BASIS (IF YOU DON'T DELETE THE SERVER).**
<br> Run the script to create a production Digital Ocean Droplet server that runs the application.
<br> `bash setup/local_development/2_create_sageEphem_server.sh`
<br> It will prompt you for `BECOME password:`; enter your sudo password.
2. Run the script to delete the server.
<br> `bash server/setup_scripts/ansible_delete_droplet_ephem.sh`

### Pytest
Run the full test suite, stop after the first failure.

`(venv) $ pytest -xv`


See code coverage of the tests

`(venv) $ coverage run --source=sage -m pytest -v tests/ && coverage report -m`


### Getting mbox files
For local development, you can use your real forwaded alert emails by downloading an mbox file from your email provider. Here's how you get mbox files for a gmail account:
https://support.google.com/accounts/answer/3024190

If mbox files are changed, don't forget to restart the mailserver docker container; the mbox file's emails are loaded into the server on docker compose up when docker/mailserver/entrypoint.sh runs.

# Useful Commands
## Server
SSH to the server

`ssh root@<ipv4 address> -i ~/.ssh/<private key file>`

## Send Emails Locally
Test that the dockerized email server works by sending an email locally (i.e. from outside of the container) via telnet.
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

## Mailserver Container
Enter the mailsserver container

`docker exec -it sage-mailserver bash`

Copy Postfix and Dovecot Config files to docker/mailserver/configs/ to easily inspect them
```
docker cp sage-mailserver:/etc/postfix/main.cf ./docker/mailserver/configs/postfix_main.cf \
&& docker cp sage-mailserver:/etc/postfix/master.cf ./docker/mailserver/configs/postfix_master.cf \
&& docker cp sage-mailserver:/etc/dovecot/dovecot.conf ./docker/mailserver/configs/dovecot.conf
```

### Dovecot
Show dovecot errors

`doveadm log errors`


Delete all emails from a mailbox

`doveadm expunge -u incoming mailbox 'INBOX' all`



## Postgres Container
Enter the database container and access the database.

`docker exec -it sage-db psql -h localhost -U sage_admin sage`


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

## Python Dependencies
`(venv) $ python3 -m pip install -r requirements.txt`
