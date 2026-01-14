import sys
import subprocess
from PySide6.QtCore import QObject, Signal, QThread

class CLIWorker(QObject):
    finished = Signal(str, str, int)  # status, output, exit code
    progress = Signal(str)  # status update

    def __init__(self, args):
        super().__init__()
        self.args = args

    def run(self):
        self.progress.emit("Running CLI...")
        try:
            # Use sys.executable to ensure correct Python
            process = subprocess.Popen(
                [sys.executable, "-m", "easyeda2kicad"] + self.args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            output = stdout + "\n" + stderr
            status = self.map_status(output, exit_code)
            self.finished.emit(status, output, exit_code)
        except Exception as e:
            self.finished.emit(f"Tool error: {e}", str(e), 1)

    def map_status(self, output, exit_code):
        if "lcsc_id should start by C" in output:
            return "Invalid part number (must start with C)"
        if "Failed to fetch data from EasyEDA API" in output:
            return "No internet or part not found"
        if "the following arguments are required: --lcsc_id" in output:
            return "Missing part number"
        if "Tool error" in output or exit_code != 0:
            return "Unknown failure"
        if "Created Kicad symbol" in output or "Created Kicad footprint" in output or "Created 3D model" in output:
            return "Download complete!"
        return "Done (see details)"
