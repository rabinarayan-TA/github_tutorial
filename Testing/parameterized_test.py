import pytest
from func import Portfolio


@pytest.fixture()
def sample_portfolio():
    p = Portfolio()
    p.buy("MSFT", 100, 27.0)
    p.buy("DELL", 100, 17.0)
    p.buy("ORCL", 100, 34.0)
    return p


@pytest.mark.parametrize(
    "sym, num, cost",
    [
        ("MSFT", 50, 6450),
        ("MSFT", 10, 7530),
        ("ORCL", 90, 4740),
    ],
)
def test_selling(sample_portfolio, sym, num, cost):
    sample_portfolio.sell(sym, num)
    assert sample_portfolio.cost() == cost
