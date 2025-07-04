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