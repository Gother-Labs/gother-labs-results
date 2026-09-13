from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReplayFigureAccessibilityTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text()

    def test_bess_dispatch_has_text_alternative_and_non_color_encoding(self):
        html = self.read("results/iberian-bess-policy-challenge/run/index.html")
        base_css = self.read("results/iberian-bess-policy-challenge/run/surface.css")
        a11y_css = self.read("results/iberian-bess-policy-challenge/run/accessibility.css")
        self.assertIn('aria-describedby="dispatch-chart-summary"', html)
        self.assertIn('aria-describedby="score-chart-summary"', html)
        self.assertIn("dashed-border charge bars below the zero-dispatch axis", html)
        self.assertIn("stroke-dasharray: 2 2", a11y_css)
        self.assertIn("stroke-dasharray: none", a11y_css)
        self.assertIn("stroke-dasharray: 7 8", base_css)
        self.assertIn("storage-score-dot--accepted", a11y_css)

    def test_bess_replay_announces_user_changes_and_exposes_hourly_text_data(self):
        html = self.read("results/iberian-bess-policy-challenge/run/index.html")
        script = self.read("results/iberian-bess-policy-challenge/run/surface.js")
        css = self.read("results/iberian-bess-policy-challenge/run/accessibility.css")

        self.assertIn('id="scenario-live"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('aria-atomic="true"', html)
        self.assertIn(
            'aria-controls="selected-scenario-summary scenario-hourly-data"',
            html,
        )
        self.assertIn('id="selected-scenario-summary"', html)
        self.assertIn('id="scenario-hourly-data"', html)
        for heading in (
            "Hour",
            "Price (€/MWh)",
            "Charge (MW)",
            "Discharge (MW)",
            "Net action (MW)",
            "SOC (MWh)",
        ):
            self.assertIn(f'<th scope="col">{heading}</th>', html)

        self.assertIn("function renderScenarioText", script)
        self.assertIn("scenario.hours.map", script)
        self.assertIn('return `\n        <tr>\n          <th scope="row">', script)
        self.assertIn("candidate_profit_eur", script)
        self.assertIn("baseline_profit_eur", script)
        self.assertIn("uplift_vs_comparison_baseline_eur", script)
        self.assertIn("regret_eur", script)
        self.assertIn("terminal_soc_error", script)
        self.assertIn("feasibility_penalty", script)
        self.assertIn("simultaneous_power_penalty", script)
        self.assertIn("constraint_breached", script)
        self.assertIn("comparison.valid", script)
        self.assertIn("candidate_discharge_mw) - Number(hour.candidate_charge_mw", script)

        self.assertIn("function announceScenario", script)
        self.assertIn('scenarioLive.textContent = ""', script)
        self.assertIn(
            'scenarioSelect.addEventListener("change", () => renderScenario(scenarioSelect.value, { announce: true }))',
            script,
        )
        self.assertIn("if (announce) announceScenario", script)
        self.assertIn("24 hourly rows updated", script)
        self.assertIn("storage-run-data-table-wrap", css)
        self.assertIn("overflow-x: auto", css)

    def test_qubit_replay_has_text_alternatives_and_redundant_markers(self):
        html = self.read("results/qubit-routing-lightsabre/run/index.html")
        a11y_css = self.read("results/qubit-routing-lightsabre/run/accessibility.css")
        for summary in (
            "qubit-score-summary",
            "qubit-circuit-summary",
            "qubit-topology-summary",
        ):
            self.assertIn(f'aria-describedby="{summary}"', html)
        self.assertIn("baseline marker is a solid circle", html)
        self.assertIn("accepted markers use a dashed ring", html)
        self.assertIn("qubit-run-accepted-ring", a11y_css)
        self.assertIn("qubit-run-step-marker.is-accepted", a11y_css)
        self.assertIn("stroke-dasharray: 2 2", a11y_css)

    def test_rcpsp_visuals_bind_existing_redundant_encodings_to_text(self):
        html = self.read("results/rcpsp-psplib-j30/run/index.html")
        css = self.read("results/rcpsp-psplib-j30/run/surface.css")
        for summary in (
            "rcpsp-score-summary",
            "rcpsp-dispatch-summary",
            "rcpsp-gap-summary",
        ):
            self.assertIn(f'aria-describedby="{summary}"', html)
        self.assertIn("rcpsp-gap-hatch-line", css)
        self.assertIn("stroke-dasharray: 3 4", css)
        self.assertIn("rcpsp-schedule-excess-hatch", css)
        self.assertIn("frozen 80-instance PSPLIB J30 subset, not all RCPSP instances", html)


if __name__ == "__main__":
    unittest.main()
