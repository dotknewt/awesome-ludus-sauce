# Template Name Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize noncanonical template basenames and all exact consumer references to Ludus's template naming grammar.

**Architecture:** Treat each affected template basename as one identifier propagated through its directory, Packer entrypoint, Packer source label, built `vm_name`, and consuming YAML. Rename all coupled filesystem and HCL identifiers together, leaving installer and provisioning semantics unchanged.

**Tech Stack:** Packer HCL, YAML, Python 3 naming validator, Git.

**Spec:** `docs/superpowers/specs/2026-09-10-template-name-migration-design.md`

## Global Constraints

- Use lowercase ASCII letters, digits, hyphens, and dots only; never underscores in canonical template basenames.
- Windows client names use `windows-<release>-<arch>[-<qualifier>...]-<locale>`; Server names use `windows-server-<release>-<arch>[-<qualifier>...]-<locale>`.
- Preserve the evidenced `enterprise`, genuine `tpm`, and `no-security-updates` qualifiers, as well as `no` and `us` locale tokens.
- The top-level `.pkr.hcl` basename equals its directory basename; `vm_name` equals that basename plus exactly one `-template` suffix.
- Preserve all template behavior and do not add compatibility aliases.
- Update only exact old full-basename references.
- Run the naming validator on each basename and built template name, then confirm every old full basename has no repository matches.

---

### Task 1: Normalize Template Identifiers

**Files:**
- Rename: `templates/windows-11_22h2-x64-enterprise-no/` to `templates/windows-11-22h2-x64-enterprise-no/`
- Rename: `templates/windows-11_23h2-x64-enterprise-no/` to `templates/windows-11-23h2-x64-enterprise-no/`
- Rename: `templates/windows-11_24h2-x64-enterprise-tpm-no/` to `templates/windows-11-24h2-x64-enterprise-tpm-no/`
- Rename: `templates/windows-11_24h2-x64-enterprise-tpm-us/` to `templates/windows-11-24h2-x64-enterprise-tpm-us/`
- Rename: `templates/windows-11_25h2-x64-enterprise-no/` to `templates/windows-11-25h2-x64-enterprise-no/`
- Rename: `templates/windows-11_25h2-x64-enterprise-us/` to `templates/windows-11-25h2-x64-enterprise-us/`
- Rename: `templates/windows-server-2019-x64-no_security_updates-no/` to `templates/windows-server-2019-x64-no-security-updates-no/`
- Rename: `templates/flare-vm-no/flare-vm.pkr.hcl` to `templates/flare-vm-no/flare-vm-no.pkr.hcl`
- Modify: the seven renamed top-level `.pkr.hcl` files
- Modify: `blueprints/constructing-defense/range-config.yml:91,109`

**Interfaces:**
- Consumes: the legacy template identifiers currently used by the Packer files and blueprint.
- Produces: canonical basenames and corresponding `<basename>-template` built names.

- [ ] **Step 1: Establish the failing naming baseline**

Run the naming validator on each legacy basename and its built name. For example:

```bash
python3 .opencode/skills/ludus-template-naming/scripts/validate_template_name.py \
  windows-11_22h2-x64-enterprise-no \
  windows-11_22h2-x64-enterprise-no-template
```

Expected: each underscore-containing Windows basename fails syntax validation.

- [ ] **Step 2: Rename directories and top-level Packer files**

Use `git mv` for the seven listed template directories. Within each renamed
directory, rename its top-level `.pkr.hcl` file to exactly the new directory
basename plus `.pkr.hcl`. Rename `flare-vm.pkr.hcl` to `flare-vm-no.pkr.hcl`.

- [ ] **Step 3: Update Packer and YAML identifiers**

In each renamed Windows Packer file, replace only its old full basename in the
`vm_name` default, `source "proxmox-iso"` label, and `build.sources` value.
Set the `vm_name` default to the new basename with exactly one `-template`
suffix. Replace both blueprint references with
`windows-11-22h2-x64-enterprise-no-template`.

- [ ] **Step 4: Verify canonical names and Packer formatting**

Run the validator for every new basename and built name. Run `packer fmt -check`
against all eight renamed Packer files. Run `packer validate` against those
files if the installation and required Packer variables are available; report
any environmental blockers rather than changing template behavior to bypass
them.

- [ ] **Step 5: Verify no legacy references remain**

Search the complete repository for each old full basename. Confirm no matches
remain, directory and top-level `.pkr.hcl` basenames match, and only
`flare-vm-no-template` is used as the FLARE built name.

- [ ] **Step 6: Commit**

```bash
git add templates blueprints/constructing-defense/range-config.yml
git commit -m "chore: normalize template names"
```
```
