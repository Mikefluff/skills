"""common.runners — optional execution layer for image / video / music prompt skills.

Provider adapters call vendor APIs only when the corresponding env vars are set.
If keys are unset, skills fall back to prompt-only output.
"""

__version__ = "2.2.0"
