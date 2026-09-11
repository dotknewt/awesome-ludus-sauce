# ludus_install_docker

Installs Docker Engine, the Docker CLI, containerd, Buildx, and Compose from
the official Docker Debian repository. The role also creates the `docker`
group, sets the Ludus `debian` account (UID 1000) to use it as its primary
group, and enables and starts the Docker service.

## Requirements

- Debian with an APT release recognized by Docker's Debian repository.
- Ansible with `ansible.builtin.deb822_repository` support (Ansible Core 2.15
  or later).
- Facts gathered, so `ansible_distribution_release` is available.
- Privilege escalation (`become: true`).

## Role Variables

This role has no configurable variables. The `debian` account is the Ludus
account and is intentionally managed directly.

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Install Docker on a Ludus Debian VM
  hosts: docker_hosts
  become: true
  gather_facts: true
  roles:
    - ludus_install_docker
```

## License

GPLv3
