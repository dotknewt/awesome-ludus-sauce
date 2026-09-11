# Awesome Ludus Source
Add: `ludus source add https://github.com/dotknewt/awesome-ludus-sauce.git --id awesome-ludus-sauce --force` 
Apply a blueprint: `ludus blueprint apply awesome-ludus-sauce/constructing-defense --target-range condef`

## Configure the host packet capture bridge

Once the range bridge exists, run the [host playbook](ludus-configure-bridge.yaml)
from the repository root **on the single-node Ludus/Proxmox host**, with Ansible installed:

```sh
sudo ansible-playbook ludus-configure-bridge.yaml -e range_second_octet=3
```

Replace `3` with your range's numeric `range_second_octet` allocation (1–254),
not its textual range ID. This example selects `vmbr1003` (`1000 + 3`).
The playbook runs locally on the host, enables promiscuous mode, sets bridge
ageing time to `0`, and installs a persistent interface-up hook to reapply those
settings. The bridge must already exist.

See the [bridge role documentation](ansible/roles/ludus_configure_bridge/README.md)
for host prerequisites and the hook retirement procedure.
