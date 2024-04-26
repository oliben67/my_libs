import io
import sys
import uuid
from typing import Any, Callable

from cembalo.chord.orchestrator import AzureChordOrchestrator


class CaptureOutput:
    def __enter__(self):
        self._stdout_output = ""
        self._stderr_output = ""

        self._stdout = sys.stdout
        sys.stdout = io.StringIO()

        self._stderr = sys.stderr
        sys.stderr = io.StringIO()

        return self

    def __exit__(self, *args):
        self._stdout_output = sys.stdout.getvalue()
        sys.stdout = self._stdout

        self._stderr_output = sys.stderr.getvalue()
        sys.stderr = self._stderr

    @property
    def stdout(self):
        return self._stdout_output

    @property
    def stderr(self):
        return self._stderr_output


def match_conditions(
    dictionary: dict[Any, Any],
    *,
    conditions: dict[Any, Callable[[Any], bool]],
    _and: bool = True,
    absolute: bool = False,
):
    """
    Filters a dictionary based on a dictionary of conditions. The conditions are
    either a value or a callable that takes the value as as input and needs to
    resolve to a boolean.

    example:
        >>> d = {"a": 1, "b": 3}
        >>> match_conditions(d, conditions={"a": 1, "b": lambda v: v > 2})
        True

    :param dictionary: The dictionary to filter.
    :type dictionary: ``dict[Any, Any]``
    :param conditions: A dictionary of conditions to apply to the dictionary's fields.
    :type conditions: ``dict[Any, Callable[[Any], bool]]``
    :param _and: Whether to match all conditions (True) or any condition (False).
    Defaults to ``True``.
    :type _and: ``bool``
    :param absolute: Whether all keys in conditions need to exist in dictionary.
    Defaults to ``False``.
    :type absolute: ``bool``
    :rtype: ``bool``
    """
    results = [
        condition(dictionary[key])
        if callable(condition)
        else (dictionary[key] if absolute else dictionary.get(key)) == condition
        for key, condition in conditions.items()
    ]

    return all(results) if _and else any(results)


def kill_orphaned_nics(redirect_output=False, **tags_filter):
    """
    Deletes orphaned network interfaces based on the tags provided.

    :param redirect_output: Whether to redirect the output to a file.
    :type redirect_output: ``bool``
    :param tags_filter: Tags to filter the network interfaces by.
    :type tags_filter: ``dict[str, Any]``
    :rtype: ``dict``
    """
    chord_request_id = str(uuid.UUID(int=0))
    orch = AzureChordOrchestrator.create(chord_request_id=chord_request_id, tags={})
    nics = orch.resource_manager.network_management.network_interfaces.list_all()

    deletion_results: dict[str, bool | Exception] = {}
    outputs: dict[str, dict[str, Any]] = {}

    for nic_name, resource_group_name in [
        (nic.name, parse_resource_id(nic.id).get("resource_group"))
        for nic in nics
        if nic.virtual_machine is None
        and match_conditions(nic.tags, conditions=tags_filter)
    ]:
        try:
            if not redirect_output:
                orch.resource_manager.delete_nic(
                    resource_group_name=resource_group_name, nic_name=nic_name
                )
            else:
                with CaptureOutput() as capture:
                    orch.resource_manager.delete_nic(
                        resource_group_name=resource_group_name,
                        nic_name=nic_name,
                    )
                outputs[nic_name] = {
                    "stdout": capture.stdout,
                    "stderr": capture.stderr,
                }
            deletion_results[nic_name] = True
        except Exception as e:
            deletion_results[nic_name] = e

    return (
        (
            deletion_results
            if not redirect_output
            else {**deletion_results, **{"outputs": outputs}}
        )
        if deletion_results
        else {}
    )


if __name__ == "__main__":
    kill_orphaned_nics(
        **{"finmod-chord-request-url": "https://cembalo.int.finmod.eu.scor.local"},
    )

