// vim: ft=asciidoc

= yedit repository
:toc: macro
:toc-title:

toc::[]

== Ansible Role: Yedit

This repository contains an ansible module for modifying yaml files.

I didn't see a good method of editing yaml files and config managing them through ansible.  This is my attempt.

== Install

As `yedit` is not a listed Ansible module, have to install it manually by placing `lib_yaml_editor` directory in a location recognized by Ansible. For details, see http://docs.ansible.com/ansible/latest/index.html[Ansible documentation]:

* http://docs.ansible.com/ansible/devel/playbooks_reuse_roles.html#embedding-modules-and-plugins-in-roles[Embedding Modules and Plugins In Roles]
* http://docs.ansible.com/ansible/latest/intro_configuration.html#module-utils[module_utils]

Alternatively you can install via Ansible Galaxy:

    $ ansible-galaxy install kwoodson.yedit

If you do this, you should also add a `requirements.yml` so other users of your playbook know what dependencies to install:

```yaml
---
- src: kwoodson.yedit
```


== Examples

Sometimes it is necesarry to config manage .yml files.
[source,yaml]
----
- hosts: localhost
  gather_facts: no
  roles:
  - roles/lib_yaml_editor
  tasks:
  - name: manage yaml files
    yedit:
      src: /tmp/test.yaml
      key: a.b.c
      value:
        d:
          e:
            f:
              this is a test

  - name: get a specific value
    yedit:
      src: /tmp/test.yaml
      state: list
      key: a.b.c.d.e.f
    register: yeditout
  - debug: var=yeditout
----

== Documentation

Full documentation is available inline https://github.com/kwoodson/ansible-role-yedit/blob/master/library/yedit.py#L15[here].
