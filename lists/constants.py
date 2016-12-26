# Currencies
class Currency:
    def __init__(self, name, abbreviation):
        self.abbreviation = abbreviation
        self.name = name

    def __str__(self):
        return '{name} ({abbreviation})'.format(abbreviation=self.abbreviation, name=self.name)

NZD = Currency(name='New Zealand Dollars', abbreviation='NZD')
USD = Currency(name='USA Dollars', abbreviation='USD')
GBP = Currency(name='Great Britain Pounds', abbreviation='GBP')
CZK = Currency(name='Czech Koruna', abbreviation='CZK')
