

import argparse

import pandas as pd


LINES = ["A", "B", "C", "D", "E", "F"]
POS = ["1", "2", "3", "4", "5", "6"]


TEMPLATES = [
    ("{线}线{位}号 焊点看着不牢", "虚焊", "正常", ""),
    ("{线}线{位}号 表面有刮花", "外观划伤", "正常", ""),
    ("{线}线{位}号 尺寸偏了 0.3mm", "尺寸超差", "正常", ""),
    ("{线}线{位}号 有异物，也可能是毛刺", "外观毛刺", "边界", "其他"),
    ("{线}线{位}号 尺寸好像偏了一点", "尺寸超差", "边界", "其他"),
    ("{线}线{位}号 不良，你看着办", "拒答", "对抗", "其他"),
    ("{线}线{位}号 客户退回来的，上次也是这问题", "拒答", "对抗", "其他"),
    ("{线}线{位}号 不是虚焊，是毛刺", "外观毛刺", "历史失败", ""),
    ("{线}线{位}号 表面有划伤，不是毛刺", "外观划伤", "历史失败", ""),
    ("{线}线{位}号 焊点牢，但表面刮花", "外观划伤", "历史失败", ""),
]


QUOTA = {"正常": 90, "边界": 50, "对抗": 35, "历史失败": 25}


def main():
    ap = argparse.ArgumentParser(description="生成评测集")
    ap.add_argument("--out", default="data/cases.csv")
    args = ap.parse_args()


    rows = []
    for tpl, gold, stratum, accept in TEMPLATES:
        for line in LINES:
            for pos in POS:
                text = tpl.replace("{线}", line).replace("{位}", pos)
                rows.append({
                    "text": text,
                    "gold_code": gold,
                    "stratum": stratum,
                    "accept_codes": accept,
                })

    df = pd.DataFrame(rows).drop_duplicates(subset=["text"])
    print("组合出来", len(rows), "条，去重后", len(df), "条")


    picked = []
    for stratum, want in QUOTA.items():
        pool = df[df["stratum"] == stratum]
        if len(pool) < want:
            raise SystemExit(f"「{stratum}」只有 {len(pool)} 条，不够 {want} 条，请加模板")
        picked.append(pool.sample(n=want, random_state=42))


    out = pd.concat(picked).sample(frac=1, random_state=42).reset_index(drop=True)
    out.insert(0, "id", range(1, len(out) + 1))
    out = out[["id", "text", "gold_code", "stratum", "accept_codes"]]
    out.to_csv(args.out, index=False, encoding="utf-8-sig")

    print("已写入", args.out, "共", len(out), "条")
    print()
    print("每层多少条：")
    print(out["stratum"].value_counts().to_string())
    print()
    print("每种答案多少条：")
    print(out["gold_code"].value_counts().to_string())
    print()
    print("有没有重复：", out["text"].duplicated().sum(), "条（要是 0）")


if __name__ == "__main__":
    main()
