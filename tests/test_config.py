import os
from pathlib import Path

import pytest

from quantbench_crew.config import init_env_file, load_config, load_env_file


def test_load_yaml_config() -> None:
    config = load_config(Path("configs/agents.yaml"))

    assert "agents" in config
    assert "quant_scout" in config["agents"]


def test_load_env_file_sets_missing_values_without_overriding(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "# local secrets",
                "OPENAI_API_KEY=sk-local # inline comment",
                "export GEMINI_API_KEY='g-local'",
                'DEEPSEEK_API_KEY="d-local"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("OPENAI_API_KEY", "already-set")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    loaded = load_env_file(env_file)

    assert loaded["OPENAI_API_KEY"] == "sk-local"
    assert loaded["GEMINI_API_KEY"] == "g-local"
    assert loaded["DEEPSEEK_API_KEY"] == "d-local"
    assert loaded["OPENAI_API_KEY"] != "already-set"
    assert os.environ["OPENAI_API_KEY"] == "already-set"
    assert os.environ["GEMINI_API_KEY"] == "g-local"


def test_init_env_file_copies_template_and_refuses_overwrite(tmp_path) -> None:
    template = tmp_path / ".env.example"
    target = tmp_path / ".env"
    template.write_text("OPENAI_API_KEY=\n", encoding="utf-8")

    created = init_env_file(target, template=template)

    assert created == target
    assert target.read_text(encoding="utf-8") == "OPENAI_API_KEY=\n"
    with pytest.raises(FileExistsError):
        init_env_file(target, template=template)
