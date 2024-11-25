from typer.testing import CliRunner

from demisto_sdk.__main__ import app
from TestSuite.test_tools import (
    ChangeCWD,
)

DOC_REVIEW = "doc-review"


def test_spell_integration_dir_valid(repo, mocker, monkeypatch):
    """
    Given
    - a integration directory.

    When
    - Running doc-review on it.

    Then
    - Ensure spell check runs on yml and md files only.
    - Ensure no misspelled words are found.
    """

    pack = repo.create_pack("my_pack")
    integration = pack.create_integration("myint")
    integration.create_default_integration()

    with ChangeCWD(repo.path):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(
            app, [DOC_REVIEW, "-i", integration.path], catch_exceptions=False
        )
        assert all(
            [
                current_str in result.output
                for current_str in [
                    "No misspelled words found ",
                    integration.yml.path,
                    integration.readme.path,
                    integration.description.path,
                ]
            ]
        )
        assert "Words that might be misspelled were found in" not in result.output
        assert integration.code.path not in result.output


def test_spell_integration_invalid(repo):
    """
    Given
    - a integration file path with misspelled words.

    When
    - Running doc-review on it.

    Then
    - Ensure misspelled words are found.
    """

    pack = repo.create_pack("my_pack")
    integration = pack.create_integration("myint")
    integration.create_default_integration()
    yml_content = integration.yml.read_dict()
    yml_content["display"] = "legal words kfawh and some are not"
    yml_content["description"] = "ggghghgh"
    integration.yml.write_dict(yml_content)

    with ChangeCWD(repo.path):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(
            app, [DOC_REVIEW, "-i", integration.yml.path], catch_exceptions=False
        )
        assert "No misspelled words found " not in result.output
        assert "Words that might be misspelled were found in" in result.output
        assert "kfawh" in result.output
        assert "ggghghgh" in result.output


def test_spell_script_invalid(repo, mocker, monkeypatch):
    """
    Given
    - a script file path with misspelled words.

    When
    - Running doc-review on it.

    Then
    - Ensure misspelled words are found.
    """

    pack = repo.create_pack("my_pack")
    script = pack.create_script("myscr")
    script.create_default_script()
    yml_content = script.yml.read_dict()
    yml_content["comment"] = "legal words kfawh and some are not"
    arg_description = (
        yml_content["args"][0].get("description") + " some more ddddddd words "
    )
    yml_content["args"][0]["description"] = arg_description
    script.yml.write_dict(yml_content)

    with ChangeCWD(repo.path):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(
            app, [DOC_REVIEW, "-i", script.yml.path], catch_exceptions=False
        )
    assert "No misspelled words found " not in result.output
    assert "Words that might be misspelled were found in" in result.output
    assert "kfawh" in result.output
    assert "ddddddd" in result.output
    assert "kfawh" in result.output


def test_spell_playbook_invalid(repo, mocker, monkeypatch):
    """
    Given
    - a playbook file path with misspelled words.

    When
    - Running doc-review on it.

    Then
    - Ensure misspelled words are found.
    """

    pack = repo.create_pack("my_pack")
    playbook = pack.create_playbook("myplaybook")
    playbook.create_default_playbook()
    yml_content = playbook.yml.read_dict()
    yml_content["description"] = "legal words kfawh and some are not"
    task_description = (
        yml_content["tasks"]["0"]["task"].get("description")
        + " some more ddddddd words "
    )
    yml_content["tasks"]["0"]["task"]["description"] = task_description
    playbook.yml.write_dict(yml_content)

    with ChangeCWD(repo.path):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(
            app, [DOC_REVIEW, "-i", playbook.yml.path], catch_exceptions=False
        )
        assert "No misspelled words found " not in result.output
        assert "Words that might be misspelled were found in" in result.output
        assert "kfawh" in result.output
        assert "ddddddd" in result.output


def test_spell_readme_invalid(repo, mocker, monkeypatch):
    """
    Given
    - a readme file path with misspelled words and valid and invalid camelCase words.

    When
    - Running doc-review on it.

    Then
    - Ensure misspelled words are found.
    - Ensure legal camelCase words are not marked.
    """

    pack = repo.create_pack("my_pack")
    integration = pack.create_integration("myint")
    integration.create_default_integration()
    integration.readme.write(
        "some weird readme which is not really a word. "
        "and should be noted bellow - also hghghghgh\n"
        "GoodCase stillGoodCase notGidCase"
    )

    with ChangeCWD(repo.path):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(
            app, [DOC_REVIEW, "-i", integration.readme.path], catch_exceptions=False
        )
        assert all(
            [
                current_str in result.output
                for current_str in [
                    "Words that might be misspelled were found in",
                    "readme",
                    "hghghghgh",
                    "notGidCase",
                ]
            ]
        )
        assert all(
            [
                current_str not in result.output
                for current_str in [
                    "No misspelled words found ",
                    "GoodCase",
                    "stillGoodCase",
                ]
            ]
        )


def test_review_release_notes_valid(repo, mocker, monkeypatch):
    """
    Given
    - an valid rn file:
        - Line start with capital letter.
        - Line has a period in the end.
        - Line does not use the word 'bug'.
        - Line has no misspelled word.
        - Line fits a template.

    When
    - Running doc-review on it.

    Then
    - Ensure no errors are found.
    """

    pack = repo.create_pack("my_pack")
    valid_rn = (
        "\n"
        "#### Integrations\n"
        "##### Demisto\n"
        " - Fixed an issue where the ***ip*** command failed when unknown categories were returned.\n"
    )
    rn = pack.create_release_notes(version="1.1.0", content=valid_rn)
    with ChangeCWD(repo.path):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(app, [DOC_REVIEW, "-i", rn.path], catch_exceptions=False)
        assert all(
            [
                current_str in result.output
                for current_str in [
                    "No misspelled words found",
                    f" - Release notes {rn.path} match a known template.",
                ]
            ]
        )


def test_review_release_notes_invalid(repo, mocker, monkeypatch):
    """
    Given
    - an invalid rn file:
        - Line does not start with capital letter.
        - Line does not have period in the end.
        - Line uses the word 'bug'.
        - Line has a misspelled word.
        - Line does not fit any template.

    When
    - Running doc-review on it.

    Then
    - Ensure misspelled words are found and correct fix is suggested.
    - Ensure all errors are found.
    """

    pack = repo.create_pack("my_pack")
    valid_rn = (
        "\n"
        "#### Integrations\n"
        "##### Demisto\n"
        " - fixed a bug where the ***ip*** commanda failed when unknown categories were returned\n"
    )
    rn = pack.create_release_notes(version="1.1.0", content=valid_rn)
    with ChangeCWD(repo.path):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(app, [DOC_REVIEW, "-i", rn.path], catch_exceptions=False)

        assert all(
            [
                current_str in result.output
                for current_str in [
                    'Notes for the line: "fixed a bug where the ***ip*** commanda '
                    'failed when unknown categories were returned"',
                    "Line #4 is not using one of our templates,",
                    'Refrain from using the word "bug", use "issue" instead.',
                    "Line #4 should end with a period (.)",
                    "Line #4 should start with capital letter.",
                    "commanda - did you mean:",
                    "command",
                ]
            ]
        )


def test_templates_print(repo, mocker, monkeypatch):
    """
    Given
    - templates flag
    When
    - Running doc-review with it.

    Then
    - Ensure templates are printed.
    - Ensure no additional checks run.
    """

    with ChangeCWD(repo.path):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(app, [DOC_REVIEW, "--templates"], catch_exceptions=False)
        assert "General Pointers About Release Notes:" in result.output
        assert "Checking spelling on" not in result.output
