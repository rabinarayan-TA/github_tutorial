from func import Portfolio
import pytest

# To test the .sell() method, we add three more tests


def test_sell():
    p = Portfolio()
    p.buy("MSFT", 100, 27.0)
    p.buy("DELL", 100, 17.0)
    p.buy("ORCL", 100, 34.0)
    p.sell("MSFT", 50)
    assert p.cost() == 6450


def test_not_enough():
    p = Portfolio()  # Didn't I just do this?
    p.buy("MSFT", 100, 27.0)  #  |
    p.buy("DELL", 100, 17.0)  #  |
    p.buy("ORCL", 100, 34.0)  #  /
    with pytest.raises(ValueError):
        p.sell("MSFT", 200)


def test_dont_own_it():
    p = Portfolio()  # What, again!?!?
    p.buy("MSFT", 100, 27.0)  #  |
    p.buy("DELL", 100, 17.0)  #  |
    p.buy("ORCL", 100, 34.0)  #  /
    with pytest.raises(ValueError):
        p.sell("IBM", 1)
