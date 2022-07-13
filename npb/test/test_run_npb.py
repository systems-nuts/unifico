import pytest

from npb.run_npb import parse_suite


def test_parse_suite():
    """
    Test whether parse suite returns the correct list of strings:
        'benchmark_name class'
    """
    tuple_list = parse_suite("npb/test/suite.def")
    target_list = [
        "bt C",
        "sp C",
        "lu C",
        "ft C",
        "cg C",
        "mg C",
        "ep C",
        "ua C",
        "is C",
        "dc B",
    ]

    assert set(tuple_list) == set(target_list), "NPB parse suite error"
