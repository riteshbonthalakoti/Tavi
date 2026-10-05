import re
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field

class IntentResult(BaseModel):
    intent_name: Optional[str] = None
    intent_type: str = "task"  # "task" or "conversation"
    confidence: float = 0.0
    matched_rule: Optional[str] = None
    normalized_input: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    is_supported: bool = False

class IntentRule:
    def __init__(self, name: str, patterns: List[str], intent_type: str = "task"):
        self.name = name
        self.intent_type = intent_type
        # Compile deterministic regex patterns that match the entire normalized string
        self.patterns = [re.compile(p) for p in patterns]

class IntentRegistry:
    def __init__(self):
        self._intents: List[IntentRule] = []

    def register(self, intent_name: str, patterns: List[str], intent_type: str = "task") -> None:
        self._intents.append(IntentRule(intent_name, patterns, intent_type=intent_type))

    def get_rules(self) -> List[IntentRule]:
        return self._intents

class IntentEngine:
    def __init__(self, registry: IntentRegistry):
        self.registry = registry

    def normalize(self, text: str) -> str:
        """
        Deterministically normalizes input text.
        """
        text = text.lower()
        text = re.sub(r'[?!.,;:]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def classify(self, text: str) -> IntentResult:
        """
        Classifies the normalized text against registered deterministic patterns.
        """
        normalized = self.normalize(text)
        
        for rule in self.registry.get_rules():
            for pattern in rule.patterns:
                if pattern.match(normalized):
                    return IntentResult(
                        intent_name=rule.name,
                        intent_type=rule.intent_type,
                        confidence=1.0,
                        matched_rule=pattern.pattern,
                        normalized_input=normalized,
                        is_supported=True
                    )
                    
        return IntentResult(
            normalized_input=normalized
        )
