# sage

This app is like Mint, but better. It collects all of your personal financial data. The data is collected from alert emails sent from your financial institutions. The bank alert emails can be directed to your personal email account, such as a Gmail account. Then setup your account to forward the alert emails to a self-hosted email server. The financial data in the emails is extracted, stored, and made viewable. 

## Usage
*This app is actively under development. It isn't ready to be used.*
1. Run the production setup script. This will create a .env file using the file .env-example as a template.
`bash scripts/production_setup.sh`
2. Buy a domain name. Add it to the .env file.
3. Create a Digital Ocean API Key. Add it to the .env file.
4. Create SSH keys for the production server. Add it to the .env file.
5. Set up the email account that receives the transaction alert emails to forward all emails to the receiving email address specified in the .env file.
6. Add the forwarding email address to the .env file.
8. Change the app logic to reflect the bank email addresses and regex searches needed to parse your personal transaction data.

# Useful Commands
## Docker
Start the docker containers for the development environment
`docker compose -f docker-compose.yml -f docker-compose.dev.yml up`
Start the docker containers for production
`docker compose -f docker-compose.yml -f docker-compose.prod.yml up`
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

## Mailserver Container
Enter the mailsserver container
`docker exec -it sage-mailserver bash`
Copy Postfix and Dovecot Config files to docker/mailserver/configs/ to easily inspect them
```
docker cp sage-mailserver:/etc/postfix/main.cf ./docker/mailserver/configs/postfix_main.conf \
&& docker cp sage-mailserver:/etc/postfix/master.cf ./docker/mailserver/configs/postfix_master.cf \
&& docker cp sage-mailserver:/etc/dovecot/dovecot.conf ./docker/mailserver/configs/dovecot.conf \
```

### Dovecot
Show dovecot errors
`doveadm log errors`
Delete all emails from a mailbox
`doveadm expunge -u incoming mailbox 'INBOX' all`

## Postgres
Enter the database container and access the database.
`docker exec -it sage-db psql -h localhost -U sage_admin sage`
Remove all containers and volumes after a schema change.
`docker rm -f $(docker ps -a -q) && docker volume rm $(docker volume ls -q)`

# Local Development

## Globally Installed Software
- Docker
  - Use [these instructions](https://docs.docker.com/engine/install/) to install 
- Python 3.7 or higher

## Setting up the Development Environment
1. Run the development setup script.
`bash scripts/setup_development.sh`
2. Start docker
`docker compose -f docker-compose.yml -f docker-compose.override.yml up -d` 

## Python Dependencies
`(venv) $ python3 -m pip install -r requirements.txt`

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

## Testing with pytest
Run the full test suite, stop after the first failure.
`(venv) $ pytest -xv`
See cosde coverage of the Tests
`(venv) $ coverage run --source=sage -m pytest -v tests/ && coverage report -m`

### Getting mbox files
For local development, you can use your real forwaded alert emails by downloading an mbox file from your email provider. Here's how you get mbox files for a gmail account:
https://support.google.com/accounts/answer/3024190

If mbox files are changed, don't forget to restart the mailserver docker container; the mbox file's emails are loaded into the server on docker compose up when docker/mailserver/entrypoint.sh runs.
