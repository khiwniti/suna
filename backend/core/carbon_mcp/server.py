"""
Embodied Carbon Calculator MCP Server - Provides carbon calculation tools.

This MCP server provides tools for:
- Embodied carbon calculation using TGO emission factors
- EDGE certification methodology assessment
- Carbon reporting and visualization
- Material optimization recommendations

Usage:
    Run as: python -m core.carbon_mcp.server
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from core.carbon_mcp.data.tgo_factors import TGO_EMISSION_FACTORS, get_emission_factors, get_factor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Input models
class CalculateCarbonInput(BaseModel):
    materials: List[Dict[str, Any]]
    project_name: str = "Unnamed Project"
    transport_distance_km: Optional[float] = None
    transport_type: Optional[str] = "road_diesel"


class GetTGOFactorsInput(BaseModel):
    category: Optional[str] = None
    material_key: Optional[str] = None


class AssessEdgeInput(BaseModel):
    project_data: Dict[str, Any]
    target_certification: str = "basic"  # basic, advanced, elite


class GenerateReportInput(BaseModel):
    carbon_data: Dict[str, Any]
    report_type: str = "summary"  # summary, detailed, edg


class OptimizeMaterialsInput(BaseModel):
    current_materials: List[Dict[str, Any]]
    target_reduction_percent: float = 20.0


class MapIFCQuantitiesToCarbonInput(BaseModel):
    ifc_quantities: Dict[str, Any]
    material_mapping: Optional[Dict[str, str]] = None


# EDGE Certification Thresholds (kgCO2e/m²/year)
EDGE_THRESHOLDS = {
    "basic": {
        "operational_energy": 100,  # kWh/m²/year
        "embodied_carbon": 900,  # kgCO2e/m²
        "water": 40,  # liters/person/day
        "materials_mandatory": [
            "structural_steel_recycled",
            "structural_concrete_blended_cement"
        ]
    },
    "advanced": {
        "operational_energy": 75,
        "embodied_carbon": 650,
        "water": 30,
        "materials_mandatory": [
            "structural_steel_recycled",
            "structural_concrete_blended_cement",
            "insulation_high_performance"
        ]
    },
    "elite": {
        "operational_energy": 50,
        "embodied_carbon": 400,
        "water": 20,
        "materials_mandatory": [
            "structural_steel_recycled",
            "structural_concrete_blended_cement",
            "insulation_high_performance",
            "renewable_energy_system"
        ]
    }
}


def calculate_embodied_carbon(
    materials: List[Dict[str, Any]],
    project_name: str = "Unnamed Project",
    transport_distance_km: Optional[float] = None,
    transport_type: str = "road_diesel"
) -> Dict[str, Any]:
    """Calculate embodied carbon for a list of materials with quantities."""
    
    result = {
        "success": True,
        "project_name": project_name,
        "calculation_date": datetime.now().isoformat(),
        "materials": [],
        "total_carbon_kg": 0,
        "total_carbon_tonnes": 0,
        "transport_carbon_kg": 0,
        "grand_total_kg": 0,
        "summary": {}
    }
    
    for mat in materials:
        category = mat.get("category", "").lower()
        material_key = mat.get("material_key", "")
        quantity = float(mat.get("quantity", 0))
        unit = mat.get("unit", "")
        
        # Get emission factor
        factor = get_factor(category, material_key)
        
        if factor is None:
            result["materials"].append({
                "material": mat.get("name", f"{category}/{material_key}"),
                "quantity": quantity,
                "unit": unit,
                "status": "not_found",
                "message": f"No emission factor found for {category}/{material_key}"
            })
            continue
        
        # Calculate carbon
        material_carbon = factor * quantity
        
        mat_result = {
            "material": mat.get("name", f"{category}/{material_key}"),
            "category": category,
            "material_key": material_key,
            "quantity": quantity,
            "unit": unit,
            "emission_factor": factor,
            "emission_factor_unit": TGO_EMISSION_FACTORS.get(category, {}).get("unit", "unit"),
            "carbon_kg": round(material_carbon, 2),
            "carbon_tonnes": round(material_carbon / 1000, 4)
        }
        
        result["materials"].append(mat_result)
        result["total_carbon_kg"] += material_carbon
    
    result["total_carbon_tonnes"] = round(result["total_carbon_kg"] / 1000, 4)
    
    # Add transport carbon if distance provided
    if transport_distance_km and transport_distance_km > 0:
        total_weight_tonnes = sum(m.get("quantity", 0) for m in materials if 
                                   TGO_EMISSION_FACTORS.get(m.get("category", ""), {}).get("unit", "") == "tonne")
        
        transport_factor = get_factor("transport", transport_type)
        if transport_factor and total_weight_tonnes > 0:
            result["transport_carbon_kg"] = round(
                transport_factor * transport_distance_km * total_weight_tonnes, 2
            )
    
    result["grand_total_kg"] = round(
        result["total_carbon_kg"] + result["transport_carbon_kg"], 2
    )
    result["grand_total_tonnes"] = round(result["grand_total_kg"] / 1000, 4)
    
    # Create summary by category
    for mat_result in result["materials"]:
        cat = mat_result.get("category", "unknown")
        if cat not in result["summary"]:
            result["summary"][cat] = {
                "carbon_kg": 0,
                "percentage": 0
            }
        result["summary"][cat]["carbon_kg"] += mat_result.get("carbon_kg", 0)
    
    # Calculate percentages
    for cat in result["summary"]:
        if result["total_carbon_kg"] > 0:
            result["summary"][cat]["percentage"] = round(
                result["summary"][cat]["carbon_kg"] / result["total_carbon_kg"] * 100, 1
            )
    
    return result


def get_tgo_factors(
    category: Optional[str] = None,
    material_key: Optional[str] = None
) -> Dict[str, Any]:
    """Get TGO emission factors for materials."""
    
    if category and material_key:
        factor = get_factor(category, material_key)
        if factor is not None:
            cat_data = TGO_EMISSION_FACTORS.get(category, {})
            factors = cat_data.get("factors", {})
            mat_data = factors.get(material_key, {})
            
            return {
                "success": True,
                "category": category,
                "material_key": material_key,
                "factor": factor,
                "unit": cat_data.get("unit", "unit"),
                "details": mat_data
            }
        else:
            return {
                "success": False,
                "error": f"No factor found for {category}/{material_key}"
            }
    
    if category:
        cat_data = TGO_EMISSION_FACTORS.get(category, {})
        return {
            "success": True,
            "category": category,
            "description": cat_data.get("description", ""),
            "unit": cat_data.get("unit", "unit"),
            "factors": cat_data.get("factors", {})
        }
    
    # Return all categories
    return {
        "success": True,
        "categories": {
            cat: {
                "description": data.get("description", ""),
                "unit": data.get("unit", "unit"),
                "materials": list(data.get("factors", {}).keys())
            }
            for cat, data in TGO_EMISSION_FACTORS.items()
        }
    }


def assess_edge_certification(
    project_data: Dict[str, Any],
    target_certification: str = "basic"
) -> Dict[str, Any]:
    """Assess project against EDGE certification criteria."""
    
    if target_certification not in EDGE_THRESHOLDS:
        return {
            "success": False,
            "error": f"Invalid certification level: {target_certification}. Choose from: {list(EDGE_THRESHOLDS.keys())}"
        }
    
    thresholds = EDGE_THRESHOLDS[target_certification]
    
    result = {
        "success": True,
        "target_certification": target_certification,
        "thresholds": thresholds,
        "assessments": {},
        "overall_status": "pending",
        "recommendations": []
    }
    
    # Extract project metrics
    gross_floor_area = float(project_data.get("gross_floor_area", 0))  # m²
    embodied_carbon_total = float(project_data.get("embodied_carbon_kg", 0))
    operational_energy = float(project_data.get("operational_energy_kwh", 0))  # kWh/year
    water_consumption = float(project_data.get("water_liters_per_day", 0))  # liters/day
    occupant_count = float(project_data.get("occupants", 1))
    
    # Calculate per m² values
    if gross_floor_area > 0:
        embodied_carbon_per_m2 = embodied_carbon_total / gross_floor_area
        operational_energy_per_m2 = operational_energy / gross_floor_area
    else:
        embodied_carbon_per_m2 = 0
        operational_energy_per_m2 = 0
    
    if occupant_count > 0:
        water_per_person = water_consumption / occupant_count
    else:
        water_per_person = water_consumption
    
    # Assess operational energy
    energy_status = "pass" if operational_energy_per_m2 <= thresholds["operational_energy"] else "fail"
    result["assessments"]["operational_energy"] = {
        "value": round(operational_energy_per_m2, 2),
        "threshold": thresholds["operational_energy"],
        "unit": "kWh/m²/year",
        "status": energy_status,
        "message": f"Operational energy: {round(operational_energy_per_m2, 2)} kWh/m²/year (threshold: {thresholds['operational_energy']})"
    }
    if energy_status == "fail":
        result["recommendations"].append(f"Reduce operational energy to {thresholds['operational_energy']} kWh/m²/year or below")
    
    # Assess embodied carbon
    carbon_status = "pass" if embodied_carbon_per_m2 <= thresholds["embodied_carbon"] else "fail"
    result["assessments"]["embodied_carbon"] = {
        "value": round(embodied_carbon_per_m2, 2),
        "threshold": thresholds["embodied_carbon"],
        "unit": "kgCO2e/m²",
        "status": carbon_status,
        "message": f"Embodied carbon: {round(embodied_carbon_per_m2, 2)} kgCO2e/m² (threshold: {thresholds['embodied_carbon']})"
    }
    if carbon_status == "fail":
        result["recommendations"].append(f"Reduce embodied carbon to {thresholds['embodied_carbon']} kgCO2e/m² or below")
    
    # Assess water consumption
    water_status = "pass" if water_per_person <= thresholds["water"] else "fail"
    result["assessments"]["water"] = {
        "value": round(water_per_person, 2),
        "threshold": thresholds["water"],
        "unit": "liters/person/day",
        "status": water_status,
        "message": f"Water consumption: {round(water_per_person, 2)} L/person/day (threshold: {thresholds['water']})"
    }
    if water_status == "fail":
        result["recommendations"].append(f"Reduce water consumption to {thresholds['water']} L/person/day or below")
    
    # Check mandatory materials
    materials_used = project_data.get("materials_used", [])
    mandatory_check = []
    for mandatory in thresholds.get("materials_mandatory", []):
        if mandatory in materials_used:
            mandatory_check.append({"material": mandatory, "status": "present"})
        else:
            mandatory_check.append({"material": mandatory, "status": "missing"})
    
    result["assessments"]["mandatory_materials"] = {
        "status": "pass" if all(m["status"] == "present" for m in mandatory_check) else "fail",
        "items": mandatory_check
    }
    
    # Calculate overall status
    all_pass = all(
        a["status"] == "pass" 
        for a in result["assessments"].values() 
        if isinstance(a, dict) and "status" in a
    )
    result["overall_status"] = "pass" if all_pass else "fail"
    
    if result["overall_status"] == "pass":
        result["recommendations"].insert(0, f"🎉 Project meets {target_certification.upper()} certification criteria!")
    else:
        result["recommendations"].insert(0, "⚠️ Project does not yet meet all EDGE certification criteria")
    
    return result


def generate_carbon_report(
    carbon_data: Dict[str, Any],
    report_type: str = "summary"
) -> Dict[str, Any]:
    """Generate a carbon report from calculation data."""
    
    result = {
        "success": True,
        "report_type": report_type,
        "generated_at": datetime.now().isoformat(),
        "content": {}
    }
    
    if report_type == "summary":
        result["content"] = _generate_summary_report(carbon_data)
    elif report_type == "detailed":
        result["content"] = _generate_detailed_report(carbon_data)
    elif report_type == "edge":
        result["content"] = _generate_edge_report(carbon_data)
    else:
        return {"success": False, "error": f"Unknown report type: {report_type}"}
    
    return result


def _generate_summary_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a summary report."""
    
    total = data.get("total_carbon_kg", 0)
    
    return {
        "title": f"Embodied Carbon Report: {data.get('project_name', 'Unnamed Project')}",
        "total_embodied_carbon": {
            "value": round(total, 2),
            "unit": "kgCO2e"
        },
        "total_embodied_carbon_tonnes": {
            "value": round(total / 1000, 4),
            "unit": "tCO2e"
        },
        "transport_carbon": {
            "value": round(data.get("transport_carbon_kg", 0), 2),
            "unit": "kgCO2e"
        },
        "grand_total": {
            "value": round(data.get("grand_total_kg", total), 2),
            "unit": "kgCO2e"
        },
        "top_contributors": _get_top_contributors(data.get("materials", []), 5),
        "summary_by_category": data.get("summary", {})
    }


def _generate_detailed_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a detailed report with all materials."""
    
    report = _generate_summary_report(data)
    report["detailed_materials"] = data.get("materials", [])
    report["calculation_methodology"] = {
        "source": "Thailand TGO Emission Factors 2024",
        "scope": "Scope 1 + Scope 3 (transport)",
        "note": "Biogenic carbon included for wood products"
    }
    
    return report


def _generate_edge_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an EDGE-specific report."""
    
    report = _generate_summary_report(data)
    report["edge_compatibility"] = {
        "assessed": True,
        "note": "Use assess_edge_certification tool for full EDGE assessment"
    }
    
    # Estimate EDGE categories
    floor_area = data.get("project_floor_area_m2", 1000)  # Default assumption
    
    report["edge_estimates"] = {
        "embodied_carbon_per_m2": round(data.get("total_carbon_kg", 0) / floor_area, 2) if floor_area > 0 else "N/A",
        "unit": "kgCO2e/m²",
        "baseline_comparison": "Compare against EDGE thresholds: Basic=900, Advanced=650, Elite=400"
    }
    
    # Suggest material improvements
    report["material_recommendations"] = _get_edge_recommendations(data.get("materials", []))
    
    return report


def _get_top_contributors(materials: List[Dict], limit: int = 5) -> List[Dict]:
    """Get top carbon-contributing materials."""
    sorted_materials = sorted(
        materials, 
        key=lambda x: x.get("carbon_kg", 0), 
        reverse=True
    )
    return [
        {
            "material": m.get("material", "Unknown"),
            "carbon_kg": round(m.get("carbon_kg", 0), 2),
            "percentage": round(m.get("carbon_kg", 0) / max(sum(mat.get("carbon_kg", 0) for mat in materials), 1) * 100, 1)
        }
        for m in sorted_materials[:limit]
    ]


def _get_edge_recommendations(materials: List[Dict]) -> List[str]:
    """Get recommendations for EDGE certification."""
    
    recommendations = []
    seen_categories = set()
    
    for mat in materials:
        cat = mat.get("category", "")
        key = mat.get("material_key", "")
        
        if cat in seen_categories:
            continue
        seen_categories.add(cat)
        
        # Concrete recommendations
        if cat == "concrete":
            if "recycled" not in key.lower():
                recommendations.append("Consider using recycled aggregate concrete (-25% carbon)")
            if "standard" in key.lower() or "high_strength" in key.lower():
                recommendations.append("Consider using blended cement (PPC/PSC) for concrete (-30% carbon)")
        
        # Steel recommendations
        elif cat == "steel":
            if "recycled" not in key.lower():
                recommendations.append("Consider using recycled EAF steel (-57% carbon)")
        
        # Cement recommendations
        elif cat == "cement":
            if "opc_type_i" in key.lower():
                recommendations.append("Consider using Portland Pozzolana Cement (-26% carbon)")
        
        # Insulation recommendations
        elif cat == "insulation":
            recommendations.append("Ensure insulation meets minimum thickness for climate zone")
    
    if not recommendations:
        recommendations.append("Materials appear to be optimized for low carbon")
    
    return recommendations


def optimize_materials(
    current_materials: List[Dict[str, Any]],
    target_reduction_percent: float = 20.0
) -> Dict[str, Any]:
    """Suggest material alternatives to achieve carbon reduction target."""
    
    result = {
        "success": True,
        "target_reduction": f"{target_reduction_percent}%",
        "original_materials": current_materials,
        "optimizations": [],
        "estimated_reduction_percent": 0,
        "total_savings_kg": 0
    }
    
    # Calculate current total
    current_total = 0
    for mat in current_materials:
        factor = get_factor(mat.get("category", ""), mat.get("material_key", ""))
        if factor:
            current_total += factor * mat.get("quantity", 0)
    
    result["original_total_kg"] = round(current_total, 2)
    
    # Define optimization mappings
    optimizations = {
        # Concrete
        ("concrete", "concrete_standard"): ("concrete", "concrete_recycled"),
        ("concrete", "concrete_high_strength"): ("concrete", "concrete_low_strength"),
        ("concrete", "concrete_ready_mix"): ("concrete", "concrete_recycled"),
        
        # Cement
        ("cement", "opc_type_i"): ("cement", "opc_type_ii"),
        
        # Steel
        ("steel", "steel_rebar"): ("steel", "steel_recycled"),
        ("steel", "steel_section"): ("steel", "steel_recycled"),
        
        # Bricks
        ("bricks", "clay_brick"): ("bricks", "autoclaved_block"),
    }
    
    optimized_materials = []
    
    for mat in current_materials:
        cat = mat.get("category", "").lower()
        key = mat.get("material_key", "")
        
        new_cat, new_key = optimizations.get((cat, key), (None, None))
        
        if new_cat and new_key:
            original_factor = get_factor(cat, key)
            new_factor = get_factor(new_cat, new_key)
            quantity = mat.get("quantity", 0)
            
            if original_factor and new_factor:
                original_carbon = original_factor * quantity
                new_carbon = new_factor * quantity
                savings = original_carbon - new_carbon
                
                optimized_mat = mat.copy()
                optimized_mat["material_key"] = new_key
                optimized_mat["original_carbon_kg"] = round(original_carbon, 2)
                optimized_mat["optimized_carbon_kg"] = round(new_carbon, 2)
                optimized_mat["savings_kg"] = round(savings, 2)
                optimized_mat["savings_percent"] = round(savings / original_carbon * 100, 1) if original_carbon > 0 else 0
                
                result["optimizations"].append({
                    "original": f"{cat}/{key}",
                    "suggested": f"{new_cat}/{new_key}",
                    "savings": round(savings, 2),
                    "savings_percent": round(savings / original_carbon * 100, 1) if original_carbon > 0 else 0
                })
                
                optimized_materials.append(optimized_mat)
                result["total_savings_kg"] += savings
    
    result["optimized_materials"] = optimized_materials
    
    if current_total > 0:
        result["estimated_reduction_percent"] = round(
            result["total_savings_kg"] / current_total * 100, 1
        )
    
    result["final_total_kg"] = round(current_total - result["total_savings_kg"], 2)
    
    return result


def map_ifc_quantities_to_carbon(
    ifc_quantities: Dict[str, Any],
    material_mapping: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Map IFC quantity take-off data to carbon calculation inputs."""
    
    # Default material mapping (IFC type -> TGO category/key)
    default_mapping = {
        "IfcWall": ("concrete", "concrete_standard"),
        "IfcWallStandardCase": ("concrete", "concrete_standard"),
        "IfcCurtainWall": ("glass", "float_glass_6mm"),
        "IfcSlab": ("concrete", "concrete_standard"),
        "IfcRoof": ("roofing", "metal_roofing"),
        "IfcColumn": ("steel", "steel_rebar"),
        "IfcBeam": ("steel", "steel_section"),
        "IfcDoor": ("wood", "timber_solid"),
        "IfcWindow": ("aluminum", "aluminum_extrusion"),
    }
    
    mapping = material_mapping or default_mapping
    
    materials = []
    
    for quantity in ifc_quantities.get("quantities", []):
        elem_type = quantity.get("element_type", "")
        
        if elem_type in mapping:
            cat, key = mapping[elem_type]
            
            # Extract quantities
            q = quantity.get("quantities", {})
            volume = q.get("NetVolume", {}).get("value", 0) or q.get("GrossVolume", {}).get("value", 0)
            area = q.get("NetArea", {}).get("value", 0) or q.get("GrossArea", {}).get("value", 0)
            
            # Determine primary quantity
            if volume and volume > 0:
                quantity_value = volume
                unit = "m³"
            elif area and area > 0:
                quantity_value = area
                unit = "m²"
            else:
                # Use count as fallback
                quantity_value = 1
                unit = "count"
            
            materials.append({
                "category": cat,
                "material_key": key,
                "quantity": quantity_value,
                "unit": unit,
                "source_element": elem_type,
                "element_id": quantity.get("element_id")
            })
    
    return {
        "success": True,
        "materials": materials,
        "note": "Review and adjust quantities before final carbon calculation"
    }


# MCP Server Implementation
app = Server("carbon-mcp-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available carbon calculation tools."""
    return [
        Tool(
            name="calculate_embodied_carbon",
            description="Calculate embodied carbon for a list of materials using Thailand TGO emission factors. Input materials with category, material_key, and quantity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "materials": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string", "description": "Material category (concrete, steel, cement, etc.)"},
                                "material_key": {"type": "string", "description": "Specific material key (e.g., concrete_standard, steel_rebar)"},
                                "quantity": {"type": "number", "description": "Quantity of material"},
                                "unit": {"type": "string", "description": "Unit of measurement"},
                                "name": {"type": "string", "description": "Optional material name"}
                            },
                            "required": ["category", "material_key", "quantity"]
                        },
                        "description": "List of materials to calculate carbon for"
                    },
                    "project_name": {"type": "string", "description": "Project name for the calculation", "default": "Unnamed Project"},
                    "transport_distance_km": {"type": "number", "description": "Average transport distance in km (optional)"},
                    "transport_type": {"type": "string", "description": "Transport type (road_diesel, rail, ship)", "default": "road_diesel"}
                },
                "required": ["materials"]
            }
        ),
        Tool(
            name="get_tgo_factors",
            description="Get Thailand TGO emission factors for construction materials. Can retrieve all categories, a specific category, or a specific material factor.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Material category (concrete, steel, cement, etc.)"},
                    "material_key": {"type": "string", "description": "Specific material key to look up"}
                }
            }
        ),
        Tool(
            name="assess_edge_certification",
            description="Assess a project against EDGE (Excellence in Design for Greater Efficiencies) green building certification criteria. Supports basic, advanced, and elite certification levels.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_data": {
                        "type": "object",
                        "properties": {
                            "gross_floor_area": {"type": "number", "description": "Gross floor area in m²"},
                            "embodied_carbon_kg": {"type": "number", "description": "Total embodied carbon in kgCO2e"},
                            "operational_energy_kwh": {"type": "number", "description": "Annual operational energy in kWh"},
                            "water_liters_per_day": {"type": "number", "description": "Daily water consumption in liters"},
                            "occupants": {"type": "number", "description": "Number of occupants"},
                            "materials_used": {"type": "array", "items": {"type": "string"}, "description": "List of materials used in project"}
                        },
                        "required": ["gross_floor_area", "embodied_carbon_kg"]
                    },
                    "target_certification": {"type": "string", "enum": ["basic", "advanced", "elite"], "description": "Target EDGE certification level", "default": "basic"}
                },
                "required": ["project_data"]
            }
        ),
        Tool(
            name="generate_carbon_report",
            description="Generate a carbon report from calculation data. Supports summary, detailed, and EDGE-specific report formats.",
            inputSchema={
                "type": "object",
                "properties": {
                    "carbon_data": {"type": "object", "description": "Carbon calculation data"},
                    "report_type": {"type": "string", "enum": ["summary", "detailed", "edge"], "description": "Type of report to generate", "default": "summary"}
                },
                "required": ["carbon_data"]
            }
        ),
        Tool(
            name="optimize_materials",
            description="Suggest lower-carbon material alternatives to achieve a target carbon reduction percentage. Analyzes current materials and suggests optimized alternatives.",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_materials": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string"},
                                "material_key": {"type": "string"},
                                "quantity": {"type": "number"},
                                "unit": {"type": "string"}
                            }
                        },
                        "description": "List of current materials"
                    },
                    "target_reduction_percent": {"type": "number", "description": "Target reduction percentage", "default": 20.0}
                },
                "required": ["current_materials"]
            }
        ),
        Tool(
            name="map_ifc_quantities_to_carbon",
            description="Map IFC quantity take-off data to carbon calculation material inputs. Converts BIM element quantities to material categories for carbon calculation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ifc_quantities": {"type": "object", "description": "IFC quantity data from get_element_quantities"},
                    "material_mapping": {"type": "object", "description": "Optional custom mapping of IFC types to TGO categories"}
                },
                "required": ["ifc_quantities"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls."""
    
    if name == "calculate_embodied_carbon":
        result = calculate_embodied_carbon(
            materials=arguments.get("materials", []),
            project_name=arguments.get("project_name", "Unnamed Project"),
            transport_distance_km=arguments.get("transport_distance_km"),
            transport_type=arguments.get("transport_type", "road_diesel")
        )
    elif name == "get_tgo_factors":
        result = get_tgo_factors(
            category=arguments.get("category"),
            material_key=arguments.get("material_key")
        )
    elif name == "assess_edge_certification":
        result = assess_edge_certification(
            project_data=arguments.get("project_data", {}),
            target_certification=arguments.get("target_certification", "basic")
        )
    elif name == "generate_carbon_report":
        result = generate_carbon_report(
            carbon_data=arguments.get("carbon_data", {}),
            report_type=arguments.get("report_type", "summary")
        )
    elif name == "optimize_materials":
        result = optimize_materials(
            current_materials=arguments.get("current_materials", []),
            target_reduction_percent=arguments.get("target_reduction_percent", 20.0)
        )
    elif name == "map_ifc_quantities_to_carbon":
        result = map_ifc_quantities_to_carbon(
            ifc_quantities=arguments.get("ifc_quantities", {}),
            material_mapping=arguments.get("material_mapping")
        )
    else:
        result = {"success": False, "error": f"Unknown tool: {name}"}
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Main entry point for the Carbon MCP server."""
    logger.info("Starting Carbon MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
