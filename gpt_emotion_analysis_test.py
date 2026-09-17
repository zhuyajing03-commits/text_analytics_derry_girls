import pandas as pd
import spacy

# 1. 读取原始数据
df = pd.read_excel("derry_girls_negative_analysis.xlsx")

# 2. 每类情感按比例抽取最多25条数据
sample = (df.groupby("Negative Emotion", group_keys=False)
            .apply(lambda g: g.sample(min(len(g), 25), random_state=42)))

# 3. 将抽取出的数据打散（洗牌），防止相同情感或相同Season过度集中
sample = sample.sample(frac=1, random_state=42).reset_index(drop=True)

# 4. 自动 POS（词性）标注
# 加载 spaCy 英文预训练模型 (需提前在终端运行: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def text_pos_tagger(text):
    if pd.isna(text):
        return ""
    doc = nlp(str(text))
    # 将文本转化为 "单词/词性" 的格式，例如: "I/PRON love/VERB comedy/NOUN"
    return " ".join([f"{token.text}/{token.pos_}" for token in doc])

# 对 Clean Text 列运行词性标注，并将结果保存至新列
sample["POS Tags"] = sample["Clean Text"].apply(text_pos_tagger)

# 5. 保存到指定的新 Excel 文件，保留所有原始列信息及新增的 POS 结果
output_filename = "negative_analysis_manual_examination.xlsx"
sample.to_excel(output_filename, index=False)

print(f"成功生成抽样与POS标注文件: {output_filename}")