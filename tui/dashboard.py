from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static, DataTable
from textual.reactive import reactive

from core.monitor import read_eve
from core.state import blocked_ips
from datetime import datetime


class ShadowShield(App):
    CSS_PATH = "tui/dashboard.css"
    alerts = reactive([])

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("🛡️  ShadowShield Dashboard", id="title"),
            Horizontal(
                DataTable(id="alerts"),
                Static("", id="side-info")
            )
        )
        yield Footer()

    def on_mount(self):
        alerts_table = self.query_one("#alerts", DataTable)
        alerts_table.add_columns("Time", "Signature", "Src IP", "Dst IP")
        self.set_interval(5, self.refresh_alerts)

    def refresh_alerts(self):
        alerts_table = self.query_one("#alerts", DataTable)
        side_info = self.query_one("#side-info", Static)

        alerts_table.clear()
        all_logs = read_eve()
        recent_alerts = [a for a in all_logs if a.get("event_type") == "alert"][-10:]

        for entry in recent_alerts:
            ts = entry.get("timestamp")
            time_str = datetime.fromisoformat(ts).strftime("%H:%M:%S") if ts else "—"
            sig = entry["alert"]["signature"]
            src = entry.get("src_ip", "—")
            dst = entry.get("dest_ip", "—")
            alerts_table.add_row(time_str, sig, src, dst)

        side_info.update(f"🚫 Blocked IPs: [bold red]{len(blocked_ips)}[/bold red]")

if __name__ == "__main__":
    app = ShadowShield()
    app.run()
