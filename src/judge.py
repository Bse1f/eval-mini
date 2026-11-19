"""拿预测和标准答案比，判成四档，再按层汇总。"""

import argparse

import pandas as pd

ORDER = ["正常", "边界", "对抗", "历史失败"]


def judge_one(pred, gold, accept):
    """输入：预测、标准答案、也可接受的答案；输出：四档之一。

    顺序不能换：先看对不对，再看是不是没给答案。
    标准答案里本来就有"拒答"这个值，先判"是不是拒答"会把答对的也判成未作答。
    """
    if pred == gold:
        return "完全正确"
    if pred == "":
        return "未作答"
    if accept and pred in accept.split(","):
        return "部分正确"
    return "错误"


def main():
    ap = argparse.ArgumentParser(description="评测判卷")
    ap.add_argument("--cases", default="data/cases.csv")
    ap.add_argument("--pred", default="data/pred.csv")
    ap.add_argument("--out", default="reports/detail.csv")
    args = ap.parse_args()

    cases = pd.read_csv(args.cases, encoding="utf-8-sig")
    pred = pd.read_csv(args.pred, encoding="utf-8-sig")
    df = cases.merge(pred, on="id", how="left")
    df["pred_code"] = df["pred_code"].fillna("")
    df["accept_codes"] = df["accept_codes"].fillna("")

    grades = []
    for p, g, a in zip(df["pred_code"], df["gold_code"], df["accept_codes"]):
        grades.append(judge_one(p, g, a))
    df["grade"] = grades

    df = df.rename(columns={
        "id": "编号", "text": "现场描述", "gold_code": "标准答案",
        "pred_code": "预测", "stratum": "分层", "grade": "判定",
    })
    df.to_csv(args.out, index=False, encoding="utf-8-sig")

    # 先把四档数出来，再算通过率
    tab = pd.crosstab(df["分层"], df["判定"])
    for col in ["完全正确", "部分正确", "错误", "未作答"]:
        if col not in tab.columns:
            tab[col] = 0
    tab = tab[["完全正确", "部分正确", "错误", "未作答"]]
    tab["合计"] = tab.sum(axis=1)
    tab["通过率"] = (tab["完全正确"] / tab["合计"] * 100).round(1)
    tab = tab.reindex([s for s in ORDER if s in tab.index])

    print("分层汇总（通过率 = 完全正确 / 该层条数）")
    print(tab.to_string())
    print()

    total = len(df)
    ok = (df["判定"] == "完全正确").sum()
    print(f"总体：{total} 条，完全正确 {ok} 条，通过率 {ok / total * 100:.1f}%")
    print("明细已写入", args.out)


if __name__ == "__main__":
    main()
