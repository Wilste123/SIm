import json
import unittest

from src.engine.beam_calculations import analyze_beam, calculate_beam_moment_uniform_load, calculate_beam_shear_uniform_load
from src.engine.global_stability import assess_lateral_stability
from src.engine.load_paths import (
    calculate_line_load_kn_per_m,
    calculate_total_area_load,
    detect_unresolved_load_paths,
    distribute_load_to_supports,
)
from src.engine.material_calculations import build_materials_dataframe, summarize_materials
from src.engine.removal_scenarios import apply_removal_scenario, assess_removal_risk
from src.engine.risk_assessment import assess_risk
from src.engine.structural_system import build_structural_model
from src.engine.weather_simulation import WEATHER_SCENARIOS
from src.export.json_export import build_project_payload, export_project_json


class EngineTests(unittest.TestCase):
    def test_uniform_beam_formulas(self):
        self.assertAlmostEqual(calculate_beam_moment_uniform_load(1000.0, 4.0), 2000.0)
        self.assertAlmostEqual(calculate_beam_shear_uniform_load(1000.0, 4.0), 2000.0)

    def test_wall_generation_without_openings(self):
        wall_data = {
            "wall_width_m": 4.8,
            "wall_height_m": 2.4,
            "stud_spacing_mm": 600,
            "stud_dimension": "48x148",
            "top_plates": 2,
            "bottom_plates": 1,
            "has_door": False,
            "door_width_m": 0.0,
            "door_height_m": 0.0,
            "door_left_m": 0.0,
            "has_window": False,
            "window_width_m": 0.0,
            "window_height_m": 0.0,
            "window_left_m": 0.0,
            "window_bottom_m": 0.0,
        }
        from src.engine.wall_generator import generate_wall_layout

        result = generate_wall_layout(wall_data)
        self.assertGreaterEqual(result["regular_stud_count"], 8)
        self.assertEqual(result["extra_stud_count"], 0)

    def test_material_summary_and_json_export(self):
        from src.engine.wall_generator import generate_wall_layout

        wall_data = {
            "wall_width_m": 3.6,
            "wall_height_m": 2.4,
            "stud_spacing_mm": 600,
            "stud_dimension": "48x98",
            "top_plates": 2,
            "bottom_plates": 1,
            "has_door": False,
            "door_width_m": 0.0,
            "door_height_m": 0.0,
            "door_left_m": 0.0,
            "has_window": False,
            "window_width_m": 0.0,
            "window_height_m": 0.0,
            "window_left_m": 0.0,
            "window_bottom_m": 0.0,
        }
        wall_result = generate_wall_layout(wall_data)
        material_df = build_materials_dataframe(wall_data, wall_result, {"48x98": 32})
        summary = summarize_materials(material_df, 10)
        self.assertGreater(summary["cost_with_waste"], summary["total_cost"])

        beam_data = {
            "span_m": 3.0,
            "beam_dimension": "48x198",
            "material_type": "C24 tre",
            "load_type": "jevnt fordelt last",
            "load_kg": 0.0,
            "load_kn_per_m": 1.5,
            "beam_count": 1,
            "center_spacing_mm": 600,
            "deflection_limit": "L/300",
        }
        beam_result = analyze_beam(beam_data)
        risk = assess_risk(wall_data, wall_result, beam_data, beam_result, "Normal belastning")
        payload = build_project_payload(
            project_data={
                "project_name": "Test",
                "building_type": "Bod",
                "location": "",
                "performed_by": "Tester",
                "project_date": "2026-01-01",
                "note": "",
            },
            wall_data=wall_data,
            wall_result=wall_result,
            beam_data=beam_data,
            beam_result=beam_result,
            scenario_name="Normal belastning",
            scenario=WEATHER_SCENARIOS["Normal belastning"],
            risk=risk,
            material_df=material_df,
            material_summary=summary,
            barn_analysis={"overall_risk_level": "yellow"},
        )
        exported = export_project_json(payload)
        parsed = json.loads(exported)
        self.assertEqual(parsed["project"]["project_name"], "Test")
        self.assertIn("material_list", parsed)
        self.assertIn("barn_system_analysis", parsed)

    def test_risk_assessment_red(self):
        from src.engine.wall_generator import generate_wall_layout

        wall_data = {
            "wall_width_m": 4.8,
            "wall_height_m": 2.4,
            "stud_spacing_mm": 600,
            "stud_dimension": "36x68",
            "top_plates": 2,
            "bottom_plates": 1,
            "has_door": True,
            "door_width_m": 1.2,
            "door_height_m": 2.1,
            "door_left_m": 0.5,
            "has_window": True,
            "window_width_m": 1.2,
            "window_height_m": 1.0,
            "window_left_m": 2.5,
            "window_bottom_m": 0.8,
        }
        wall_result = generate_wall_layout(wall_data)
        beam_data = {
            "span_m": 5.0,
            "beam_dimension": "36x68",
            "material_type": "C24 tre",
            "load_type": "jevnt fordelt last",
            "load_kg": 0.0,
            "load_kn_per_m": 5.0,
            "beam_count": 1,
            "center_spacing_mm": 600,
            "deflection_limit": "L/400",
        }
        beam_result = analyze_beam(beam_data)
        risk = assess_risk(wall_data, wall_result, beam_data, beam_result, "Snø + vind")
        self.assertEqual(risk["level"], "red")

    def test_load_path_helpers(self):
        self.assertAlmostEqual(calculate_total_area_load(30.0, 2.0), 60.0)
        self.assertEqual(distribute_load_to_supports(40.0, ["a", "b"]), {"a": 20.0, "b": 20.0})
        self.assertAlmostEqual(calculate_line_load_kn_per_m(2.1, 3.0), 6.3)

    def test_removal_risk_and_lateral_stability(self):
        building_input = {
            "lengde_m": 18.0,
            "bredde_m": 10.0,
            "monehoyde_m": 5.0,
            "gesimshoyde_m": 3.2,
            "antall_etasjer": 1,
            "taktype": "saltak",
            "takvinkel_grader": 27.0,
            "konstruksjonstype": "ukjent",
        }
        system_input = {
            "yttervegger_baerende": True,
            "har_innvendig_baerevegg": True,
            "innervegg_posisjon_m": 5.0,
            "har_stolperekker": False,
            "har_stolper": False,
            "antall_stolper": 0,
            "tak_baeres_av": ["yttervegger", "innervegg"],
            "manuelle_baerelinjer": [],
        }
        load_input = {
            "egenlast_tak_kn_m2": 0.8,
            "snolast_kn_m2": 1.5,
            "nyttelast_gulv_kn_m2": 2.0,
            "lagerlast_kn_m2": 1.0,
            "vindscenario": "storm",
            "usikkerhetsfaktor": 1.2,
        }

        model = build_structural_model(building_input, system_input, load_input)
        unresolved_before = detect_unresolved_load_paths(model)
        self.assertEqual(unresolved_before, [])

        scenario = {
            "scenario_name": "fjern innvendig bærevegg",
            "remove_support_ids": ["innervegg_1"],
            "proposed_replacement": "ingen",
            "replacement_beam_span_m": 6.0,
            "temporary_support_needed": True,
        }

        after = apply_removal_scenario(model, scenario)
        risk = assess_removal_risk(model, after, scenario)
        lateral = assess_lateral_stability(after, scenario)

        self.assertIn(risk["risk_level"], {"yellow", "red"})
        self.assertTrue(risk["requires_engineer"])
        self.assertIn(lateral["risk_level"], {"yellow", "red"})


if __name__ == "__main__":
    unittest.main()
