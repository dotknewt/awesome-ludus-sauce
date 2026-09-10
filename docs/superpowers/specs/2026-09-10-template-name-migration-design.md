# Template Name Migration Design

## Goal

Normalize all noncanonical Ludus template names and exact consuming references
to the repository's `ludus-template-naming` grammar without changing template
semantics.

## Scope

Rename the following template basenames:

| Old basename | New basename |
| --- | --- |
| `windows-11_22h2-x64-enterprise-no` | `windows-11-22h2-x64-enterprise-no` |
| `windows-11_23h2-x64-enterprise-no` | `windows-11-23h2-x64-enterprise-no` |
| `windows-11_24h2-x64-enterprise-tpm-no` | `windows-11-24h2-x64-enterprise-tpm-no` |
| `windows-11_24h2-x64-enterprise-tpm-us` | `windows-11-24h2-x64-enterprise-tpm-us` |
| `windows-11_25h2-x64-enterprise-no` | `windows-11-25h2-x64-enterprise-no` |
| `windows-11_25h2-x64-enterprise-us` | `windows-11-25h2-x64-enterprise-us` |
| `windows-server-2019-x64-no_security_updates-no` | `windows-server-2019-x64-no-security-updates-no` |

Rename `templates/flare-vm-no/flare-vm.pkr.hcl` to
`templates/flare-vm-no/flare-vm-no.pkr.hcl` so its top-level Packer filename
matches the existing directory basename. `flare-vm-no` remains a named FLARE
environment rather than an OS-shaped template name.

For every OS-shaped rename, update the template directory, top-level
`.pkr.hcl` filename, Packer source identifier, build source reference, and
the `vm_name` default. The final built name is the normalized basename plus
one `-template` suffix. Update the two `constructing-defense` blueprint
references to the normalized Windows 11 22H2 built name.

## Semantic Evidence

All `-no` templates use `InputLocale` `nb-NO` in their `Autounattend.xml`
files. Both `-us` templates use `InputLocale` `en-US`. The 24H2 templates
contain a `tpm_config` device block, so their `tpm` qualifier is retained.
The 2019 Server template's disabled-update provisioner establishes its
`no-security-updates` qualifier. Windows 11 templates retain their
`enterprise` qualifier.

## Constraints

- Preserve locale, role, edition, architecture, release, provisioners, and
  hardware settings.
- Do not add compatibility aliases.
- Do not modify unrelated worktree changes from the source checkout.
- Validate both each basename and its final `-template` name with
  `ludus-template-naming/scripts/validate_template_name.py`.
- Search the complete repository for each old full basename after the rename;
  no occurrences may remain.
- Run `packer fmt -check` and `packer validate` for each renamed Packer file
  when the local Packer installation and required variables allow it.
