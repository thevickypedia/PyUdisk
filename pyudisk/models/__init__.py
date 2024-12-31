from typing import List

from pydantic import BaseModel, Field


class Usage(BaseModel):
    """Disk partition's usage information."""

    Total: str
    Used: str
    Free: str
    Percent: int | float


class SystemPartitions(BaseModel):
    """System partitions' mountpoints and fstypes."""

    system_mountpoints: List[str] = Field(
        default_factory=lambda: [
            "/sys",
            "/proc",
            "/dev",
            "/run",
            "/boot",
            "/tmp",
            "/var",
            "/snap",
            "/sys/kernel",
            "/sys/fs",
            "/var/lib/docker",
            "/dev/loop",
            "/run/user",
            "/run/snapd",
        ]
    )
    system_fstypes: List[str] = Field(
        default_factory=lambda: [
            "sysfs",
            "proc",
            "devtmpfs",
            "tmpfs",
            "devpts",
            "fusectl",
            "securityfs",
            "overlay",
            "hugetlbfs",
            "debugfs",
            "cgroup2",
            "configfs",
            "bpf",
            "binfmt_misc",
            "efivarfs",
            "fuse",
            "nsfs",
            "squashfs",
            "autofs",
            "tracefs",
            "pstore",
        ]
    )
