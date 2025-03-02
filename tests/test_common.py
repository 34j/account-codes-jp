from account_codes_jp import AccountType, get_account_type, get_blue_return_accounts


def test_account_types() -> None:
    G = get_blue_return_accounts()
    assert get_account_type(G, "現金") == AccountType.Asset
    assert get_account_type(G, "買掛金") == AccountType.Liability
    assert get_account_type(G, "元入金") == AccountType.Equity
    assert get_account_type(G, "消耗品費") == AccountType.Expense
    assert get_account_type(G, "仕入") == AccountType.Revenue
