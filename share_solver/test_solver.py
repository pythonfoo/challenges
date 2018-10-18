import pytest

from . import get_all_solutions


@pytest.mark.parametrize(
    "solution",
    list(get_all_solutions()),
)
@pytest.mark.parametrize(
    "inputs,result",
    [
        ((8, 32, 10), (4, 9)),
        ((55, 29, 64), ((15, 16))),
        ((64, 74, 34), ((137, 230))),
        ((32, 88, 78), ((39, 4))),
        ((34, 45, 81), ((79, 14))),
        ((90, 24, 73), ((168, 233))),
        ((14, 71, 25), ((71, 42))),
        ((80, 51, 9), ((7, 111))),
        ((69, 61, 45), ((183, 253))),
        ((80, 35, 92), ((161, 32))),
        ((69, 41, 23), ((41, 231))),
    ],
)
def test_solution(solution, inputs, result):
    # print(SOLUTION)
    print(f"{solution}, {inputs} -> {result}")
    assert solution(*inputs) == result
