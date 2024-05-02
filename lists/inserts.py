from itertools import groupby


def splitted(lst, elem):
    """
    Split list on a given element
    """
    return [list(group) for k, group in groupby(lst, lambda x: x == elem) if not k]


def flatten(lst):
    """
    Flattens a nested list into a single list.

    :param lst: The nested list to be flattened.
    :type lst: ``lst``
    :rtype: ``lst``
    """
    return [elem for sub_list in lst for elem in sub_list]


def insert_at(lst, sub, elem, _all=False):
    """
    Inserts the 'sub' list at the first occurrence of 'elem' in the 'lst' list.
    If '_all' is True, inserts 'sub' at all occurrences of 'elem' in 'lst'.

    :param lst: The list to insert into.
    :type lst: ``lst``
    :param sub: The list to insert.
    :type sub: ``lst``
    :param elem: The element to search for in 'lst'.
    :type elem: ``Any``
    :param _all: If True, insert at all occurrences of 'elem'. Defaults to False.
    :type _all: ``bool``
    :rtype: ``lst``
    """
    if isinstance(lst, str):
        return insert_at(
            [c for c in lst],
            [c for c in sub] if isinstance(sub, str) else sub,
            elem,
            _all=_all,
        )

    def _insert_at(l):
        idx = l.index(elem)
        return l[:idx] + sub + l[idx + 1 :]

    if not _all:
        return _insert_at(lst)

    while True:
        try:
            lst = _insert_at(lst)
        except ValueError:
            break

    return lst


def insert_after(lst, sub, elem, _all=False):
    """
    Inserts the elements of the 'sub' list after the first occurrence of 'elem' in the 'lst' list.
    If '_all' is True, inserts 'sub' after all occurrences of 'elem' in 'lst'.

    :param lst: The list to insert into.
    :type lst: ``lst``
    :param sub: The list to insert.
    :type sub: ``lst``
    :param elem: The element to search for in 'lst'.
    :type elem: ``Any``
    :param _all: If True, insert after all occurrences of 'elem'. Defaults to False.
    :type _all: ``bool``
    :rtype: ``lst``
    """
    if isinstance(lst, str):
        return insert_after(
            [c for c in lst],
            [c for c in sub] if isinstance(sub, str) else sub,
            elem,
            _all=_all,
        )

    if not _all:
        idx = lst.index(elem)
        return lst[: idx + 1] + sub + lst[idx + 1 :]

    split_lst = [
        list(group if not k else []) for k, group in groupby(lst, lambda x: x == elem)
    ]
    return flatten(
        [
            sub_list + [elem] + sub if not sub_list else sub_list
            for sub_list in split_lst
        ]
    )


def insert_before(lst, sub, elem, _all=False):
    """
    Inserts a sublist `sub` before the first occurrence of `elem` in the given list `lst`.
    If `_all` is True, inserts `sub` before all occurrences of `elem` in `lst`.

    :param lst: The list to insert into.
    :type lst: ``lst``
    :param sub: The list to insert.
    :type sub: ``lst``
    :param elem: The element to search for in 'lst'.
    :type elem: ``Any``
    :param _all: If True, insert before all occurrences of 'elem'. Defaults to False.
    :type _all: ``bool``
    :rtype: ``lst``
    """
    if isinstance(lst, str):
        return insert_before(
            [c for c in lst],
            [c for c in sub] if isinstance(sub, str) else sub,
            elem,
            _all=_all,
        )

    if not _all:
        idx = lst.index(elem)
        return lst[:idx] + sub + lst[idx:]

    split_lst = [
        list(group if not k else []) for k, group in groupby(lst, lambda x: x == elem)
    ]
    return flatten(
        [
            sub + [elem] + sub_list if not sub_list else sub_list
            for sub_list in split_lst
        ]
    )
