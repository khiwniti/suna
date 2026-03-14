"""
Carbon MCP Package - Embodied carbon calculation tools for the Suna platform.
"""

from core.carbon_mcp.server import (
    calculate_embodied_carbon,
    get_tgo_factors,
    assess_edge_certification,
    generate_carbon_report,
    optimize_materials,
    map_ifc_quantities_to_carbon,
    TGO_EMISSION_FACTORS,
)

from core.carbon_mcp.data.tgo_factors import get_emission_factors, get_factor

__all__ = [
    "calculate_embodied_carbon",
    "get_tgo_factors",
    "assess_edge_certification",
    "generate_carbon_report",
    "optimize_materials",
    "map_ifc_quantities_to_carbon",
    "TGO_EMISSION_FACTORS",
    "get_emission_factors",
    "get_factor",
]
