"""Test Jac cli module."""

import io
import os
import subprocess
import sys


from jaclang.cli import cli
from jaclang.utils.test import TestCase


class JacCliTests(TestCase):
    """Test pass module."""

    def setUp(self) -> None:
        """Set up test."""
        return super().setUp()

    def test_jac_cli_run(self) -> None:
        """Basic test for pass."""
        captured_output = io.StringIO()
        sys.stdout = captured_output

        # Execute the function
        cli.run(self.fixture_abs_path("hello.jac"))

        sys.stdout = sys.__stdout__
        stdout_value = captured_output.getvalue()

        self.assertIn("Hello World!", stdout_value)

    def test_jac_cli_alert_based_err(self) -> None:
        """Basic test for pass."""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.stderr = captured_output

        # Execute the function
        # try:
        cli.enter(self.fixture_abs_path("err2.jac"), entrypoint="speak", args=[])  # type: ignore
        # except Exception as e:
        #     print(f"Error: {e}")

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        stdout_value = captured_output.getvalue()
        # print(stdout_value)
        self.assertIn("Errors occurred", stdout_value)

    def test_jac_ast_tool_pass_template(self) -> None:
        """Basic test for pass."""
        captured_output = io.StringIO()
        sys.stdout = captured_output

        cli.tool("pass_template")

        sys.stdout = sys.__stdout__
        stdout_value = captured_output.getvalue()
        self.assertIn("Sub objects.", stdout_value)
        self.assertGreater(stdout_value.count("def exit_"), 10)

    def test_jac_cmd_line(self) -> None:
        """Basic test for pass."""
        process = subprocess.Popen(
            ["jac"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout_value, _ = process.communicate(input="exit\n")
        self.assertEqual(process.returncode, 0, "Process did not exit successfully")
        self.assertIn("Welcome to the Jac CLI!", stdout_value)

    def test_ast_print(self) -> None:
        """Testing for print AstTool."""
        captured_output = io.StringIO()
        sys.stdout = captured_output

        cli.tool("ir", ["ast", f"{self.fixture_abs_path('hello.jac')}"])

        sys.stdout = sys.__stdout__
        stdout_value = captured_output.getvalue()
        self.assertIn("+-- Token", stdout_value)

    def test_ast_dotgen(self) -> None:
        """Testing for print AstTool."""
        captured_output = io.StringIO()
        sys.stdout = captured_output

        cli.tool("ir", ["ast.", f"{self.fixture_abs_path('hello.jac')}"])

        sys.stdout = sys.__stdout__
        stdout_value = captured_output.getvalue()
        self.assertIn('[label="MultiString"]', stdout_value)

    def test_type_check(self) -> None:
        """Testing for print AstTool."""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        cli.check(f"{self.fixture_abs_path('game1.jac')}")
        sys.stdout = sys.__stdout__
        stdout_value = captured_output.getvalue()
        self.assertIn("Errors: 0, Warnings: 1", stdout_value)

    def test_build_and_run(self) -> None:
        """Testing for print AstTool."""
        if os.path.exists(f"{self.fixture_abs_path('needs_import.jir')}"):
            os.remove(f"{self.fixture_abs_path('needs_import.jir')}")
        captured_output = io.StringIO()
        sys.stdout = captured_output
        cli.build(f"{self.fixture_abs_path('needs_import.jac')}")
        cli.run(f"{self.fixture_abs_path('needs_import.jir')}")
        sys.stdout = sys.__stdout__
        stdout_value = captured_output.getvalue()
        self.assertIn("Errors: 0, Warnings: 0", stdout_value)
        self.assertIn("<module 'pyfunc' from", stdout_value)

    def test_cache_no_cache_on_run(self) -> None:
        """Basic test for pass."""
        process = subprocess.Popen(
            ["jac", "run", f"{self.fixture_abs_path('hello_nc.jac')}", "-nc"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, _ = process.communicate()
        self.assertFalse(
            os.path.exists(
                f"{self.fixture_abs_path(os.path.join('__jac_gen__', 'hello_nc.jbc'))}"
            )
        )
        self.assertIn("Hello World!", stdout)
        process = subprocess.Popen(
            ["jac", "run", f"{self.fixture_abs_path('hello_nc.jac')}", "-c"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, _ = process.communicate()
        self.assertIn("Hello World!", stdout)
        self.assertTrue(
            os.path.exists(
                f"{self.fixture_abs_path(os.path.join('__jac_gen__', 'hello_nc.jbc'))}"
            )
        )
        os.remove(
            f"{self.fixture_abs_path(os.path.join('__jac_gen__', 'hello_nc.jbc'))}"
        )
