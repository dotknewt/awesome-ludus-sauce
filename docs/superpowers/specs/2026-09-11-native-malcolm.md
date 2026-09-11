# Native Malcolm role — approved design

Convert `ansible/roles/role_malcolm_install` from the external ConstructingDefense Debian installer to native, convergent Ansible tasks. The user approved this design and requires public variables prefixed `ludus_install_malcolm_*`. The role directory retains its name.

## Requirements

- Debian 12/13 amd64, using the existing `ludus_install_docker` role dependency.
- Default existing user `debian` and installation directory `/home/debian/Malcolm`; discover real home, UID and primary GID. Append Docker membership, never replace account group memberships.
- Pin Malcolm `v26.08.0`, commit `07bbccdfe2732fb5c5147070cdfca2857b85bacc`; no moving `main`. Reject unsupported version overrides rather than claim arbitrary-version compatibility.
- Native packages, dedicated Python venv, source installation, missing environment-file initialization, host sysctls/resource limits, credentials, certificates, and systemd management. Narrow upstream configuration and bounded lifecycle commands are allowed; no remote Debian installer, shell wrapper, global pip modifications, global sudoers changes, bootloader changes, or ignored failures.
- Preserve existing data, credentials, non-admin htpasswd entries, and valid CAs. Detect existing installations before changing source; incompatible or unidentifiable installations require actionable migration guidance. No automatic upgrades or destructive directory replacement.
- Basic authentication; role password required. Blueprint explicitly retains the existing condef lab credential. Secret tasks hide output and diffs. Persistent backend secrets must survive reruns and partial-install recovery.
- Expose capture enablement, interface, filter, rotation sizes/time, and timeouts. Default capture interface uses the discovered default interface and must exist when capture is enabled. Live capture remains enabled for the PCAP blueprint; avoid duplicate packet storage engines.
- Verify configuration key/value postconditions and Compose validity; exit zero alone is insufficient.
- Native TLS generation must preserve existing valid keys/CAs and repair missing derived artifacts. Fail rather than silently rotate an unrecoverable CA or backend credential after existing initialization.
- Systemd runs as the chosen user with its venv Python, explicit working directory and Docker/network ordering; `Type=oneshot`, `RemainAfterExit=yes`, bounded start/stop and `control.py --start --quiet`. Pull required images before startup. Restart only on relevant changes.
- Verify container health and authenticated `https://127.0.0.1/mapi/ready`, including true processing-ready fields. A systemd active/exited state alone is insufficient.
- Document fresh install, rerun, migration, credential changes, capture, dependencies, and Debian 12/13 VM acceptance checks, including reboot and PCAP ingestion.

## Execution constraints

- Use SDD with explicit `openai/gpt-5.6-sol` for every subagent, launched via `opencode run --model openai/gpt-5.6-sol --agent build` because the native task tool has no model selector.
- User selected an isolated worktree. Implementation worktree: `/tmp/opencode/malcolm-native`, branch `feat/native-malcolm-role`.
- Do not commit, stage, merge, push, deploy a range, or touch unrelated user work. Leave changes available for user review.
- Local validation is permitted in scratch directories. Do not apply host-management tasks to the coding host or change its Docker/systemd configuration.
- Upstream source research is at `/tmp/opencode/malcolm-native-upstream.md`; pinned source checkout at `/tmp/opencode/malcolm-upstream-research`. These are research inputs, not deployed artifacts.
