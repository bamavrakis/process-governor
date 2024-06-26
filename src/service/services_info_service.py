from abc import ABC
from typing import Optional

import psutil
from psutil import STATUS_STOPPED, NoSuchProcess, ZombieProcess, AccessDenied
from psutil._pswindows import WindowsService

from constants.any import LOG
from model.service import Service
from util.decorators import suppress_exception

# Fix bug of psutil
WindowsService.description = suppress_exception(
    WindowsService.description,
    (FileNotFoundError, ZombieProcess, AccessDenied, OSError),
    lambda: ""
)
WindowsService._query_config = suppress_exception(
    WindowsService._query_config,
    (FileNotFoundError, ZombieProcess, AccessDenied, OSError),
    lambda: dict(display_name="", binpath="", username="", start_type="")
)


class ServicesInfoService(ABC):
    """
    The ServicesInfoService class provides methods for retrieving information about running services.
    It is an abstract base class (ABC) to be subclassed by specific implementation classes.
    """

    @staticmethod
    def get_list() -> dict[int, Service]:
        """
        Get a dictionary of running services and their information.

        Returns:
            dict[int, Service]: A dictionary where keys are process IDs (pids) and values are Service objects
            representing the running services.
        """
        result: dict[int, Service] = {}

        for service in psutil.win_service_iter():
            try:
                info = service.as_dict()

                if info['status'] == STATUS_STOPPED:
                    continue

                result[info['pid']] = Service(
                    info['pid'],
                    info['name'],
                    info['display_name'],
                    info['description'],
                    info['status'],
                    info['binpath']
                )
            except NoSuchProcess:
                LOG.warning(f"No such service: {service.name}")

        return result

    @classmethod
    def get_by_pid(cls, pid: int, dct: dict[int, Service]) -> Optional[Service]:
        """
        Get a Service object by its process ID (pid) from the provided dictionary.

        Args:
            pid (int): The process ID (pid) of the service to retrieve.
            dct (dict[int, Service]): A dictionary of services where keys are process IDs (pids) and values are
            Service objects.

        Returns:
            Optional[Service]: The Service object if found, or None if not found.
        """
        return dct.get(pid)
