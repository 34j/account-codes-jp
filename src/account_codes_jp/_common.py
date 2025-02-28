from typing import Literal, TypeVar

import networkx as nx
from strenum import StrEnum

SUNDRY = "諸口"
Account = TypeVar("Account", bound=str)
AccountSundry = Literal["諸口"]


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


def get_account_type(G: nx.DiGraph, account: str) -> AccountType | None:
    ancestors = nx.ancestors(G, account)
    ancestors_l2 = ancestors[2]
    if SUNDRY in ancestors_l2:
        return AccountType.Sundry
    for account_type in AccountType:
        if account_type.value in ancestors_l2:
            return account_type
    return None
