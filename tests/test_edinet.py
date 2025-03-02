from account_codes_jp import AccountType, get_account_type_factory, get_edinet_accounts


def test_get():
    G = get_edinet_accounts()
    t = get_account_type_factory(G)
    assert t("現金") == AccountType.Asset
    assert t("買掛金") == AccountType.Liability
    assert t("資本金") == AccountType.Equity
    assert t("消耗品費") == AccountType.Expense
    assert t("売上高") == AccountType.Revenue
