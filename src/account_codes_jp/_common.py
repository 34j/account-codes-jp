from strenum import StrEnum


class AccountType(StrEnum):
    Assets = "資産"
    Liabilities = "負債"
    Equity = "純資産"
    Revenue = "収益"
    Expenses = "費用"
    Sundry = "諸口"

    @property
    def is_positive(self) -> bool:
        return self in (AccountType.Assets, AccountType.Revenue)

    @property
    def is_static(self) -> bool:
        return self in (AccountType.Equity, AccountType.Liabilities, AccountType.Equity)
