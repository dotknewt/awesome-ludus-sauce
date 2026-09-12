from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys

import pytest
import yaml

from helpers import ANSIBLE_PLAYBOOK, ROLE_DIR


VM_POWER = ROLE_DIR / "tasks" / "vm_power.yml"


def _run_power(tmp_path: Path, variables=None):
    inventory = tmp_path / "inventory.yml"
    inventory.write_text(yaml.safe_dump({"all": {"hosts": {
        "pcap": {"ansible_host": "192.0.2.1", "ansible_connection": "ssh",
                 "ansible_ssh_common_args": "-o ConnectTimeout=1", **(variables or {})},
        # Deliberately different ID: delegation must retain the guest's ID.
        "localhost": {"ansible_connection": "local", "ansible_become": False, "proxmox_vmid": 118},
    }}}), encoding="utf-8")
    playbook = tmp_path / "power.yml"
    playbook.write_text(yaml.safe_dump([{
        "name": "Exercise power check with an unreachable guest",
        "hosts": "pcap", "gather_facts": False,
        "tasks": [{"ansible.builtin.include_tasks": str(VM_POWER)}],
    }]), encoding="utf-8")
    return subprocess.run(
        [str(ANSIBLE_PLAYBOOK), "-i", str(inventory), str(playbook)],
        env={**os.environ, "ANSIBLE_NOCOLOR": "1",
             "ANSIBLE_LOCAL_TEMP": str(tmp_path / ".ansible-local")},
        text=True, capture_output=True, check=False, timeout=60,
    )


def _proxmox(tmp_path: Path, state: str, *, fail_start: bool = False):
    # Replace only the external Proxmox CLI; execute the real Ansible tasks.
    state_file = tmp_path / "vm-state"
    state_file.write_text(state, encoding="utf-8")
    cli = tmp_path / "pvesh"
    cli.write_text(
        f"#!{sys.executable}\n"
        "import json, pathlib, sys\n"
        f"state = pathlib.Path({str(state_file)!r})\n"
        "args = sys.argv[1:]\n"
        "if args == ['get', '/cluster/resources', '--type', 'vm', '--output-format', 'json']:\n"
        # Cluster resource status can lag behind the node's live status.
        "    print(json.dumps([{'vmid': 117, 'type': 'qemu', 'node': 'pve2', 'status': 'stopped'},\n"
        "                      {'vmid': 118, 'type': 'qemu', 'node': 'pve1', 'status': 'stopped'}]))\n"
        "elif args == ['create', '/nodes/pve2/qemu/117/status/start']:\n"
        "    if state.read_text() == 'running':\n"
        "        sys.exit('VM already running')\n"
        f"    if {fail_start!r}:\n"
        "        sys.exit('VM is locked')\n"
        "    state.write_text('running')\n"
        "    print('UPID:pve2:test')\n"
        "elif args == ['get', '/nodes/pve2/qemu/117/status/current', '--output-format', 'json']:\n"
        "    print(json.dumps({'status': state.read_text()}))\n"
        "else:\n"
        "    sys.exit('Unexpected Proxmox command: ' + repr(args))\n",
        encoding="utf-8",
    )
    cli.chmod(0o755)
    return state_file, {
        "proxmox_vmid": 117,
        "_ludus_install_malcolm_pvesh_command": str(cli),
    }


def test_running_vm_is_unchanged(tmp_path: Path) -> None:
    state, variables = _proxmox(tmp_path, "running")
    result = _run_power(tmp_path, variables)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "changed=0" in result.stdout
    assert state.read_text() == "running"


def test_stopped_vm_starts_and_second_run_is_unchanged(tmp_path: Path) -> None:
    state, variables = _proxmox(tmp_path, "stopped")
    first = _run_power(tmp_path, variables)
    assert first.returncode == 0, first.stdout + first.stderr
    assert state.read_text() == "running"
    assert "changed=1" in first.stdout
    second = _run_power(tmp_path, variables)
    assert second.returncode == 0, second.stdout + second.stderr
    assert "changed=0" in second.stdout


def test_real_start_failure_is_reported(tmp_path: Path) -> None:
    state, variables = _proxmox(tmp_path, "stopped", fail_start=True)
    result = _run_power(tmp_path, variables)
    assert result.returncode != 0
    assert "VM is locked" in result.stdout + result.stderr
    assert state.read_text() == "stopped"


def test_standalone_inventory_skips_proxmox(tmp_path: Path) -> None:
    result = _run_power(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "changed=0" in result.stdout


@pytest.mark.parametrize("vmid", [999, True, "117/../../118"])
def test_invalid_or_missing_vm_cannot_start_another_vm(tmp_path: Path, vmid) -> None:
    state, variables = _proxmox(tmp_path, "stopped")
    result = _run_power(tmp_path, {**variables, "proxmox_vmid": vmid})
    assert result.returncode != 0
    assert "inventory VM ID" in result.stdout + result.stderr
    assert state.read_text() == "stopped"
