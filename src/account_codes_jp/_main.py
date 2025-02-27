from collections.abc import Sequence
from enum import StrEnum
from io import BytesIO
from logging import getLogger
from pathlib import Path
from typing import Any, Literal, Protocol, TypeVar

import networkx as nx
import numpy as np
import pandas as pd
from requests_cache import CachedSession

LOG = getLogger(__name__)

Account = TypeVar("Account", bound=str)
SUNDRY = "諸口"
AccountSundry = Literal["諸口"]


class ETaxAccountProtocol(Protocol):
    industry: Literal[
        "一般商工業",
        "建設業",
        "銀行・信託業",
        "銀行・信託業（特定取引勘定設置銀行）",
        "建設保証業",
        "第一種金融商品取引業",
        "生命保険業",
        "損害保険業",
        "鉄道事業",
        "海運事業",
        "高速道路事業",
        "電気通信事業",
        "電気事業",
        "ガス事業",
        "資産流動化業",
        "投資運用業",
        "投資業",
        "特定金融業",
        "社会医療法人",
        "学校法人",
        "商品先物取引業",
        "リース事業",
        "投資信託受益証券",
    ]
    """EDINETで設定されている業種目（23業種）"""
    grounded: bool
    """会計基準及び業法等の法令規則に設定の根拠を有するか"""
    label: str
    """標準ラベル（日本語）"""
    label_en: str
    """標準ラベル（英語）"""
    label_long: str
    """冗長ラベル（日本語）"""
    label_long_en: str
    """冗長ラベル（英語）"""
    label_category: str
    """用途区分、財務諸表区分及び業種区分のラベル（日本語）"""
    label_category_en: str
    """用途区分、財務諸表区分及び業種区分のラベル（英語）"""
    prefix: str
    """名前空間プレフィックス"""
    element: str
    """要素名"""
    type: str
    """データ型"""
    substitution_group: str
    """代替グループ"""
    instant: bool
    """即時かどうか（期間時点区分）"""
    debit: bool
    """借方かどうか（貸借区分）"""
    abstract: bool
    """抽象かどうか"""
    depth: Literal[0, 1, 2, 3, 4, 5, 6, 7]
    """階層の深さ"""
    title: bool
    """EDINETの勘定科目リストで冗長ラベルがタイトル項目"""
    total: bool
    """EDINETの勘定科目リストで用途区分が合計と使用できる"""
    account_type: Literal[
        None,
        "資産",
        "流動資産",
        "固定資産",
        "有形固定資産",
        "無形固定資産",
        "投資その他の資産",
        "繰延資産",
        "負債",
        "流動負債",
        "固定負債",
        "特別法上の準備金等",
        "純資産",
        "株主資本",
        "資本金",
        "資本剰余金",
        "利益剰余金",
        "評価・換算差額等",
        "新株予約権",
    ]
    """EDINETの勘定科目リストで使用されている勘定科目を財務諸表規則に基づき区分したもの"""
    code: str
    """貸借対照表のCSV形式データを作成するのに使用する勘定科目コード"""
    label_etax: str
    """EDINETの勘定科目リストで使用されている勘定科目及び勘定科目コードに対応する公表用e-Tax勘定科目（日本語）"""
    label_etax_en: str
    """EDINETの勘定科目リストで使用されている勘定科目及び勘定科目コードに対応する公表用e-Tax勘定科目（日本語）"""
    etax: Literal[
        None,
        "資産",
        "流動資産",
        "固定資産",
        "有形固定資産",
        "無形固定資産",
        "投資その他の資産",
        "繰延資産",
        "負債",
        "流動負債",
        "固定負債",
        "特別法上の準備金等",
        "純資産",
        "株主資本",
        "資本金",
        "資本剰余金",
        "利益剰余金",
        "評価・換算差額等",
        "新株予約権",
    ]
    """e-Taxの勘定科目を財務諸表規則に基づき区分したもの"""


def to_bool_or_nan(
    x: "pd.Series[str]",
    true_values: Sequence[Any],
    false_values: Sequence[Any],
) -> "pd.Series[Any]":
    true_idx = x.isin(true_values)
    false_idx = x.isin(false_values)
    x[true_idx] = True
    x[false_idx] = False
    x[~true_idx & ~false_idx] = pd.NA
    return x


def get_all_account(
    debug_unique: bool = False,
) -> tuple[Sequence[ETaxAccountProtocol], nx.DiGraph]:
    path = Path("~/.cache/aoiro/aoiro").expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with CachedSession(path) as s:
        URL = (
            "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho3/1/BScodeall_2019.xlsx"
        )
        r = s.get(URL)
        with BytesIO(r.content) as f:
            df = pd.read_excel(
                f,
                sheet_name="貸借対照表\u3000勘定科目コード表(2019年版)",
                skiprows=2,
                na_values=["-"],
                true_values=["true"],
                false_values=["false"],
            )
    df.rename(
        columns={
            "業種": "industry",
            "科目分類": "grounded",
            "標準ラベル（日本語）": "label",
            "標準ラベル（英語）": "label_en",
            "冗長ラベル（日本語）": "label_long",
            "冗長ラベル（英語）": "label_long_en",
            "用途区分、財務諸表区分及び業種区分のラベル（日本語）": "label_category",
            "用途区分、財務諸表区分及び業種区分のラベル（英語）": "label_category_en",
            "名前空間プレフィックス": "prefix",
            "要素名": "element",
            "type": "type",
            "substitutionGroup": "substitution_group",
            "periodType": "instant",
            "balance": "debit",
            "abstract": "abstract",
            "depth": "depth",
            "タイトル項目": "title",
            "合計\n（用途区分）": "total",
            "勘定科目区分": "account_type",
            "勘定科目コード": "account_code",
            "e-Tax対応勘定科目（日本語）": "label_etax",
            "e-Tax対応勘定科目（英語）": "label_etax_en",
            "e-Tax勘定科目区分": "etax",
        },
        inplace=True,
        errors="raise",
    )
    for k in ["total", "title"]:
        df[k] = to_bool_or_nan(df[k], ["○"], [np.nan])
    df["instant"] = to_bool_or_nan(df["instant"], ["instant"], ["duration"])
    df["debit"] = to_bool_or_nan(df["debit"], ["debit"], ["credit"])

    if debug_unique:
        for k, col in df.items():
            LOG.debug(f"{k}: {col.unique()[:100].tolist()}")

    G = nx.DiGraph()
    ancestors: list[Any] = []
    for k, row in df.iterrows():
        G.add_node(row["label"], **row.to_dict())
        if row["depth"] > len(ancestors) + 1:
            raise RuntimeError(
                f"{k}: depth: {row['depth']}, depth_prev: {len(ancestors)}"
            )
        ancestors = ancestors[: row["depth"] - 1]
        if ancestors:
            G.add_edge(ancestors[-1], row["label"])
        ancestors.append(row["label"])
    return df, G


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
