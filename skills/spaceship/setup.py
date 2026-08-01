from __future__ import annotations

from setuptools import setup
from setuptools.command.build_py import build_py

_SOURCE_ONLY_STARTER_MODULES = {
    "spaceship_safe_agent_cli.commands.auth",
    "spaceship_safe_agent_cli.commands.demo",
    "spaceship_safe_agent_cli.commands.jobs",
    "spaceship_safe_agent_cli.oauth_tokens",
    "spaceship_safe_agent_cli.project_config",
}


class SpaceshipBuildPy(build_py):
    def find_all_modules(self) -> list[tuple[str, str, str]]:
        return [
            module
            for module in super().find_all_modules()
            if f"{module[0]}.{module[1]}" not in _SOURCE_ONLY_STARTER_MODULES
        ]


setup(cmdclass={"build_py": SpaceshipBuildPy})
