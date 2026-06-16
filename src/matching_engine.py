# -*- coding: utf-8 -*-
"""
TF-IDF 匹配引擎
=============
使用 scikit-learn 的 TfidfVectorizer 计算用户查询与每件展品的余弦相似度，
返回 Top-K 推荐结果。
"""

from typing import List, Dict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from . import config


class MatchingEngine:
    """封装 TF-IDF 语料库构建 + 查询匹配全流程。"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(**config.TFIDF_CONFIG)
        self.tfidf_matrix = None
        self.exhibits: List[Dict] = []

    def build_corpus(self, exhibits: List[Dict]) -> None:
        """接收预处理后的展品列表，构建 TF-IDF 矩阵。"""
        self.exhibits = exhibits
        corpus = [ex.get("_match_text_tokenized", "") for ex in exhibits]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def query(self, query_text: str, top_k: int = None) -> List[Dict]:
        """输入已分词的查询文本，返回 top_k 个推荐结果。"""
        top_k = top_k or config.TOP_K
        if self.tfidf_matrix is None:
            raise RuntimeError("语料库尚未构建，请先调用 build_corpus()")

        query_vec = self.vectorizer.transform([query_text])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = scores.argsort()[::-1][:top_k]

        query_terms = set(query_text.split())
        vocab = np.array(self.vectorizer.get_feature_names_out())

        results = []
        for rank, idx in enumerate(top_indices, start=1):
            exhibit = self.exhibits[idx]
            score = float(scores[idx])
            exhibit_vec = self.tfidf_matrix[idx].toarray().flatten()
            top_feature_idx = exhibit_vec.argsort()[::-1][:30]
            exhibit_terms = set(vocab[top_feature_idx])
            matched = list(query_terms & exhibit_terms)[:8]

            results.append({
                "rank": rank,
                "exhibit": exhibit,
                "exhibit_id": exhibit["id"],
                "exhibit_name_zh": exhibit.get("name_zh", ""),
                "similarity_score": round(score, 4),
                "matched_terms": matched,
            })
        return results

    @staticmethod
    def generate_reason_zh(match_result: Dict, course_name: str, top_keyword: str) -> str:
        """根据模板生成中文匹配理由。"""
        ex = match_result["exhibit"]
        score_pct = int(match_result["similarity_score"] * 100)
        name = ex.get("name_zh", "\u8be5\u5c55\u54c1")
        desc = ex.get("description_zh", "")
        key_aspect = desc[:40].rstrip("\uff0c\u3002\u3001") + "\u2026" if len(desc) > 40 else desc

        return (
            f"\u8be5\u5c55\u54c1\u4e0e\u60a8\u7684\u8bfe\u7a0b\u300c{course_name}\u300d\u76f8\u5173"
            f"(\u5339\u914d\u5ea6\uff1a{score_pct}%)\u3002"
            f"\u5c55\u54c1\u300c{name}\u300d\u5c55\u793a\u4e86{key_aspect}\uff0c"
            f"\u4e0e\u60a8\u63d0\u5230\u7684\u300c{top_keyword}\u300d\u76f4\u63a5\u76f8\u5173\u3002"
        )

    @staticmethod
    def generate_reason_en(match_result: Dict, course_name_en: str, top_keyword_en: str) -> str:
        ex = match_result["exhibit"]
        score_pct = int(match_result["similarity_score"] * 100)
        name = ex.get("name_en", "This exhibit")
        desc = ex.get("description_en", "")
        key_aspect = desc[:80].rstrip(",. ") + "..." if len(desc) > 80 else desc
        return (
            f"This exhibit relates to your course \"{course_name_en}\" "
            f"(Match: {score_pct}%). {name} features {key_aspect}, "
            f"which connects with \"{top_keyword_en}\" from your query."
        )
