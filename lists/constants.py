# Currencies
class Currency:
    def __init__(self, name, abbreviation, slice):
        self.abbreviation = abbreviation
        self.name = name
        self.string_slice = slice

    def __str__(self):
        return '{name} ({abbreviation})'.format(abbreviation=self.abbreviation, name=self.name)

NZD = Currency(name='New Zealand Dollars', abbreviation='NZD', slice=slice(3, None, None))
USD = Currency(name='USA Dollars', abbreviation='USD', slice=slice(3, None, None))
GBP = Currency(name='Great Britain Pounds', abbreviation='GBP', slice=slice(1, None, None))
CZK = Currency(name='Czech Koruna', abbreviation='CZK', slice=slice(0, -3, None))
