"""
Thailand TGO Emission Factors for Embodied Carbon Calculations.

Source: Thailand Greenhouse Gas Organization (TGO)
These factors are based on Thai-specific data and should be used for projects
in Thailand. For international projects, consider using region-specific factors.

Last Updated: 2024
"""

TGO_EMISSION_FACTORS = {
    # Concrete and Cement Products (kgCO2e/unit)
    "concrete": {
        "description": "Concrete products",
        "unit": "m³",
        "factors": {
            "concrete_standard": {
                "name": "Standard Concrete (C30/37)",
                "factor": 397.0,  # kgCO2e/m³
                "source": "TGO 2024",
                "notes": "Average Thai concrete mix"
            },
            "concrete_high_strength": {
                "name": "High Strength Concrete (C50/60)",
                "factor": 475.0,  # kgCO2e/m³
                "source": "TGO 2024",
                "notes": "Higher cement content"
            },
            "concrete_low_strength": {
                "name": "Low Strength Concrete (C20/25)",
                "factor": 330.0,  # kgCO2e/m³
                "source": "TGO 2024",
                "notes": "Lower cement content"
            },
            "concrete_recycled": {
                "name": "Recycled Aggregate Concrete",
                "factor": 290.0,  # kgCO2e/m³
                "source": "TGO 2024",
                "notes": "With 30% recycled aggregates"
            },
            "concrete_ready_mix": {
                "name": "Ready-Mix Concrete (Average)",
                "factor": 410.0,  # kgCO2e/m³
                "source": "TGO 2024",
                "notes": "Average ready-mix delivery"
            }
        }
    },
    
    # Cement
    "cement": {
        "description": "Cement types",
        "unit": "tonne",
        "factors": {
            "opc_type_i": {
                "name": "Ordinary Portland Cement (Type I)",
                "factor": 927.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "General purpose cement"
            },
            "opc_type_ii": {
                "name": "Portland Pozzolana Cement (PPC)",
                "factor": 685.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Blended cement with pozzolanic materials"
            },
            "opc_type_v": {
                "name": "Portland Slag Cement (PSC)",
                "factor": 590.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Blended cement with blast furnace slag"
            },
            "white_cement": {
                "name": "White Cement",
                "factor": 1150.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Higher process emissions"
            }
        }
    },
    
    # Steel Products
    "steel": {
        "description": "Steel and metal products",
        "unit": "tonne",
        "factors": {
            "steel_rebar": {
                "name": "Steel Rebar (Deformed Bars)",
                "factor": 1580.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Thai domestic production"
            },
            "steel_section": {
                "name": "Steel Sections (H, I, C shapes)",
                "factor": 2100.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Structural steel sections"
            },
            "steel_plate": {
                "name": "Steel Plate/Sheet",
                "factor": 2350.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Hot rolled plate"
            },
            "steel_tube": {
                "name": "Steel Tube/Pipe",
                "factor": 2450.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Hollow sections"
            },
            "steel_recycled": {
                "name": "Recycled Steel (EAF)",
                "factor": 680.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Electric Arc Furnace production"
            },
            "stainless_steel": {
                "name": "Stainless Steel",
                "factor": 4500.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "304/316 grade"
            },
            "steel_roofing": {
                "name": "Steel Roofing Sheet",
                "factor": 1950.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Color coated"
            }
        }
    },
    
    # Aggregates
    "aggregates": {
        "description": "Aggregate materials",
        "unit": "tonne",
        "factors": {
            "sand": {
                "name": "Sand (Natural)",
                "factor": 7.5,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "River sand extraction"
            },
            "gravel": {
                "name": "Gravel/Crushed Stone",
                "factor": 12.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Crushed rock aggregates"
            },
            "recycled_aggregate": {
                "name": "Recycled Concrete Aggregate",
                "factor": 5.5,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "From demolition concrete"
            },
            "manufactured_sand": {
                "name": "Manufactured Sand (M-Sand)",
                "factor": 15.0,  # kgCO2e/tonne
                "source": "TGO 2024",
                "notes": "Crushed rock sand"
            }
        }
    },
    
    # Bricks and Blocks
    "bricks": {
        "description": "Brick and block products",
        "unit": "piece",
        "factors": {
            "clay_brick": {
                "name": "Clay Brick (Traditional)",
                "factor": 0.52,  # kgCO2e/piece
                "source": "TGO 2024",
                "notes": "Standard clay brick (~2.5kg)"
            },
            "concrete_block": {
                "name": "Concrete Block (200mm)",
                "factor": 3.2,  # kgCO2e/piece
                "source": "TGO 2024",
                "notes": "Hollow concrete block"
            },
            "autoclaved_block": {
                "name": "Autoclaved Aerated Concrete Block",
                "factor": 1.8,  # kgCO2e/piece
                "source": "TGO 2024",
                "notes": "Lightweight AAC block"
            },
            "silicate_brick": {
                "name": "Silicate Brick",
                "factor": 0.65,  # kgCO2e/piece
                "source": "TGO 2024",
                "notes": "Sand-lime brick"
            }
        }
    },
    
    # Glass
    "glass": {
        "description": "Glass products",
        "unit": "m²",
        "factors": {
            "float_glass_4mm": {
                "name": "Float Glass (4mm)",
                "factor": 12.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Clear float glass"
            },
            "float_glass_6mm": {
                "name": "Float Glass (6mm)",
                "factor": 18.8,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Clear float glass"
            },
            "tempered_glass": {
                "name": "Tempered Safety Glass",
                "factor": 24.0,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Heat treated"
            },
            "laminated_glass": {
                "name": "Laminated Glass",
                "factor": 28.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Two layers with PVB"
            },
            "insulated_glass": {
                "name": "Insulated Glass Unit (IGU)",
                "factor": 35.0,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Double glazed unit"
            }
        }
    },
    
    # Insulation Materials
    "insulation": {
        "description": "Thermal insulation products",
        "unit": "m²",
        "factors": {
            "eps_25mm": {
                "name": "EPS (25mm)",
                "factor": 3.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Expanded polystyrene"
            },
            "xps_25mm": {
                "name": "XPS (25mm)",
                "factor": 5.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Extruded polystyrene"
            },
            "mineral_wool_50mm": {
                "name": "Mineral Wool (50mm)",
                "factor": 8.0,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Stone wool insulation"
            },
            "glass_wool_50mm": {
                "name": "Glass Wool (50mm)",
                "factor": 6.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Fiberglass insulation"
            },
            "polyurethane_25mm": {
                "name": "PU Foam (25mm)",
                "factor": 7.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Polyurethane spray foam"
            }
        }
    },
    
    # Wood and Wood Products
    "wood": {
        "description": "Wood and timber products",
        "unit": "m³",
        "factors": {
            "timber_solid": {
                "name": "Solid Timber (Softwood)",
                "factor": -650.0,  # kgCO2e/m³ (negative = biogenic carbon sequestration)
                "source": "TGO 2024",
                "notes": "Includes biogenic carbon"
            },
            "timber_hardwood": {
                "name": "Hardwood Timber",
                "factor": -850.0,  # kgCO2e/m³
                "source": "TGO 2024",
                "notes": "Tropical hardwood"
            },
            "plywood": {
                "name": "Plywood",
                "factor": 450.0,  # kgCO2e/m³
                "source": "TGO 2024",
                "notes": "Structural plywood"
            },
            "mdf": {
                "name": "MDF",
                "factor": 680.0,  # kgCO2e/m³
                "source": "TGO 2024",
                "notes": "Medium density fiberboard"
            },
            "osb": {
                "name": "OSB",
                "factor": 350.0,  # kgCO2e/m³
                "source": "TGO 2024",
                "notes": "Oriented strand board"
            }
        }
    },
    
    # Aluminum
    "aluminum": {
        "description": "Aluminum products",
        "unit": "kg",
        "factors": {
            "aluminum_extrusion": {
                "name": "Aluminum Extrusion",
                "factor": 8.5,  # kgCO2e/kg
                "source": "TGO 2024",
                "notes": "Window/door frames"
            },
            "aluminum_sheet": {
                "name": "Aluminum Sheet",
                "factor": 9.2,  # kgCO2e/kg
                "source": "TGO 2024",
                "notes": "Cladding sheets"
            },
            "aluminum_recycled": {
                "name": "Recycled Aluminum",
                "factor": 1.2,  # kgCO2e/kg
                "source": "TGO 2024",
                "notes": "Secondary aluminum"
            }
        }
    },
    
    # Roofing Materials
    "roofing": {
        "description": "Roofing materials",
        "unit": "m²",
        "factors": {
            "tile_concrete": {
                "name": "Concrete Roof Tile",
                "factor": 8.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Concrete roof tile"
            },
            "tile_clay": {
                "name": "Clay Roof Tile",
                "factor": 6.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Terracotta roof tile"
            },
            "metal_roofing": {
                "name": "Metal Roofing (Steel)",
                "factor": 7.0,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Steel sheet roofing"
            },
            "membrane_roofing": {
                "name": "Roofing Membrane (TPO)",
                "factor": 5.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Thermoplastic membrane"
            }
        }
    },
    
    # Flooring Materials
    "flooring": {
        "description": "Flooring materials",
        "unit": "m²",
        "factors": {
            "tile_ceramic": {
                "name": "Ceramic Tile",
                "factor": 10.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Glazed ceramic floor tile"
            },
            "tile_porcelain": {
                "name": "Porcelain Tile",
                "factor": 12.0,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Full body porcelain"
            },
            "marble_tile": {
                "name": "Marble Tile",
                "factor": 25.0,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Natural stone marble"
            },
            "granite_tile": {
                "name": "Granite Tile",
                "factor": 22.0,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Natural stone granite"
            },
            "vinyl_flooring": {
                "name": "Vinyl Flooring (PVC)",
                "factor": 5.8,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "LVT vinyl tile"
            },
            "rubber_flooring": {
                "name": "Rubber Flooring",
                "factor": 7.2,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Recycled rubber"
            }
        }
    },
    
    # Wall Finishes
    "wall_finishes": {
        "description": "Wall finishing materials",
        "unit": "m²",
        "factors": {
            "plaster_thin": {
                "name": "Thin Plaster/Putty",
                "factor": 0.8,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Interior wall finish"
            },
            "plaster_render": {
                "name": "Cement Render",
                "factor": 4.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Exterior render"
            },
            "paint_emulsion": {
                "name": "Emulsion Paint",
                "factor": 1.2,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Water-based interior paint"
            },
            "paint_textured": {
                "name": "Textured Paint",
                "factor": 2.0,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Decorative textured coating"
            },
            "wallpaper": {
                "name": "Wallpaper",
                "factor": 1.5,  # kgCO2e/m²
                "source": "TGO 2024",
                "notes": "Paper-based wallpaper"
            }
        }
    },
    
    # Transport Factors (per tonne-km)
    "transport": {
        "description": "Transportation emission factors",
        "unit": "tonne-km",
        "factors": {
            "road_diesel": {
                "name": "Road Transport (Diesel Truck)",
                "factor": 0.068,  # kgCO2e/tonne-km
                "source": "TGO 2024",
                "notes": "Average diesel truck"
            },
            "road_gasoline": {
                "name": "Road Transport (Gasoline)",
                "factor": 0.095,  # kgCO2e/tonne-km
                "source": "TGO 2024",
                "notes": "Gasoline vehicle"
            },
            "rail": {
                "name": "Rail Transport",
                "factor": 0.022,  # kgCO2e/tonne-km
                "source": "TGO 2024",
                "notes": "Electric rail"
            },
            "ship": {
                "name": "Sea Transport",
                "factor": 0.016,  # kgCO2e/tonne-km
                "source": "TGO 2024",
                "notes": "Maritime shipping"
            }
        }
    }
}


def get_emission_factors(category: str = None) -> dict:
    """Get emission factors by category or all factors."""
    if category:
        return TGO_EMISSION_FACTORS.get(category, {})
    return TGO_EMISSION_FACTORS


def get_factor(category: str, material_key: str) -> float:
    """Get a specific emission factor."""
    category_data = TGO_EMISSION_FACTORS.get(category, {})
    factors = category_data.get("factors", {})
    material = factors.get(material_key, {})
    return material.get("factor", 0.0)
