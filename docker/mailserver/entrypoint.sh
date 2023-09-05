#!/usr/bin/bash

# TLS CERTS: Only run in production
if [[ -f "/letsencrypt.sh" ]]; then
  bash /letsencrypt.sh
  if [[ -f "${CRT_FILE}" && -f "${KEY_FILE}" ]]; then
    if ![[ openssl s_client -connect ${HOST}.${DOMAIN}:993 -starttls smtp | grep -q 'CONNECTED']]; then
      echo 'CRITICAL ERROR: Failed to connect using TLS.'
    fi
  else
    echo 'CRITICAL ERROR: Failed to find TLS cert files.'
  fi
  ufw deny 80
fi

# SUPERVISOR
cat > /etc/supervisor/conf.d/supervisord.conf <<EOF
[supervisord]
nodaemon=true
user=root
EOF

# CRON: Supervisord
cat >> /etc/supervisor/conf.d/supervisord.conf <<EOF
[program:cron]
command=cron -f
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF
# CRON: Config
rm -f /etc/cron.daily/*
rm -f /etc/cron.d/*

# POSTFIX: Supervisord
cat >> /etc/supervisor/conf.d/supervisord.conf <<EOF
[program:postfix]
command=/postfix.sh
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
[program:maillog2stdout]
command=tail -f /var/log/mail.log
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF
cat > /postfix.sh <<'EOF'
#!/bin/bash
trap "postfix stop" SIGINT
trap "postfix stop" SIGTERM
trap "postfix reload" SIGHUP
postfix start
sleep 5
while kill -0 "$(cat /var/spool/postfix/pid/master.pid)"; do
  sleep 5
done
EOF
chmod +x /postfix.sh

# POSTFIX: Send Postfix logs to stdout
postconf -F '*/*/chroot = n'
echo "$DOMAIN" > /etc/mailname
postconf -e maillog_file=/var/log/mail.log
echo '0 0 * * * root echo "" > /var/log/mail.log' > /etc/cron.d/maillog

# POSTFIX: Config common to the dev and prod environments
postconf -e myhostname=$HOST
postconf -e myorigin=$DOMAIN
postconf -e "mydestination = $HOST.$DOMAIN, $DOMAIN, localhost.$DOMAIN, localhost.localdomain, localhost"
postconf -e "home_mailbox = Maildir/"

# POSTFIX/DOVECOT: Config specific to the dev or prod environment
[[ -f "/postfix_dovecot_config.sh" ]] && bash /postfix_dovecot_config.sh

# Set up DKIM and FAIL2BAN (prod only)
[[ -f "/dkim_fail2ban.sh" ]] && bash /dkim_fail2ban.sh

# Initialize an email user
useradd -m -s /bin/bash $RECEIVING_EMAIL_USER
{ echo "$RECEIVING_EMAIL_PASSWORD"; echo "$RECEIVING_EMAIL_PASSWORD"; } | passwd $RECEIVING_EMAIL_USER
service postfix reload
service dovecot restart

# Create the Maildir mailbox
mkdir /home/incoming/Maildir
if [[ -f /home/$RECEIVING_EMAIL_USER/test_data/example_data/transaction_emails.mbox ]]; then
  # Convert mbox (mb) file to Maildir (md)
  # docs found out https://github.com/dovecot/tools/blob/main/mb2md.pl
  mb2md -s /home/$RECEIVING_EMAIL_USER/test_data/example_data/transaction_emails.mbox -d /home/incoming/Maildir/
fi
# TODO: Create an imap group
chmod -R 777 /home/incoming/Maildir

exec "$@"
