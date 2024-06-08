from abc import ABC
from typing import Set

import psutil
from psutil import NoSuchProcess

from model.process import Process
from configuration.config import Config


class ProcessesInfoService(ABC):
    """
    The ProcessesInfoService class provides methods for retrieving information about running processes.
    It is an abstract base class (ABC) to be subclassed by specific implementation classes.
    """

    @classmethod
    def get_list(cls, config: Config) -> dict[int, Process]:
        """
        Get a dictionary of running processes and their information.

        Returns:
            dict[int, Process]: A dictionary where keys are process IDs (pids) and values are Process objects
            representing the running processes.
        """
        result: dict[int, Process] = {}
        cls.__pids_to_reinforce = set()
        cls.__process_reinforce_rule_list = set(
            [process_name.lower() for process_name in config.processReinforceRuleList]
        )
        current_pids = psutil.pids()

        for pid in current_pids:
            try:
                process = psutil.Process(pid)
                info: dict[str, str] = process.as_dict(attrs=["name", "exe", "nice", "ionice", "cpu_affinity"])
                result[pid] = Process(
                    pid,
                    info["exe"],
                    info["name"],
                    int(info["nice"]) if info["nice"] else None,
                    int(info["ionice"]) if info["ionice"] else None,
                    info["cpu_affinity"],
                    process,
                )

                process_name = info.get("name", "").lower()
                if process_name in cls.__process_reinforce_rule_list:
                    cls.__pids_to_reinforce.add(pid)

            except NoSuchProcess:
                pass

        cls.__prev_pids = set(current_pids)

        return result

    __prev_pids: Set[int] = set()
    __pids_to_reinforce: Set[int] = set()
    __process_reinforce_rule_list: Set[int] = set()

    @classmethod
    def get_new_processes(cls) -> dict[int, Process]:
        """
        Get a dictionary of newly created processes since the last check.

        Returns:
            dict[int, Process]: A dictionary where keys are process IDs (pids) and values are Process objects
            representing the newly created processes.
        """
        result: dict[int, Process] = {}
        current_pids = psutil.pids()

        for pid in current_pids:
            if pid not in cls.__prev_pids or pid in cls.__pids_to_reinforce:
                try:
                    process = psutil.Process(pid)
                    info: dict[str, str] = process.as_dict(attrs=["name", "exe", "nice", "ionice", "cpu_affinity"])
                    result[pid] = Process(
                        pid,
                        info["exe"],
                        info["name"],
                        int(info["nice"]) if info["nice"] else None,
                        int(info["ionice"]) if info["ionice"] else None,
                        info["cpu_affinity"],
                        process,
                    )

                    process_name = info.get("name", "").lower()
                    if process_name in cls.__process_reinforce_rule_list:
                        cls.__pids_to_reinforce.add(pid)

                except NoSuchProcess:
                    pass

        cls.__prev_pids = set(current_pids)

        return result
