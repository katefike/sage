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
# Removes all containers
docker rm -f $(docker ps -a -q)
# Removes all volumes
docker volume rm $(docker volume ls -q)
docker compose up
# Removes all images
docker rmi $(docker images -q)
```

# Show dovecot errors
```
doveadm log errors
```
# Local Development

## Globally Installed Software
- Docker
  - Use [these instructions](https://docs.docker.com/engine/install/) to install 
- Python 3.7 or higher

## Create a docker-mailserver (DMS) Account
1. Start the docker containers
```bash
$ docker compose up
```
2. Create at least one email account (unless you're using LDAP). You have two minutes to do so, otherwise DMS will shutdown and restart. You can add accounts with tusing the `dms_setup.sh` script:
```bash
$ scripts/dms_setup.sh email add fake_account@example.com
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