#!/usr/bin/env python

from argparse import ArgumentParser
from jinja2 import Template
from ldap3 import ALL, Connection, Server
import os.path
import yaml


class LDAPSync:

    def __init__(self, **options):
        self.options = options
        self.server = Server(self.options["ldap_uri"], get_info=ALL)
        self.connection = Connection(self.server, user=self.options["ldap_user"],
                                     password=self.options["ldap_password"], auto_bind="DEFAULT")
        self.groups = {}

    def ldap_get_groups(self):
        groups = {}
        try:
            self.connection.bind()
            self.connection.search(self.options["ldap_dn_search"], self.options["ldap_group_filter"], attributes="cn")
            result_groups = self.connection.entries
            for group in result_groups:
                groups[group.cn.value] = []

                self.connection.search(self.options["ldap_dn_search"],
                                       f"(&{self.options['ldap_user_filter']}(memberof={group.entry_dn}))",
                                       attributes=["mail"])
                members = self.connection.entries

                for member in members:
                    groups[group.cn.value].append(member.mail.value)
            self.connection.unbind()
        except Exception as e:
            print(f"Cannot bind to {self.options['ldap_uri']}: {e}!")

        return groups

    def prepare_acls(self, groups):
        with open(self.options["jinja_template"]) as file_:
            template = Template(file_.read(), trim_blocks=True)

        context = {
            "groups": groups,
        }
        with open(self.options["output_file"], mode="w", encoding="utf-8") as results:
            results.write(template.render(context))
        print(f"{self.options['output_file']} successfully written.")

        return

    def run(self):
        groups = self.ldap_get_groups()
        if len(groups) == 0:
            return 1
        self.prepare_acls(groups)

        return 0


def main(*args: str) -> int:

    parser = ArgumentParser()
    parser.add_argument("--config", help="Config file", type=str, required=False, default="config.yaml")
    parser.add_argument("--ldap-uri", help="LDAP connection URI", type=str, required=False, default="ldap://localhost")
    parser.add_argument("--ldap-user", help="LDAP BindDN username", type=str, required=False, default="cn=admin")
    parser.add_argument("--ldap-password", help="LDAP BindDN password", type=str, required=False, default="Password")
    parser.add_argument("--ldap-dn-search", help="LDAP BaseDN search", type=str, required=False,
                        default="dc=example,dc=com")
    parser.add_argument("--ldap-group-filter", help="LDAP group filter", type=str, required=False,
                        default="(objectClass=ipausergroup)")
    parser.add_argument("--ldap-user-filter", help="LDAP user filter", type=str, required=False,
                        default="(objectClass=person)")
    parser.add_argument("--jinja-template", help="Jinja2 template file", type=str, required=False,
                        default="acls.yaml.jinja2")
    parser.add_argument("--output-file", help="Output file", type=str, required=False, default="acls.yaml")
    args = parser.parse_args()

    opt = vars(args)
    if not os.path.exists(args.config):
        yaml.dump(opt, open(args.config, "w"), Dumper=yaml.Dumper)
    args = yaml.load(open(args.config), Loader=yaml.FullLoader)
    opt.update(args)
    args = opt

    return LDAPSync(**args).run()


if __name__ == '__main__':
    exit(main())

