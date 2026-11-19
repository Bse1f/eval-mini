"""人工标注和机器预测差多远：算一致率、列分歧清单。"""

import argparse

import pandas as pd

ORDER = ["正常", "边界", "对抗", "历史失败"]


def main():
    ap = argparse.ArgumentParser(description="人机一致率")
    ap.add_argument("--human", default="data/human_40.csv")
    ap.add_argument("--pred", default="data/pred.csv")
    ap.add_argument("--cases", default="data/cases.csv")
    ap.add_argument("--out", default="reports/disagreement.csv")
    args = ap.parse_args()

    human = pd.read_csv(args.human, encoding="utf-8-sig")
    human = human.rename(columns={"我的判定": "人判"})
    pred = pd.read_csv(args.pred, encoding="utf-8-sig")
    cases = pd.read_csv(args.cases, encoding="utf-8-sig")

    df = human.merge(pred, on="id", how="left").merge(
        cases[["id", "stratum", "gold_code"]], on="id", how="left"
    )
    df["人判"] = df["人判"].fillna("").str.strip()
    df["一致"] = df["人判"] == df["pred_code"]

    print(f"抽检 {len(df)} 条，一致 {df['一致'].sum()} 条，"
          f"人机一致率 {df['一致'].mean() * 100:.1f}%")
    print()

    print("按分层看：")
    by = df.groupby("stratum").agg(条数=("一致", "size"), 一致=("一致", "sum"))
    by["一致率"] = (by["一致"] / by["条数"] * 100).round(1)
    by = by.reindex([s for s in ORDER if s in by.index])
    print(by.to_string())
    print()

    diff = df[~df["一致"]].rename(columns={
        "id": "编号", "text": "现场描述", "stratum": "分层",
        "gold_code": "标准答案", "pred_code": "机器", "人判": "人",
    })
    diff = diff[["编号", "现场描述", "分层", "标准答案", "机器", "人"]]
    diff.to_csv(args.out, index=False, encoding="utf-8-sig")

    print(f"分歧 {len(diff)} 条，已写入 {args.out}")
    if len(diff):
        print(diff.to_string(index=False))


if __name__ == "__main__":
    main()
