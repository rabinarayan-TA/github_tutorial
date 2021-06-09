from func import Portfolio
import pytest

# To test the .sell() method, we add three more tests
# pytest with fixture


@pytest.fixture
def sample_portfolio():
    p = Portfolio()
    p.buy("MSFT", 100, 27.0)
    p.buy("DELL", 100, 17.0)
    p.buy("ORCL", 100, 34.0)
    return p


def test_sell(sample_portfolio):
    sample_portfolio.sell("MSFT", 50)
    assert sample_portfolio.cost() == 6450


def test_not_enough(sample_portfolio):
    with pytest.raises(ValueError):
        sample_portfolio.sell("MSFT", 200)


def test_dont_own_it(sample_portfolio):
    with pytest.raises(ValueError):
        sample_portfolio.sell("IBM", 1)
