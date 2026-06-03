"""System 4: Cognitive Operating System

The brain that makes System 3 smarter. Provides pattern recognition,
emotional modeling, language analysis, and executive decision-making.
"""

from .pattern_recognition import (
    PatternLibrary,
    StructureAnalyzer,
    CharacterArcAnalyzer,
    EmotionalArcAnalyzer,
    PacingAnalyzer,
    ThemeAnalyzer,
    PatternScore,
    PatternRecognizer,
)
from .language_engine import (
    LanguageEngine,
    VoiceProfile,
    DialogueScore,
    ScreenplayDialogueAnalysis,
    DialogueCritic,
)
from .director_agent import (
    DirectorAgent,
    Decision,
    Verdict,
    WorkingMemory,
    QualityThresholds,
)

__all__ = [
    "PatternLibrary",
    "StructureAnalyzer",
    "CharacterArcAnalyzer",
    "EmotionalArcAnalyzer",
    "PacingAnalyzer",
    "ThemeAnalyzer",
    "PatternScore",
    "PatternRecognizer",
    "LanguageEngine",
    "VoiceProfile",
    "DialogueScore",
    "ScreenplayDialogueAnalysis",
    "DialogueCritic",
    "DirectorAgent",
    "Decision",
    "Verdict",
    "WorkingMemory",
    "QualityThresholds",
]
