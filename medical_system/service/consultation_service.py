"""业务服务层 - AI 医疗咨询（规则兜底 + 可选 DeepSeek 大模型）。"""
from __future__ import annotations

from typing import Any, Dict

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - openai 缺失时降级到规则兜底
    OpenAI = None  # type: ignore

from medical_system.core.config import Settings


class ConsultationService:
    def __init__(self) -> None:
        self.settings = Settings.instance()

    def chat(self, message: str) -> Dict[str, Any]:
        if not message or not message.strip():
            raise ParamException("咨询内容不能为空")

        reply = self._llm_chat(message.strip()) if self.settings.llm_api_key else self._rule_chat(message.strip())
        return {
            "answer": reply,
            "source": "deepseek" if self.settings.llm_api_key else "rule",
            "disclaimer": "本回答仅供参考，不能替代专业医生的诊断和治疗，如有身体不适请及时就医。",
        }

    def _llm_chat(self, message: str) -> str:
        try:
            client = OpenAI(api_key=self.settings.llm_api_key,
                            base_url=self.settings.llm_base_url)
            completion = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system",
                     "content": "你是一位专业的医疗咨询助手，用中文简洁、专业地回答健康咨询，并在结尾提醒不能替代医生诊断。"},
                    {"role": "user", "content": message},
                ],
                temperature=0.7,
                max_tokens=600,
            )
            return completion.choices[0].message.content or "未获取到回复。"
        except Exception as exc:  # noqa: BLE001
            return f"（大模型调用失败：{exc}）已切换到规则兜底：\n" + self._rule_chat(message)

    @staticmethod
    def _rule_chat(message: str) -> str:
        lowered = message.lower()
        if any(k in lowered for k in ("发烧", "高烧", "发热", "体温")):
            return ("建议多饮水、休息，必要时服用退烧药（如对乙酰氨基酚）；若体温持续超过39℃或伴有呼吸困难，应及时就医。")
        if any(k in lowered for k in ("头痛", "偏头痛", "头晕")):
            return ("建议避免过度劳累，保证睡眠，避免强光噪音；剧烈或突发头痛应立即就医排除器质性病变。")
        if any(k in lowered for k in ("血压", "高血压", "降压")):
            return ("建议低盐饮食，规律监测血压，遵医嘱服用降压药；血压持续偏高需就诊心内科。")
        if any(k in lowered for k in ("血糖", "糖尿病", "多尿", "多饮")):
            return ("建议控制饮食，规律运动，监测血糖，遵医嘱使用降糖药物。")
        if any(k in lowered for k in ("胃痛", "胃胀", "反酸", "胃炎")):
            return ("建议饮食规律，避免辛辣油腻，按医嘱服用胃药；症状不缓解需就诊消化内科。")
        if any(k in lowered for k in ("失眠", "入睡困难", "情绪低落", "抑郁", "焦虑")):
            return ("建议保持规律作息，适度运动，与亲友沟通；情绪持续低落影响生活时建议就诊精神心理科。")
        return ("感谢您的咨询。由于信息有限，建议您前往正规医院就诊，由专业医生结合检查给出诊断与治疗建议。")
