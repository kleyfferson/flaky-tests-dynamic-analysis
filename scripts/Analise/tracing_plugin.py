import os
from pathlib import Path
from Analise.TestResult import TestResult

def pytest_configure(config):
    if os.environ.get("AUTO_TRACE") == "True":
        plugin = TestResult(
            trace=True,
            prof=os.environ.get("AUTO_PROF") == "True",
            outputDir=os.environ.get("AUTO_OUTPUT_DIR", "."),
            testName=os.environ.get("AUTO_TEST_NAME", ""),
            automation_root=Path(os.environ.get("AUTO_AUTOMATION_ROOT", ".")) if os.environ.get("AUTO_AUTOMATION_ROOT") else None,
            project_root_dir=os.environ.get("AUTO_PROJECT_ROOT", "")
        )
        config.pluginmanager.register(plugin, name="auto_trace_plugin")
