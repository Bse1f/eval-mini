"""一个很笨的关键词分类器，代表"上一版系统"。它就是被评测的那个对象。"""

import argparse

import pandas as pd

# 顺序有意义：从上往下试，命中就停
RULES = [
    ("虚焊", ["虚焊", "焊点", "焊接"]),
    ("外观划伤", ["划伤", "刮花", "擦伤"]),
    ("外观毛刺", ["毛刺", "飞边", "异物"]),
    ("尺寸超差", ["尺寸", "公差", "超差"]),
]


def classify(text):
    """输入：一句现场描述；输出：一个类别码，都不命中就拒答。"""
    for code, words in RULES:
        for word in words:
            if word in text:
                return code
    return "拒答"


def main():
    ap = argparse.ArgumentParser(description="关键词分类器")
    ap.add_argument("--input", default="data/cases.csv")
    ap.add_argument("--out", default="data/pred.csv")
    args = ap.parse_args()

    cases = pd.read_csv(args.input, encoding="utf-8-sig")
    cases["pred_code"] = [classify(t) for t in cases["text"]]

    cases[["id", "pred_code"]].to_csv(args.out, index=False, encoding="utf-8-sig")
    print("已写入", args.out, "共", len(cases), "条")
    print()
    print("它自己觉得各类多少条：")
    print(cases["pred_code"].value_counts().to_string())


if __name__ == "__main__":
    main()
