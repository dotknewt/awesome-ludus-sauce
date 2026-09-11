# Native Malcolm Role Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the remote Bash installer with an idempotent, verified Malcolm Ansible role.

**Architecture:** Ansible owns host prerequisites, pinned source, configuration inputs, persistent authentication artifacts and lifecycle. Only narrowly scoped pinned upstream application commands remain. Native tasks repair partial initialization without rotating established secrets or replacing data.

**Tech Stack:** Ansible, Debian 12/13, Docker Compose, Python virtual environments, community.crypto/community.general/ansible.posix where needed, pytest and scratch localhost Ansible behavioral tests.

**Spec:** `docs/superpowers/specs/2026-09-11-native-malcolm.md`

## Global Constraints

- All public variables use `ludus_install_malcolm_*`; retain `ansible/roles/role_malcolm_install` and the existing `ludus_install_docker` dependency.
- Pin `v26.08.0` / `07bbccdfe2732fb5c5147070cdfca2857b85bacc`; Debian 12/13 amd64; basic authentication.
- Use native modules/templates, with narrow upstream configuration/control commands only; command tasks use argv, checked outcomes and explicit working directories.
- Preserve data, secrets, unrelated htpasswd users, and valid CAs on repeat and interrupted runs. Reject unsafe migration and unsupported releases with actionable errors.
- Secrets use no_log and diff suppression. No default admin password in the role; blueprint explicitly supplies its lab password.
- No deployment or system changes to the coding host. Scratch-local tests may exercise production tasks with temporary paths.
- No commits, staging, merges, pushes, or changes outside assigned files except scratch reports/tools. Use apply_patch for edits. No nested subagents.
- Every implementer and reviewer uses explicit `openai/gpt-5.6-sol` via OpenCode CLI. Reviews must return separate spec and quality verdicts.
- Research references: `/tmp/opencode/malcolm-native-upstream.md` and exact pinned checkout `/tmp/opencode/malcolm-upstream-research`.

---

### Task 1: Native prerequisites and pinned installation

**Files:**
- Modify `ansible/roles/role_malcolm_install/defaults/main.yml`.
- Create `ansible/roles/role_malcolm_install/tasks/preflight.yml`, `packages.yml`, `system.yml`, `install.yml`.
- Create `ansible/roles/role_malcolm_install/templates/malcolm-limits.conf.j2`.
- Create `ansible/roles/role_malcolm_install/tests/test_installation.py` and scratch-local behavioral playbooks/helpers only as needed.
- Integration ruling: modify `ansible/roles/ludus_install_docker/defaults/main.yml`, `tasks/main.yml`, and Malcolm `meta/main.yml` to allow Docker user selection (default debian), append supplementary membership, and avoid forcing UID/comment/primary group. Reject source without immutable provenance and never recursively delete an ambiguous partial directory.

**Interfaces:**
- Consumes: gathered Ansible facts and existing Docker dependency.
- Produces public defaults `ludus_install_malcolm_user: debian`, `ludus_install_malcolm_install_dir: /home/debian/Malcolm`, `ludus_install_malcolm_version: v26.08.0`, `ludus_install_malcolm_commit: 07bbccdfe2732fb5c5147070cdfca2857b85bacc`, `ludus_install_malcolm_venv_dir: '{{ ludus_install_malcolm_install_dir }}/.venv'`, `ludus_install_malcolm_admin_username: condef`, `ludus_install_malcolm_admin_password: ''`, capture enablement/interface/filter/rotation and lifecycle timeouts.
- Produces internal facts `_ludus_install_malcolm_home`, `_ludus_install_malcolm_uid`, `_ludus_install_malcolm_gid`, `_ludus_install_malcolm_capture_interface`, plus installed verified source and venv. Keep all internal state prefixed `_ludus_install_malcolm_`.
- No main.yml replacement yet: Task 2 wires these files into the role. Avoid notifications to undefined handlers; Task 2 can add necessary notifications when lifecycle exists.

- [ ] **Step 1:** Read current defaults/meta, Docker dependency, pinned upstream requirements and research. Establish a scratch validation venv under `/tmp/opencode` with Ansible, pytest, YAML/Jinja and required collections. Record exact tools/versions. No preexisting role tests exist; record baseline status.
- [ ] **Step 2:** Add behavioral tests before implementing migration and preflight conditions. At minimum execute real preflight tasks against synthetic facts and scratch directories: unsupported OS/architecture/password fails; supported Debian12/13 reaches source inspection; mismatched or unidentifiable existing installation is rejected without file mutation. Keep tests focused on behavior, not YAML string snapshots.
- [ ] **Step 3:** Implement preflight assertions, account resolution using getent, interface validation, immutable source version guard and safe partial-clone handling. Base rejection messages on actual detected metadata. Do not use service state as an installation proxy.
- [ ] **Step 4:** Implement apt prerequisites and owner Docker access, venv creation and tested pinned Python requirements. Native source acquisition uses exact git commit with existing-source inspection before checkout; no force reset of modified installations. Distinguish role-owned partial initialization from unrelated directories.
- [ ] **Step 5:** Implement native sysctl/resource-limit tasks. Use a dedicated Malcolm sysctl file, relevant documented sysctls (vm.max_map_count 524288, fs.file-max 2097152, vm.overcommit_memory 1, inotify settings, etc.); do not lower tcp_retries2 unless explicitly configured. Scope PAM limits to the role account, with nofile 65535 and memlock unlimited. Do not recursively chown existing data.
- [ ] **Step 6:** Run behavioral tests and syntax/lint appropriate to these files; record red and green results and exact commands in the report. Document any cross-task requirements for service restart notifications and collection dependencies. Leave files uncommitted.

### Task 2: Configuration, authentication, and service convergence

**Files:**
- Replace `ansible/roles/role_malcolm_install/tasks/main.yml`.
- Create `tasks/configure.yml`, `tasks/authentication.yml`, `tasks/service.yml`, and focused included task files for TLS/secrets as necessary in the same role.
- Create `handlers/main.yml` and role templates for managed authentication/configuration inputs.
- Modify `templates/malcolm.service.j2`, `defaults/main.yml`, and Task 1 files only where integration requires.
- Create `tests/test_authentication.py`, `tests/test_configuration.py`, `tests/test_service.py` and behavioral test playbooks/helpers as needed.

**Interfaces:**
- Consumes Task 1 defaults/facts/source/venv and pinned research.
- Produces a complete role with task order `preflight`, `packages`, `system`, `install`, `configure`, `authentication`, `service` and handler `Restart Malcolm`.
- Backend state persists on the managed host, never an ephemeral controller lookup cache. Public defaults retain the mandated prefix.

- [ ] **Step 1:** Read Task 1 report and relevant production files; inspect pinned upstream control/config/auth contracts locally. Write tests exercising real managed auth/config tasks in scratch paths: stable rerun, interrupted initialization, existing secondary htpasswd principal preserved through admin password/name changes, valid CA retained with missing leaf repair, invalid unrecoverable established secret state fails without rotation. Native crypto/htpasswd modules may use target venv dependencies in scratch tests.
- [ ] **Step 2:** Initialize missing config/*.env from release examples only. Apply managed keys natively or with one conditional `scripts/install.py --configure true --non-interactive --load-existing-env true` pass and `--extra` overrides. Validate actual values and ensure changed input or missing artifacts retries configuration. Basic auth, runtime/profile, UID/GID, capture interface/filter/rotation, and single capture storage engine must match inputs. Preserve unknown config and secret values.
- [ ] **Step 3:** Manage backend secret keys in `netbox-secret.env`, `postgres.env`, `valkey.env`, `arkime-secret.env` and `.opensearch.primary.curlrc` natively. Keep per-key persistent state and adopt established valid values without overwrite. Generate missing values only for genuinely uninitialized state. Handle placeholders from release examples. Never write one coarse completion marker that prevents recovery of missing derived files.
- [ ] **Step 4:** Manage admin crypt hash in auth.env and bcrypt htpasswd natively, with newline-delimited records, preserving other principals. Generate/reuse suitable salts on host; password change must converge once. Manage required LDAP/metadata placeholders without overwriting existing content. Apply no_log and diff:false to sensitive operations and validate semantic postconditions without exposing values.
- [ ] **Step 5:** Use native community.crypto tasks for web TLS and forwarding CA/server/client certs. Preserve valid keys/CAs and existing valid trust sets; regenerate only missing/recoverable derived objects. Generate required DH parameters and Logstash-compatible private key formats. Validate key/certificate pairs and required bind sources. Do not use upstream destructive auth generators.
- [ ] **Step 6:** Validate `docker compose --file <dir>/docker-compose.yml --profile malcolm config` and expected image tags without disclosing secrets. Pull required images idempotently (community.docker compose pull module or actual missing-image inspection), with bounded operation. Service unit uses venv Python, explicit args, `--quiet true`, Docker/network dependencies, Type=oneshot/RemainAfterExit, working directory, user/group, startup and stop timeouts; no unconditional reload/restart. Flush appropriate restart handler before readiness.
- [ ] **Step 7:** Verify enabled service and expected running container health plus authenticated `/mapi/ready` true fields `opensearch`, `pcap_monitor`, `logstash_lumberjack`, `logstash_pipelines` with configurable bounded retries. Self-signed local endpoint probe may disable certificate verification only for this documented localhost readiness probe.
- [ ] **Step 8:** Run task tests and syntax/lint; exercise actual upstream configurator in a scratch copy with the actual produced configuration if feasible, without host install or Docker changes. Record red/green evidence, skipped VM-dependent checks and dependency requirements. Leave files uncommitted.

### Task 3: Blueprint, documentation, and verification integration

**Files:**
- Update `ansible/roles/role_malcolm_install/README.md`.
- Update `blueprints/constructing-defense/requirements.yml`, `range-config.yml`, `TODO.md`.
- Create role `tests/requirements.txt`, collection requirements, test runner documentation and VM acceptance playbook(s) as needed.
- Production edits only to resolve concrete integration issues, with covering tests and explicit report.

**Interfaces:**
- Consumes complete role and Task 1/2 reports.
- Produces documented, reproducible local validation and explicit Debian12/13 VM acceptance procedure.

- [ ] **Step 1:** Load ludus-range-config skill before editing the blueprint. Set pcap role_vars `ludus_install_malcolm_admin_username: condef`, `ludus_install_malcolm_admin_password: 'Temp1234!!'`, `ludus_install_malcolm_capture_enabled: true`; explain this as the existing lab credential. Preserve all other VM settings.
- [ ] **Step 2:** Declare every used collection in appropriate requirements with compatible minimum versions and document controller/target dependencies. Keep the existing Docker role dependency and do not duplicate its implementation.
- [ ] **Step 3:** Replace scaffold README with exact variable/default reference, pin policy, migration/adoption instructions that preserve data, credential rotation semantics, rerun/partial-recovery behavior, capture-interface behavior, service readiness, and troubleshooting commands that do not print secrets. Update TODO accurately: native conversion complete; live Debian compatibility remains unverified until tested.
- [ ] **Step 4:** Provide runnable local suite commands and a VM-only acceptance playbook/checklist covering Debian12 and13, install, second-run convergence, secret fingerprints, admin update retaining a secondary principal, interrupted recovery, reboot and small PCAP ingestion. Do not run deployment tasks against the coding host and do not claim unexecuted acceptance checks passed.
- [ ] **Step 5:** Run all meaningful local tests and complete role syntax/lint checks using scratch dependencies. Validate all advertised public variable names and blueprint YAML. Report exact commands/output and remaining live acceptance requirements. Leave files uncommitted.
