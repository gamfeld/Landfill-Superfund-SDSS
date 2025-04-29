
scenario = {
  "id": "Scenario_01",
  "name": "Baseline with Buffer + RNG",
  "spatial_params": {
    "expansion_acreage": 47,            # in acres!
    "height_increase_ft": 70,           # landfill vertical expansion (max 70 -- need to 
    "buffer_installed": True,
    "buffer_geometry": "riparian",      # options: 'none', 'riparian', 'wetland', 'reedbed'
    "buffer_width_m": 30                # optional spatial modifier
  },
  "nonspatial_params": {
    "fill_rate_tpd": 7500,              # tons per day
    "turbine_efficiency_pct": 34.5,     # %
    "flare_nox_rate_g_MMBtu": 0.3,  
    "rng_upgrade": True,
    "abatement_cost_usd": 5000000       # probably need to include qualifiers better lol
  },
    "external_drivers": {
    "policy_pressure": {
      "active": True,
      "constraints": {
        "max_voc_ppb": 150,             # maximum allowed VOC concentration
        "max_pm25_ug_m3": 12,           # maximum PM2.5 concentration in µg/m3
        "emissions_offset_required": 0.3 # 30% GHG reduction relative to baseline
      }
    },
    "legal_constraint_active": {
      "active": True,
      "constraints": {
        "prohibit_expansion_over_aquifer": True,
        "max_landfill_height_ft": 800,  # maximum post-expansion height allowed
        "mandatory_monitoring_install": True
      }
    },
    "waste_import_change_pct": 25
    },

  "metadata": {                         # For all other less-rigid constraints perhaps,
                                        # Just include some notes about them (for now)
    "date_created": "2025-04-29",
    "notes": "Inc. RNG upgrade, aggressive odor control, and moderate fill rate increase"
  }
}
