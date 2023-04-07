headscale-acl-sync
==================

**headscale-acl-sync** - syncer that syncs LDAP group entries and applies them
into Headscale's ACL rules.

Installation
------------

headscale-acl-sync requires:

* python 3.x
* jinja2 (https://pypi.org/project/Jinja2/)
* ldap3 (https://pypi.org/project/ldap3/)

Usage
-----

```
./headscale-acl-sync.py -h

usage: headscale-acl-sync.py [-h] [--config CONFIG] [--ldap-uri LDAP_URI] [--ldap-user LDAP_USER] [--ldap-password LDAP_PASSWORD] [--ldap-dn-search LDAP_DN_SEARCH] [--ldap-group-filter LDAP_GROUP_FILTER]
                             [--jinja-template JINJA_TEMPLATE] [--output-file OUTPUT_FILE]

options:
  -h, --help            show this help message and exit
  --config CONFIG       Config file
  --ldap-uri LDAP_URI   LDAP connection URI
  --ldap-user LDAP_USER
                        LDAP BindDN username
  --ldap-password LDAP_PASSWORD
                        LDAP BindDN password
  --ldap-dn-search LDAP_DN_SEARCH
                        LDAP BaseDN search
  --ldap-group-filter LDAP_GROUP_FILTER
                        LDAP group filter
  --jinja-template JINJA_TEMPLATE
                        Jinja2 template file
  --output-file OUTPUT_FILE
                        Output file

```

Create config.yaml (see config.yaml.example) and fill it with actual values.
In LDAP create groups with prefix `headscale_` in name and add to its users.

Next, copy actual ACL file from working configuration of Headscale as
`acls.yaml.jinja2`. Add under `groups` section this code:

```
  # Automated Jinja2 controlled groups begin
{%for group_key, group_value in groups.items() %}
  group:{{ group_key.split("_")[1] }}:
{% for entry in group_value %}
    - {{ entry }}
{% endfor %}

{% endfor %}
  # Automated Jinja2 controlled groups end
```

After first run `headscale-acl-sync` will fill it with groups of actual users
and saves generated file as `acls.yaml`. You can use these groups as ACL
objects below in `acls.yaml.jinja2`.

Use this `acls.yaml` in Headscale config.

Periodic run
------------

Add command into cron like this (runs every 5 minutes):

```
*/5 * * * * /path/to/headscal-acl-sync.py --output-file /etc/headscale/acls.yaml && systemctl restart headscale
```

License
-------

headscale-acl-sync licensed under standard MIT license.
