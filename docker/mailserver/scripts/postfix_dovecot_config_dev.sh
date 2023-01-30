#!/bin/bash
# This script configures /etc/postfix/main.conf and /etc/postfix/master.cf
# Here are the docs on the postconf arguments: https://www.postfix.org/postconf.1.html

# Diable TLS for delivering mail (Inbound/SMTP)
postconf -# "smtp_tls_CApath"
postconf -# "smtp_tls_security_level"
postconf -# "smtp_tls_session_cache_database"
# Diable TLS/SASL for  for receiving mail (Outbound/SMTPD)
postconf -# "smtpd_tls_cert_file"
postconf -# "smtpd_tls_key_file"
postconf -# "smtpd_tls_security_level"
postconf -# "smtpd_relay_restrictions"

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