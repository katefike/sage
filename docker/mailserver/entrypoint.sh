#!/usr/bin/bash

ISDEV=$ISDEV
DOMAIN=${DOMAIN}
HOST=${HOST}

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
# POSTFIX: Config
postconf -e myhostname=${HOST}
postconf -e myorigin=${DOMAIN}
postconf -F '*/*/chroot = n'
echo "$DOMAIN" > /etc/mailname
postconf -e maillog_file=/var/log/mail.log
echo '0 0 * * * root echo "" > /var/log/mail.log' > /etc/cron.d/maillog
# POSTFIX: TLS
if [[ "$ISDEV" = "1" || "$ISDEV" = "yes" || "$ISDEV" = "true" ]]; then
  CRT_FILE=/etc/postfix/certs/${HOST}.crt
  KEY_FILE=/etc/postfix/certs/${HOST}.key
  if [[ -f "${CRT_FILE}" && -f "${KEY_FILE}" ]]; then
    # POSTFIX: TLS in /etc/postfix/main.cf
    postconf -e smtpd_tls_cert_file=${CRT_FILE}
    postconf -e smtpd_tls_key_file=${KEY_FILE}
    postconf -e smtpd_tls_security_level=may
    postconf -e smtp_tls_security_level=may
    # POSTFIX: TLS in /etc/postfix/master.cf
    postconf -M submission/inet="submission   inet   n   -   n   -   -   smtpd"
    postconf -P "submission/inet/syslog_name=postfix/submission"
    postconf -P "submission/inet/smtpd_tls_security_level=encrypt"
  fi
fi
# POSTFIX: Config
# Custom configuration
[[ -f "/postfix_config.sh" ]] && bash /postfix_config.sh

# DOVECOT: Config
# Clear the file contents
:> /etc/dovecot/dovecot.conf
cat >> /etc/dovecot/dovecot.conf <<EOF
protocols = "imap"
disable_plaintext_auth = no
mail_privileged_group = mail
mail_location = maildir:~/Maildir
userdb {
  driver = passwd
}
passdb {
  driver = shadow
}

service auth {
  unix_listener /var/spool/postfix/private/auth {
    group = postfix
    mode = 0660
    user = postfix
  }
}
EOF

# Initialize an email user
useradd -m -s /bin/bash $RECEIVING_EMAIL_USER
{ echo "$RECEIVING_EMAIL_PASSWORD"; echo "$RECEIVING_EMAIL_PASSWORD"; } | passwd $RECEIVING_EMAIL_USER

service postfix reload
service dovecot restart

mkdir /home/incoming/Maildir
# For local development:
# Convert mbox (mb) file to Maildir (md)
# docs found out https://github.com/dovecot/tools/blob/main/mb2md.pl
mb2md -s /home/$RECEIVING_EMAIL_USER/test_data/example_data/transaction_emails_development.mbox -d /home/incoming/Maildir/
# TODO: Create an imap group
chmod -R 777 /home/incoming/Maildir

# DKIM and FAIL2BAN 
[[ -f "/dkim_fail2ban.sh" ]] && bash /dkim_fail2ban.sh

exec "$@"