FROM odoo:9
MAINTAINER Csaba Palankai <csaba.palankai@gmail.com>

USER root

RUN apt-get update \
    && apt-get install -y python-pip locales \
    && apt-get purge -y  \
    && rm -rf /var/lib/apt/lists/*

RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

# Replace the odoo conf
RUN rm /etc/odoo/openerp-server.conf
RUN ln -s /usr/src/dev/openerp-server.conf \
    /etc/odoo/openerp-server.conf

# Install python packages
ADD /requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Make the complete code available
ADD . /usr/src/

# XMLRPC, XMLRPCS, Longpolling
EXPOSE 8069 8071 8072

USER odoo
