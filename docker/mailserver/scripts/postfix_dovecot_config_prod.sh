#!/bin/bash
# Configures /etc/postfix/main.cf for production

# Here are the docs on the postconf arguments: https://www.postfix.org/postconf.1.html
CRT_FILE=/etc/letsencrypt/live/prod.${DOMAIN,,}/fullchain.pem
KEY_FILE=/etc/letsencrypt/live/prod.${DOMAIN,,}/privkey.pem

if ![[ -f "${CRT_FILE}" && -f "${KEY_FILE}" ]]; then
    echo "CRITICAL ERROR: Failed to find TLS cert file ${KEY_FILE} or key file ${KEY_FILE}"
fi

# POSTFIX: TLS in /etc/postfix/main.cf
postconf -e smtpd_tls_cert_file=${CRT_FILE}
postconf -e smtpd_tls_key_file=${KEY_FILE}
postconf -e smtpd_tls_security_level=encrypt
# POSTFIX: TLS in /etc/postfix/master.cf
postconf -M submission/inet="submission   inet   n   -   n   -   -   smtpd"
postconf -P "submission/inet/syslog_name=postfix/submission"
postconf -P "submission/inet/smtpd_tls_security_level=encrypt"

# Configures /etc/dovecot/dovecot.conf for production
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
