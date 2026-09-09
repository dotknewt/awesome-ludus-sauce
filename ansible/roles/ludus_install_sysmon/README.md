# README
An Ansible Role that installs, upgrades, and configures Sysmon on Windows Server (2016, 2019, and 2022), Windows 10 and Windows 11.

## Defaults
```yml
---
sysmon_executable_path: 'C:\Windows\Sysmon64.exe'
sysmon_driver_path: 'C:\Windows\SysmonDrv.sys'
sysmon_config_dest: 'C:\Windows\sysmonconfig.xml'
sysmon_drv_reg: '"C:\Windows\Sysmon64.exe" -i -accepteula'
sysmon_config_source: files/sysmonconfig.xml
sysmon_installer_url: https://download.sysinternals.com/files/Sysmon.zip
sysmon_installer_version: 15.15
sysmon_archive_sha256sum: "0EDB284C2157562C15B2EB6F7FB0B3D1752C86DBCE782FD4E5DFEA89B10E4BA6"
sysmon_eventlog_maxsize_gigabyte: 1
```

### Hints

This converts the value of `sysmon_eventlog_maxsize_gigabyte` to bytes 
- `(sysmon_eventlog_maxsize_gigabyte | int * 1024 * 1024 * 1024)`

## Example Ludus Range Config

```yaml
ludus:
  - vm_name: "{{ range_id }}-ad-dc-win2022-server-x64-1"
    hostname: "{{ range_id }}-DC01-2022"
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 11
    ram_gb: 6
    cpus: 4
    windows:
      sysprep: true
    domain:
      fqdn: ludus.domain
      role: primary-dc
    roles:
      - {{ your github username }}.{{ this repo name }}
    role_vars:
      {{ example role var usage }}
```

## License

[//]: # "If you change the License type, be sure to change the actual LICENSE file as well"

GPLv3

## Author Information

This role was created by [{{Your Github Username}}](https://github.com/{{ your github username }}), for [Ludus](https://ludus.cloud/).
