# Roles

## ludus_install_sysmon
optionally specify which config .xml to use from `files/`; default to `sysmonconfig.xml`

## role_gpo_deploy
ansible/roles/role_gpo_deploy/tasks/main.yml is a single big script; "convert" script to ansible using 

## role_malcolm_install
verify or fix installation script funtions on debian 13
replace the docker installation with the `ludus_install_docker` role 
evaluate converting https://github.com/Antonlovesdnb/ConstructingDefense/raw/refs/heads/main/malcolm_debian12_installer.sh to ansible native tasks
