# Disaster Recovery
Use this disaster recovery guide to create a brand new Sage deployment without losing all the MX and DB data on your existing deployment.

## Applicable Scenarios
- There has been unauthorized root access to your server because of a security misconfiguration, Digital Ocean breach, your private key was leaked, etc. 
- There's a bug in your production Sage deployment and you wan't to redeploy from scratch as your last-ditch-effort. 

## Semi-Applicable Scenarios
- You want to change your public IP.
    - This is semi-applicable because the disaster recovery proces described here retains your public IP. When the Digital Ocean Droplet was created, it was assigned a reserved IP (AKA floating IP) that can be transfered to a new Droplet. However, at a specific step in the process, you have the ability to change the reserved IP to a new one. 

## Steps
1. In Digital Ocean's console, turn off the droplet.
2. In Digital Ocean's console, detach the two volumes from the original droplet.
3. In Digital Ocean's console, detach the reserved IP from the original droplet.
4. In Digital Ocean's console, take a final snapshot of the original droplet.
5. In Digital Ocean's console, delete the droplet and the firewall.
6. Locally, create a new droplet. Run `bash setup/2_create_prod_server.sh`
7. You now have two reserved IPs in Digital Ocean. In Digital Ocean's console, unassign and delete the new one.
8. In Digital Ocean's console, assign the existing reserved IP to the new droplet.
9. In Digital Ocean's console, attach the volumes to the new droplet. IMPORTANT NOTE: when a volume is attached to a droplet, Digital Ocean provides steps for mounting the volumes. These steps can't be done until `setup/setup/3_configure_prod_server.sh` has been run.
10. Verify that the local `.env` has the correct values for prod
11. Run `bash setup/3_configure_prod_server.sh`
12. Circle back to the instructions Digital Ocean provided for mounting each volume. SSH to the Droplet and execute the commands Digital Ocean provided. The commands should look similar to this:
Create a mount point for your volume:
```
mkdir -p /mnt/sage_db
mkdir -p /mnt/sage_mailserver
```
Mount your volume at the newly-created mount point:
```
sudo mount -o discard,defaults,noatime /dev/disk/by-id/scsi-0DO_Volume_sage-db /mnt/sage_db
mount -o discard,defaults,noatime /dev/disk/by-id/scsi-0DO_Volume_sage-mailserver /mnt/sage_mailserver
```
Change fstab so the volume will be mounted after a reboot
```
echo '/dev/disk/by-id/scsi-0DO_Volume_sage-db /mnt/sage_db ext4 defaults,nofail,discard 0 0' | sudo tee -a /etc/fstab
echo '/dev/disk/by-id/scsi-0DO_Volume_sage-mailserver /mnt/sage_mailserver ext4 defaults,nofail,discard 0 0' | sudo tee -a /etc/fstab
```
TODO: Create and mount Digital Ocean volumes during automated production deployment https://github.com/katefike/sage/issues/145
13. Re-run `bash setup/3_configure_prod_server.sh` so that Sage is started using the mounts.
14. Send a test email. Verify it was received and all your existing emails are still there by SSH'ing to the Droplet and getting all emails: 
```
(.venv) kfike@prod:~/sage$ python3 -c 'from sage.mx import get_emails ; get_emails.main(pls_print=True)'
```
15. While SSH'd to the droplet, verify that all your existing transactions are there. Connect to the DB by running `docker exec -it  sage-db psql -U <POSTGRES_USER> sage` and executing the query `SELECT * FROM transactions;` `POSTGRES_USER` is an environment variable specified in your `.env`.