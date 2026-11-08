import pytest

from account_codes_jp import (
    AccountType,
    get_account_ambiguous_factory,
    get_account_type_factory,
    get_blue_return_accounts,
)
from account_codes_jp._blue_return import from_nested_dict


@pytest.mark.parametrize(
    "ambiguous",
    [False, True],
)
def test_get(ambiguous: bool) -> None:
    G = get_blue_return_accounts()
    t = get_account_type_factory(G)
    assert t("現金") == AccountType.Asset
    assert t("買掛金") == AccountType.Liability
    assert t("元入金") == AccountType.Equity
    assert t("消耗品費") == AccountType.Expense
    assert t("売上") == AccountType.Revenue


def test_amb() -> None:
    G = get_blue_return_accounts()
    a = get_account_ambiguous_factory(G)
    assert a("定!!!預金") == "定期預金"
    assert a("しんぶんひ") == "新聞図書費"


def test_account_type_properties() -> None:
    assert AccountType.Asset.debit is True
    assert AccountType.Equity.static is True


def test_from_nested_dict_with_list() -> None:
    G = from_nested_dict({"parent": ["child"]})
    assert G.nodes[2]["label"] == "child"
    assert list(G.predecessors(2)) == [1]
