from __future__ import annotations

from pathlib import Path

from helpers import ROLE_DIR, env_value, make_source, run_tasks


CONFIGURE = ROLE_DIR / "tasks" / "configure.yml"


def test_configuration_initializes_examples_preserves_unknowns_and_converges(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    process = source / "config" / "process.env"
    process.write_text("LOCAL_SETTING=preserve-me\n", encoding="utf-8")
    compose_before = (source / "docker-compose.yml").read_bytes()

    first = run_tasks(tmp_path, [CONFIGURE])

    assert first.returncode == 0, first.stdout + first.stderr
    assert "LOCAL_SETTING=preserve-me" in process.read_text(encoding="utf-8")
    assert env_value(process, "PUID") == str(__import__("os").getuid())
    assert env_value(process, "PGID") == str(__import__("os").getgid())
    assert env_value(process, "MALCOLM_PROFILE") == "malcolm"
    assert env_value(process, "MALCOLM_CONTAINER_RUNTIME") == "docker"
    pcap = source / "config" / "pcap-capture.env"
    assert env_value(pcap, "PCAP_ENABLE_NETSNIFF") == "false"
    assert env_value(pcap, "PCAP_ENABLE_TCPDUMP") == "false"
    assert (source / "docker-compose.yml").read_bytes() == compose_before

    second = run_tasks(tmp_path, [CONFIGURE])

    assert second.returncode == 0, second.stdout + second.stderr
    assert "changed=0" in second.stdout


def test_configuration_reapplies_changed_capture_inputs(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    first = run_tasks(tmp_path, [CONFIGURE])
    assert first.returncode == 0, first.stdout + first.stderr

    second = run_tasks(
        tmp_path,
        [CONFIGURE],
        variables={
            "ludus_install_malcolm_capture_enabled": True,
            "ludus_install_malcolm_capture_filter": "tcp port 443",
            "ludus_install_malcolm_capture_rotation_megabytes": 2048,
            "ludus_install_malcolm_capture_rotation_minutes": 5,
        },
    )

    assert second.returncode == 0, second.stdout + second.stderr
    pcap = source / "config" / "pcap-capture.env"
    assert env_value(pcap, "PCAP_ENABLE_NETSNIFF") == "true"
    assert env_value(pcap, "PCAP_ENABLE_TCPDUMP") == "false"
    assert env_value(pcap, "PCAP_IFACE") == "eth0"
    assert env_value(pcap, "PCAP_FILTER") == "tcp port 443"
    assert env_value(pcap, "PCAP_ROTATE_MEGABYTES") == "2048"
    assert env_value(pcap, "PCAP_ROTATE_MINUTES") == "5"
    assert env_value(source / "config" / "arkime-live.env", "ARKIME_LIVE_CAPTURE") == "true"
    assert env_value(source / "config" / "zeek-live.env", "ZEEK_LIVE_CAPTURE") == "true"
    assert env_value(source / "config" / "suricata-live.env", "SURICATA_LIVE_CAPTURE") == "true"


def test_configuration_rejects_duplicate_managed_capture_assignment(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    pcap = source / "config" / "pcap-capture.env"
    pcap.write_bytes(
        (source / "config" / "pcap-capture.env.example").read_bytes()
        + b"\nPCAP_FILTER=stale duplicate\n"
    )

    result = run_tasks(
        tmp_path,
        [CONFIGURE],
        variables={"ludus_install_malcolm_capture_filter": "tcp port 443"},
    )

    assert result.returncode != 0
    assert "semantic state" in result.stdout + result.stderr
    assignments = [line for line in pcap.read_text(encoding="utf-8").splitlines() if line.startswith("PCAP_FILTER=")]
    assert assignments == ["PCAP_FILTER=", "PCAP_FILTER=tcp port 443"]
