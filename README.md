# sage

This app is is like Mint, but better. It collects all of an individual's personal financial data. The data is collected from alert emails sent from your financial institutions. The bank alert emails can be directed to your personal email account, such as a Gmail account. Then setup your account to forward the alert emails to a self-hosted email server. The financial data in the emails is extracted, stored, and made viewable. 

## Usage
1. TBD
2. Create the .env file using .env-example as a template.
3. Start docker:
```bash
$ docker compose up
```

# Useful Commands
## Docker
Copy Postfix and Dovecot Config files to docker/mailserver/configs/ to easily inspect them
```
docker cp sage-mailserver-1:/etc/postfix/main.cf ./docker/mailserver/configs/postfix_main.conf \
&& docker cp sage-mailserver-1:/etc/postfix/master.cf ./docker/mailserver/configs/postfix_master.cf \
&& docker cp sage-mailserver-1:/etc/dovecot/dovecot.conf ./docker/mailserver/configs/dovecot.conf \
```
Show the names of all docker containers (active and inactive)
```
docker ps -a --format '{{.Names}}'
```
Clean restart of Docker
```
docker compose down
```
Removes all containers
```
docker rm -f $(docker ps -a -q)
```
Removes all volumes
```
docker volume rm $(docker volume ls -q)
```
Removes all images
```
docker rmi $(docker images -q)
```
Access the postgres interactive CLI within the database container
```
docker exec -it  sage-db-1 psql -U admin sage
```

## Dovecot
Show dovecot errors
```
doveadm log errors
```

## Postgres
Enter the database container and access the database.
```
docker exec -it sage-db-1 psql -h localhost -U sage_admin sage
```
Remove all containers and volumes after a schema change.
```
docker rm -f $(docker ps -a -q) && docker volume rm $(docker volume ls -q)
```

# Local Development

## Globally Installed Software
- Docker
  - Use [these instructions](https://docs.docker.com/engine/install/) to install 
- Python 3.7 or higher

## Dependencies
```
(venv) $ python3 -m pip install -r requirements.txt
```

## Send Emails Locally
Test that the dockerized email server works by sending an email locally via telnet
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


### Getting mbox files
For local development, you can use your real forwaded alert emails by downloading an mbox file from your email provider. Here's how you get mbox files for a gmail account:
https://support.google.com/accounts/answer/3024190

If mbox files are changed, don't forget to restart the mailserver docker container; the mbox file's emails are loaded into the server on docker compose up when docker/mailserver/entrypoint.sh runs.