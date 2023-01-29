#!/usr/bin/bash

ISDEV=${ISDEV}
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
if [[ "${ISDEV}" = "1" || "${ISDEV}" = "yes" || "${ISDEV}" = "true" ]]; then
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
[[ -f "/configure.sh" ]] && bash /configure.sh

# DKIM: Supervisord
KEY_FILES=$(find /etc/opendkim/domainkeys -iname *.private)
if [[ -n "${KEY_FILES}" ]]; then
cat >> /etc/supervisor/conf.d/supervisord.conf <<EOF
[program:opendkim]
command=/usr/sbin/opendkim -f
[program:rsyslog]
command=/usr/sbin/rsyslogd -n
[program:syslog2stdout]
command=tail -f /var/log/syslog
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF

# DKIM: Postfix filter config in /etc/postfix/main.cf
postconf -e milter_protocol=2
postconf -e milter_default_action=accept
postconf -e smtpd_milters=inet:localhost:12301
postconf -e non_smtpd_milters=inet:localhost:12301
# DKIM: Config
cp -n /etc/opendkim.conf /etc/opendkim.conf.orig
cp /etc/opendkim.conf.orig /etc/opendkim.conf
cat >> /etc/opendkim.conf <<EOF
AutoRestart             Yes
AutoRestartRate         10/1h
UMask                   002
Syslog                  yes
SyslogSuccess           Yes
LogWhy                  Yes
Canonicalization        relaxed/simple
ExternalIgnoreList      refile:/etc/opendkim/TrustedHosts
InternalHosts           refile:/etc/opendkim/TrustedHosts
KeyTable                refile:/etc/opendkim/KeyTable
SigningTable            refile:/etc/opendkim/SigningTable
Mode                    sv
PidFile                 /var/run/opendkim/opendkim.pid
SignatureAlgorithm      rsa-sha256
UserID                  opendkim:opendkim
Socket                  inet:12301@localhost
EOF
cp -n /etc/default/opendkim /etc/default/opendkim.orig
cp /etc/default/opendkim.orig /etc/default/opendkim
cat >> /etc/default/opendkim <<EOF
SOCKET="inet:12301@localhost"
EOF
cat > /etc/opendkim/TrustedHosts <<EOF
127.0.0.1
localhost
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
${DOMAIN}
EOF
DKIM_FILE=/etc/opendkim/domainkeys/mail.private
cat > /etc/opendkim/KeyTable <<EOF
mail._domainkey.${DOMAIN} ${DOMAIN}:mail:${DKIM_FILE}
EOF
cat > /etc/opendkim/SigningTable <<EOF
*@${DOMAIN} mail._domainkey.${DOMAIN}
EOF
for kf in ${KEY_FILES}; do
if [[ "${kf}" != "${DKIM_FILE}" ]]; then
  kfn="${kf##*._domainkey.}"
  DKIM_DOMAIN="${kfn%.private}"
  kfs="${kf%%._domainkey.*}"
  DKIM_SELECTOR="${kfs##*/}"
  echo "${DKIM_DOMAIN}" >> /etc/opendkim/TrustedHosts
  echo "${DKIM_SELECTOR}._domainkey.${DKIM_DOMAIN} ${DKIM_DOMAIN#\*.}:${DKIM_SELECTOR}:${kf}" >> /etc/opendkim/KeyTable
  echo "*@${DKIM_DOMAIN} ${DKIM_SELECTOR}._domainkey.${DKIM_DOMAIN}" >> /etc/opendkim/SigningTable
fi
done
chown opendkim:opendkim /etc/opendkim/domainkeys
chmod 770 /etc/opendkim/domainkeys
chown opendkim:opendkim ${KEY_FILES}
chmod 400 ${KEY_FILES}
echo '0 0 * * * root echo "" > /var/log/syslog' > /etc/cron.d/syslog
fi

# FAIL2BAN: Supervisord
if [[ -n "${FAIL2BAN}" ]]; then
cat >> /etc/supervisor/conf.d/supervisord.conf <<EOF
[program:fail2ban]
command=fail2ban-server -f -x -v start
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF
echo '[Definition]
logtarget = STDOUT' > /etc/fail2ban/fail2ban.d/log2stdout.conf
echo '[postfix-sasl]
enabled = true' > /etc/fail2ban/jail.d/defaults-debian.conf
[[ -n "${FAIL2BAN_BANTIME}" ]] && echo "bantime = ${FAIL2BAN_BANTIME}" >> /etc/fail2ban/jail.d/defaults-debian.conf
[[ -n "${FAIL2BAN_FINDTIME}" ]] && echo "findtime = ${FAIL2BAN_FINDTIME}" >> /etc/fail2ban/jail.d/defaults-debian.conf
[[ -n "${FAIL2BAN_MAXRETRY}" ]] && echo "maxretry = ${FAIL2BAN_MAXRETRY}" >> /etc/fail2ban/jail.d/defaults-debian.conf
mkdir -p /run/fail2ban
echo '1 0 * * * root echo "Log truncated at $(date +\%s)" > /var/log/mail.log' > /etc/cron.d/maillog
fi
# Rsyslogd does not start fix
rm -f /var/run/rsyslogd.pid

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

exec "$@"