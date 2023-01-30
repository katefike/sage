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