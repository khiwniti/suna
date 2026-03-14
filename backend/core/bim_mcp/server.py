"""
BIM MCP Server - Provides BIM-related tools for the Suna platform.

This MCP server provides tools for:
- IFC file parsing and analysis
- Building element extraction
- Material quantity take-off
- Property retrieval from BIM models

Usage:
    Run as: python -m core.bim_mcp.server
    Requires: ifcopenshell>=0.7.0
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from pydantic import BaseModel
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.server.handlers import ListToolsHandler, CallToolHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IFCParseInput(BaseModel):
    file_path: str
    include_geometry: bool = False


class ExtractElementsInput(BaseModel):
    file_path: str
    element_types: Optional[List[str]] = None
    filter_by_property: Optional[str] = None
    filter_value: Optional[str] = None


class GetElementMaterialsInput(BaseModel):
    file_path: str
    element_id: Optional[str] = None
    element_type: Optional[str] = None


class GetElementQuantitiesInput(BaseModel):
    file_path: str
    element_id: Optional[str] = None
    element_type: Optional[str] = None
    include_aggregates: bool = True


class GetElementPropertiesInput(BaseModel):
    file_path: str
    element_id: str
    property_sets: Optional[List[str]] = None


# IFC element type mapping
IFC_ELEMENT_TYPES = {
    "IfcWall": "Walls",
    "IfcSlab": "Slabs/Floors",
    "IfcColumn": "Columns",
    "IfcBeam": "Beams",
    "IfcDoor": "Doors",
    "IfcWindow": "Windows",
    "IfcStair": "Stairs",
    "IfcRoof": "Roofs",
    "IfcBuildingElementProxy": "Building Elements",
    "IfcSpace": "Spaces/Zones",
    "IfcZone": "Zones",
    "IfcWallStandardCase": "Standard Walls",
    "IfcCurtainWall": "Curtain Walls",
    "IfcRamp": "Ramps",
    "IfcRampFlight": "Ramp Flights",
    "IfcStairFlight": "Stair Flights",
    "IfcPlate": "Plates",
    "IfcMember": "Members",
    "IfcElementAssembly": "Element Assemblies",
}


def parse_ifc_file(file_path: str, include_geometry: bool = False) -> Dict[str, Any]:
    """Parse an IFC file and return basic information."""
    try:
        import ifcopenshell
        import ifcopenshell.geom
    except ImportError:
        return {
            "success": False,
            "error": "ifcopenshell not installed. Run: pip install ifcopenshell"
        }
    
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}"
        }
    
    try:
        model = ifcopenshell.open(file_path)
        
        # Get basic file information
        result = {
            "success": True,
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "schema": model.schema,
            "elements": {
                "total": 0,
                "by_type": {}
            },
            "project": None,
            "site": None,
            "building": None,
            "storeys": []
        }
        
        # Get project info
        project = model.by_type("IfcProject")
        if project:
            result["project"] = {
                "id": project[0].id(),
                "name": project[0].Name,
                "description": project[0].Description
            }
            result["elements"]["total"] += len(project)
        
        # Get site info
        sites = model.by_type("IfcSite")
        if sites:
            result["site"] = {
                "id": sites[0].id(),
                "name": sites[0].Name,
                "description": sites[0].Description
            }
            result["elements"]["total"] += len(sites)
        
        # Get building info
        buildings = model.by_type("IfcBuilding")
        if buildings:
            result["building"] = {
                "id": buildings[0].id(),
                "name": buildings[0].Name,
                "description": buildings[0].Description
            }
            result["elements"]["total"] += len(buildings)
        
        # Get storeys
        storeys = model.by_type("IfcBuildingStorey")
        result["storeys"] = [
            {
                "id": s.id(),
                "name": s.Name,
                "elevation": s.Elevation if hasattr(s, 'Elevation') else None
            }
            for s in storeys
        ]
        result["elements"]["total"] += len(storeys)
        
        # Get element counts by type
        for ifc_type, display_name in IFC_ELEMENT_TYPES.items():
            elements = model.by_type(ifc_type)
            if elements:
                result["elements"]["by_type"][display_name] = len(elements)
                result["elements"]["total"] += len(elements)
        
        # Optionally include geometry info
        if include_geometry:
            result["geometry_info"] = _get_geometry_summary(model)
        
        return result
        
    except Exception as e:
        logger.error(f"Error parsing IFC file: {str(e)}")
        return {
            "success": False,
            "error": f"Error parsing IFC file: {str(e)}"
        }


def extract_elements(
    file_path: str,
    element_types: Optional[List[str]] = None,
    filter_by_property: Optional[str] = None,
    filter_value: Optional[str] = None
) -> Dict[str, Any]:
    """Extract elements from an IFC file with optional filtering."""
    try:
        import ifcopenshell
    except ImportError:
        return {
            "success": False,
            "error": "ifcopenshell not installed. Run: pip install ifcopenshell"
        }
    
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}"
        }
    
    try:
        model = ifcopenshell.open(file_path)
        
        result = {
            "success": True,
            "elements": [],
            "count": 0
        }
        
        # Determine which types to extract
        if element_types:
            # Map display names back to IFC types
            type_mapping = {v: k for k, v in IFC_ELEMENT_TYPES.items()}
            ifc_types = [type_mapping.get(t, t) for t in element_types]
        else:
            # Get all building elements
            ifc_types = list(IFC_ELEMENT_TYPES.keys())
        
        for ifc_type in ifc_types:
            elements = model.by_type(ifc_type)
            
            for elem in elements:
                # Apply property filter if specified
                if filter_by_property and filter_value:
                    prop_value = _get_element_property(elem, filter_by_property)
                    if prop_value != filter_value:
                        continue
                
                # Extract element data
                elem_data = {
                    "id": elem.id(),
                    "type": IFC_ELEMENT_TYPES.get(ifc_type, ifc_type),
                    "ifc_type": ifc_type,
                    "name": elem.Name if hasattr(elem, 'Name') and elem.Name else f"Unnamed {ifc_type}",
                    "description": elem.Description if hasattr(elem, 'Description') and elem.Description else None,
                }
                
                # Add material info
                material = elem.Material
                if material:
                    if hasattr(material, 'Name'):
                        elem_data["material"] = material.Name
                    elif isinstance(material, str):
                        elem_data["material"] = material
                
                # Add quantity info if available
                try:
                    quantities = elem.IsDefinedBy
                    if quantities:
                        elem_data["has_quantities"] = True
                except:
                    pass
                
                result["elements"].append(elem_data)
        
        result["count"] = len(result["elements"])
        return result
        
    except Exception as e:
        logger.error(f"Error extracting elements: {str(e)}")
        return {
            "success": False,
            "error": f"Error extracting elements: {str(e)}"
        }


def get_element_materials(
    file_path: str,
    element_id: Optional[str] = None,
    element_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get materials associated with elements."""
    try:
        import ifcopenshell
    except ImportError:
        return {
            "success": False,
            "error": "ifcopenshell not installed"
        }
    
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}"
        }
    
    try:
        model = ifcopenshell.open(file_path)
        materials_map = {}
        
        if element_id:
            # Get specific element
            element = model.by_id(int(element_id))
            if element:
                material = element.Material
                if material:
                    materials_map[element.Name or f"Element {element_id}"] = _get_material_details(material, model)
        elif element_type:
            # Get materials for element type
            type_mapping = {v: k for k, v in IFC_ELEMENT_TYPES.items()}
            ifc_type = type_mapping.get(element_type, element_type)
            elements = model.by_type(ifc_type)
            
            for elem in elements:
                material = elem.Material
                if material:
                    mat_name = material.Name if hasattr(material, 'Name') else str(material)
                    if mat_name not in materials_map:
                        materials_map[mat_name] = _get_material_details(material, model)
        else:
            # Get all materials
            materials = model.by_type("IfcMaterial")
            for mat in materials:
                materials_map[mat.Name] = _get_material_details(mat, model)
        
        return {
            "success": True,
            "materials": materials_map,
            "count": len(materials_map)
        }
        
    except Exception as e:
        logger.error(f"Error getting materials: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_element_quantities(
    file_path: str,
    element_id: Optional[str] = None,
    element_type: Optional[str] = None,
    include_aggregates: bool = True
) -> Dict[str, Any]:
    """Get quantities (volume, area, count) for elements."""
    try:
        import ifcopenshell
    except ImportError:
        return {
            "success": False,
            "error": "ifcopenshell not installed"
        }
    
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}"
        }
    
    try:
        model = ifcopenshell.open(file_path)
        quantities = []
        
        if element_id:
            element = model.by_id(int(element_id))
            if element:
                q = _extract_quantities(element, model, include_aggregates)
                if q:
                    quantities.append(q)
        elif element_type:
            type_mapping = {v: k for k, v in IFC_ELEMENT_TYPES.keys()}
            ifc_type = type_mapping.get(element_type, element_type)
            elements = model.by_type(ifc_type)
            
            for elem in elements:
                q = _extract_quantities(elem, model, include_aggregates)
                if q:
                    quantities.append(q)
        else:
            # Get quantities for all elements with quantity info
            for ifc_type in IFC_ELEMENT_TYPES.keys():
                elements = model.by_type(ifc_type)
                for elem in elements:
                    q = _extract_quantities(elem, model, include_aggregates)
                    if q:
                        quantities.append(q)
        
        return {
            "success": True,
            "quantities": quantities,
            "total_count": len(quantities),
            "summary": _summarize_quantities(quantities)
        }
        
    except Exception as e:
        logger.error(f"Error getting quantities: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_element_properties(
    file_path: str,
    element_id: str,
    property_sets: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get detailed properties for a specific element."""
    try:
        import ifcopenshell
    except ImportError:
        return {
            "success": False,
            "error": "ifcopenshell not installed"
        }
    
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}"
        }
    
    try:
        model = ifcopenshell.open(file_path)
        element = model.by_id(int(element_id))
        
        if not element:
            return {
                "success": False,
                "error": f"Element not found: {element_id}"
            }
        
        result = {
            "success": True,
            "element_id": element.id(),
            "element_type": element.is_a(),
            "name": element.Name,
            "properties": {},
            "property_sets": {}
        }
        
        # Get direct attributes
        for attr in element:
            if attr:
                attr_name = attr[0]
                attr_value = attr[1]
                if attr_value is not None:
                    result["properties"][attr_name] = str(attr_value)
        
        # Get property sets
        definitions = element.IsDefinedBy
        
        for definition in definitions:
            if hasattr(definition, 'RelatingPropertyDefinition'):
                pset = definition.RelatingPropertyDefinition
                pset_name = pset.Name if hasattr(pset, 'Name') else "Unknown"
                
                if property_sets and pset_name not in property_sets:
                    continue
                
                result["property_sets"][pset_name] = {}
                
                if hasattr(pset, 'HasProperties'):
                    for prop in pset.HasProperties:
                        prop_name = prop.Name if hasattr(prop, 'Name') else "Unknown"
                        prop_value = _get_property_value(prop)
                        result["property_sets"][pset_name][prop_name] = prop_value
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting properties: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def list_ifc_files(directory: str = ".") -> Dict[str, Any]:
    """List IFC files in a directory."""
    try:
        path = Path(directory)
        if not path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }
        
        ifc_files = list(path.glob("*.ifc")) + list(path.glob("*.IFC"))
        
        files_info = []
        for f in ifc_files:
            stat = f.stat()
            files_info.append({
                "name": f.name,
                "path": str(f),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": stat.st_mtime
            })
        
        return {
            "success": True,
            "files": files_info,
            "count": len(files_info)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Helper functions
def _get_element_property(element, property_name: str):
    """Get a property value from an element."""
    try:
        definitions = element.IsDefinedBy
        for definition in definitions:
            if hasattr(definition, 'RelatingPropertyDefinition'):
                pset = definition.RelatingPropertyDefinition
                if hasattr(pset, 'HasProperties'):
                    for prop in pset.HasProperties:
                        if prop.Name == property_name:
                            return _get_property_value(prop)
    except:
        pass
    return None


def _get_material_details(material, model) -> Dict[str, Any]:
    """Get detailed material information."""
    details = {
        "name": material.Name if hasattr(material, 'Name') else str(material),
        "description": material.Description if hasattr(material, 'Description') and material.Description else None,
        "category": material.Category if hasattr(material, 'Category') and material.Category else None,
    }
    
    # Get material properties
    if hasattr(material, 'MaterialProperties'):
        props = material.MaterialProperties
        for prop in props:
            if hasattr(prop, 'Name'):
                details[prop.Name] = str(prop)
    
    return details


def _extract_quantities(element, model, include_aggregates: bool) -> Optional[Dict[str, Any]]:
    """Extract quantity information from an element."""
    try:
        definitions = element.IsDefinedBy
        
        for definition in definitions:
            if hasattr(definition, 'RelatingPropertyDefinition'):
                pset = definition.RelatingPropertyDefinition
                
                if pset.is_a() == "IfcElementQuantity":
                    q_data = {
                        "element_id": element.id(),
                        "element_name": element.Name,
                        "element_type": element.is_a(),
                        "quantities": {}
                    }
                    
                    if hasattr(pset, 'Quantities'):
                        for q in pset.Quantities:
                            q_name = q.Name if hasattr(q, 'Name') else "Unknown"
                            if q.is_a() == "IfcQuantityVolume":
                                q_data["quantities"][q_name] = {
                                    "value": q.VolumeValue if hasattr(q, 'VolumeValue') else None,
                                    "unit": "m³"
                                }
                            elif q.is_a() == "IfcQuantityArea":
                                q_data["quantities"][q_name] = {
                                    "value": q.AreaValue if hasattr(q, 'AreaValue') else None,
                                    "unit": "m²"
                                }
                            elif q.is_a() == "IfcQuantityLength":
                                q_data["quantities"][q_name] = {
                                    "value": q.LengthValue if hasattr(q, 'LengthValue') else None,
                                    "unit": "m"
                                }
                            elif q.is_a() == "IfcQuantityCount":
                                q_data["quantities"][q_name] = {
                                    "value": q.CountValue if hasattr(q, 'CountValue') else None,
                                    "unit": "count"
                                }
                            elif q.is_a() == "IfcQuantityWeight":
                                q_data["quantities"][q_name] = {
                                    "value": q.WeightValue if hasattr(q, 'WeightValue') else None,
                                    "unit": "kg"
                                }
                    
                    return q_data
    except:
        pass
    
    return None


def _summarize_quantities(quantities: List[Dict]) -> Dict[str, Any]:
    """Create a summary of quantities by element type."""
    summary = {}
    
    for q in quantities:
        elem_type = q.get("element_type", "Unknown")
        if elem_type not in summary:
            summary[elem_type] = {
                "count": 0,
                "total_volume_m3": 0,
                "total_area_m2": 0,
                "total_length_m": 0
            }
        
        summary[elem_type]["count"] += 1
        
        for q_name, q_data in q.get("quantities", {}).items():
            value = q_data.get("value")
            if value is not None:
                unit = q_data.get("unit")
                if unit == "m³":
                    summary[elem_type]["total_volume_m3"] += value
                elif unit == "m²":
                    summary[elem_type]["total_area_m2"] += value
                elif unit == "m":
                    summary[elem_type]["total_length_m"] += value
    
    return summary


def _get_property_value(prop) -> Any:
    """Extract property value from a property object."""
    if hasattr(prop, 'NominalValue'):
        return prop.NominalValue
    elif hasattr(prop, 'Value'):
        return prop.Value
    else:
        return str(prop)


def _get_geometry_summary(model) -> Dict[str, Any]:
    """Get summary of geometry in the model."""
    # This is a simplified version - full geometry processing requires more complex setup
    return {
        "note": "Full geometry analysis requires ifcopenshell.geom setup",
        "elements_with_geometry": "Run extract_elements to get element counts"
    }


# MCP Server Implementation
app = Server("bim-mcp-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available BIM tools."""
    return [
        Tool(
            name="parse_ifc_file",
            description="Parse an IFC file and return basic information including element counts, project structure, and optionally geometry data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the IFC file"
                    },
                    "include_geometry": {
                        "type": "boolean",
                        "description": "Include geometry summary (default: false)",
                        "default": False
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="extract_elements",
            description="Extract building elements from an IFC file with optional filtering by type or property.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the IFC file"
                    },
                    "element_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by element types (e.g., ['Walls', 'Columns', 'Slabs/Floors'])"
                    },
                    "filter_by_property": {
                        "type": "string",
                        "description": "Property name to filter by"
                    },
                    "filter_value": {
                        "type": "string",
                        "description": "Value to filter by"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_element_materials",
            description="Get materials associated with elements in an IFC file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the IFC file"
                    },
                    "element_id": {
                        "type": "string",
                        "description": "Specific element ID to get materials for"
                    },
                    "element_type": {
                        "type": "string",
                        "description": "Element type to get materials for (e.g., 'Walls', 'Columns')"
                    }
                }
            }
        ),
        Tool(
            name="get_element_quantities",
            description="Get quantities (volume, area, count) for elements in an IFC file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the IFC file"
                    },
                    "element_id": {
                        "type": "string",
                        "description": "Specific element ID to get quantities for"
                    },
                    "element_type": {
                        "type": "string",
                        "description": "Element type to get quantities for"
                    },
                    "include_aggregates": {
                        "type": "boolean",
                        "description": "Include aggregated totals (default: true)",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="get_element_properties",
            description="Get detailed properties for a specific element in an IFC file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the IFC file"
                    },
                    "element_id": {
                        "type": "string",
                        "description": "Element ID to get properties for"
                    },
                    "property_sets": {
                        "type": "array",
                        items: {"type": "string"},
                        "description": "Specific property sets to retrieve (optional)"
                    }
                },
                "required": ["file_path", "element_id"]
            }
        ),
        Tool(
            name="list_ifc_files",
            description="List IFC files in a directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search for IFC files (default: current directory)",
                        "default": "."
                    }
                }
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls."""
    
    if name == "parse_ifc_file":
        result = parse_ifc_file(
            file_path=arguments.get("file_path"),
            include_geometry=arguments.get("include_geometry", False)
        )
    elif name == "extract_elements":
        result = extract_elements(
            file_path=arguments.get("file_path"),
            element_types=arguments.get("element_types"),
            filter_by_property=arguments.get("filter_by_property"),
            filter_value=arguments.get("filter_value")
        )
    elif name == "get_element_materials":
        result = get_element_materials(
            file_path=arguments.get("file_path"),
            element_id=arguments.get("element_id"),
            element_type=arguments.get("element_type")
        )
    elif name == "get_element_quantities":
        result = get_element_quantities(
            file_path=arguments.get("file_path"),
            element_id=arguments.get("element_id"),
            element_type=arguments.get("element_type"),
            include_aggregates=arguments.get("include_aggregates", True)
        )
    elif name == "get_element_properties":
        result = get_element_properties(
            file_path=arguments.get("file_path"),
            element_id=arguments.get("element_id"),
            property_sets=arguments.get("property_sets")
        )
    elif name == "list_ifc_files":
        result = list_ifc_files(
            directory=arguments.get("directory", ".")
        )
    else:
        result = {"success": False, "error": f"Unknown tool: {name}"}
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Main entry point for the BIM MCP server."""
    logger.info("Starting BIM MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
