"""Vault palette and typography — re-exports ``explainers.style`` unchanged.

A single one-line indirection so the vault diagrams use the *same* brass +
slate palette as the gear-card explainers. Import from ``vault.style`` in
vault modules so a future palette swap stays local.
"""

from explainers.style import *  # noqa: F401,F403
