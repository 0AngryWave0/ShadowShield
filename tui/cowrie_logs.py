from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Input, DataTable
from rich.text import Text
import re

LOG_PATH = "/home/gogonu/cowrie/var/log/cowrie/cowrie.log"

# Regex patterns
LOGIN_ATTEMPT_PATTERN = re.compile(r"login attempt \[b'(.*?)'/b'(.*?)'\] failed")
IP_PATTERN = re.compile(r'\[(?:HoneyPot|Cowrie)(?:SSH|Telnet)Transport,\d+,([\d.]+)\]')


def parse_logs(filter_ip=None):
    entries = []
    try:
        with open(LOG_PATH, "r") as f:
            for line in f:
                login_match = LOGIN_ATTEMPT_PATTERN.search(line)
                if login_match:
                    user, passwd = login_match.groups()
                    ip_match = IP_PATTERN.search(line)
                    ip = ip_match.group(1) if ip_match else "-"

                    if filter_ip and ip != filter_ip:
                        continue

                    entries.append((ip, user, passwd))
    except FileNotFoundError:
        entries.append(("-", "File not found", "-"))

    return entries[-50:]  # only return latest 50


class CowrieLogViewer(App):
    CSS_PATH = None
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Input(placeholder="Filter by IP and press Enter", id="ip_filter"),
            DataTable(id="log_table"),
            id="main"
        )
        yield Footer()

    def on_mount(self):
        self.refresh_table()

    def refresh_table(self, filter_ip=None):
        table = self.query_one("#log_table", DataTable)
        table.clear()
        table.cursor_type = "row"
        table.add_columns("Source IP", "Username", "Password")
        logs = parse_logs(filter_ip)
        for ip, user, pwd in logs:
            row = [
                Text(ip, style="bold cyan"),
                Text(user, style="bold green"),
                Text(pwd, style="bold red")
            ]
            table.add_row(*row)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        ip = event.value.strip()
        self.refresh_table(filter_ip=ip if ip else None)


if __name__ == "__main__":
    CowrieLogViewer().run()
