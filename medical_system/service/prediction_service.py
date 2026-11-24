"""业务服务层 - 疾病预测（基于病情文本的文本分类）。"""
from __future__ import annotations

from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB


class PredictionService:
    """“用症状描述预测疾病类型，并返回相似历史病例”。

    采用 TF-IDF + 朴素贝叶斯；训练数据全部来自 ``CaseRepository.all_content()``，
    保证与实际病例语义一致。预测结果仅供参考，不能替代医生诊断。
    """

    def __init__(self, repo) -> None:
        self.repo = repo
        self._vectorizer: TfidfVectorizer | None = None
        self._model: MultinomialNB | None = None
        self._classes: List[str] = []
        self._trained = False

    def _ensure_trained(self) -> None:
        if self._trained:
            return
        rows = self.repo.all_content()
        texts = [r["text"] for r in rows]
        labels = [r["label"] for r in rows]
        if not texts:
            self._trained = True
            return
        self._vectorizer = TfidfVectorizer(max_features=2000)
        X = self._vectorizer.fit_transform(texts)
        self._model = MultinomialNB()
        self._model.fit(X, labels)
        self._classes = list(self._model.classes_)
        self._trained = True

    def predict(self, content: str) -> Dict[str, Any]:
        self._ensure_trained()
        if not self._trained_ok():
            return {
                "disease": "未知",
                "confidence": 0.0,
                "advice": "暂无足够训练数据，建议就医咨询",
                "similarCases": [],
            }

        Xq = self._vectorizer.transform([content])
        proba = self._model.predict_proba(Xq)[0]
        idx = int(proba.argmax())
        disease = str(self._classes[idx])
        confidence = float(proba[idx])

        similar = self._similar_cases(content, top_k=3)
        advice = self._advice(disease)
        return {
            "disease": disease,
            "confidence": round(confidence, 4),
            "advice": advice,
            "similarCases": similar,
        }

    def _trained_ok(self) -> bool:
        return self._model is not None and self._vectorizer is not None and bool(self._classes)

    def _similar_cases(self, content: str, top_k: int = 3) -> List[Dict[str, Any]]:
        rows = self.repo.all_content()
        if not rows:
            return []
        texts = [content] + [r["text"] for r in rows]
        X = self._vectorizer.transform(texts)
        sims = cosine_similarity(X[0:1], X[1:])[0]
        order = sims.argsort()[::-1][:top_k]
        result = []
        for i in order:
            result.append({
                "label": rows[i]["label"],
                "text": rows[i]["text"],
                "similarity": round(float(sims[i]), 3),
            })
        return result

    @staticmethod
    def _advice(disease: str) -> str:
        base = "建议及时就医，遵医嘱用药，定期复查。"
        tips = {
            "高血压": "低盐饮食，规律服用降压药，每日监测血压，避免情绪激动。",
            "糖尿病": "控制饮食，规律运动，按时监测血糖，遵医嘱使用降糖药物。",
            "冠心病": "避免剧烈运动，按医嘱服药，出现胸痛应立即就医。",
            "慢性胃炎": "饮食规律，避免辛辣刺激食物，遵医嘱服用胃药。",
            "肺炎": "注意休息，多饮水，遵医嘱使用抗生素，如有高热及时复查。",
            "偏头痛": "避免诱发因素，保证睡眠，必要时遵医嘱使用止痛药。",
            "高血脂": "低脂饮食，规律运动，按医嘱调整血脂药物，定期复查。",
            "颈椎病": "注意颈部保暖，避免长时间低头，适度做颈部功能锻炼。",
            "甲状腺结节": "定期超声随访，如结节增大或功能异常应及时就诊。",
            "抑郁症": "建议及时就诊精神/心理科，规律作息，保持社交，遵医嘱治疗。",
        }
        return tips.get(disease, base)
