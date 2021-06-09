class Portfolio:
    def __init__(self):
        # A list of lists: [[name, shares, price], ...]
        self.stocks = []

    def show(self):
        print("Stocks that we have: {}{}".format((self.stocks), "\n"))
        print("Cost of the Remaining Stocks that we have: {}{}".format((self.cost()), "\n"))

    def buy(self, name, shares, price):
        """Buy shares at a certain price."""
        self.stocks.append([name, shares, price])

    def cost(self):
        """What was the total cost of this portfolio?"""
        amt = 0.0
        for name, shares, price in self.stocks:
            amt += shares * price
        return amt

    def sell(self, name, shares):
        for holding in self.stocks:
            if holding[0] == name:
                if holding[1] < shares:
                    raise ValueError("Not Enough Shares")
                holding[1] -= shares
                break
        else:
            raise ValueError("You don't own that stuck ")
