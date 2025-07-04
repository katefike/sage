# Troubleshooting
Troubleshooting advice here is applicable in both local and prod. If you don't see what you're looking for, it may be in the env specific [local troubleshooting](docs/local_troubleshooting.md) or [prod troubleshooting](docs/prod_troubleshooting.md) files.

## Logging
Shows Sage's attempts to parse batches of emails in the MX and insert them as transactions (txns) into the DB. 
`~/sage/sage_main.log`

## _Help!_ Scenarios
### _"Help! Ansible gives the error [WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all' or [WARNING]: Could not match supplied host pattern"_
- Ensure that the setup script `1_setup_sage_directory.sh` was run using the command `bash setup/1_setup_sage_directory.sh`. 
  - This script creates the populated file `droplet_hosts`, which is read by the ansible playbook.

## MX (Mailserver) Operations
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

### Useful Commands
#### Postfix

#### Dovecot
Show dovecot errors
`doveadm log errors`


Delete all emails from a mailbox
`doveadm expunge -u incoming mailbox 'INBOX' all`

#### MX Container
Enter the mx container
`docker exec -it sage-mx bash`

Copy Postfix and Dovecot Config files to docker/mx/configs/ to easily inspect them
```
docker cp sage-mx:/etc/postfix/main.cf ./docker/mx/configs/postfix_main.cf \
&& docker cp sage-mx:/etc/postfix/master.cf ./docker/mx/configs/postfix_master.cf \
&& docker cp sage-mx:/etc/dovecot/dovecot.conf ./docker/mx/configs/dovecot.conf
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