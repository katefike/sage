FROM ubuntu:20.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt install -y certbot openssl postfix dovecot-core dovecot-imapd mailutils mb2md\ 
    supervisor opendkim opendkim-tools iptables fail2ban cron rsyslog \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/bin/supervisord"]