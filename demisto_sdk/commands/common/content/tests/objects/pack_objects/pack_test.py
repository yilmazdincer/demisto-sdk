from contextlib import contextmanager
from pathlib import Path
from shutil import rmtree
from typing import Tuple

import pytest

from demisto_sdk.commands.common.constants import PACKS_DIR
from demisto_sdk.commands.common.content import Pack
from demisto_sdk.commands.common.content.objects.pack_objects import (
    AgentTool,
    Classifier,
    Contributors,
    Dashboard,
    DocFile,
    IncidentField,
    IncidentType,
    IndicatorField,
    IndicatorType,
    Integration,
    LayoutsContainer,
    PackIgnore,
    PackMetaData,
    Playbook,
    Readme,
    ReleaseNote,
    Report,
    Script,
    SecretIgnore,
    Widget,
)
from demisto_sdk.commands.common.logger import logger
from demisto_sdk.commands.common.tools import src_root

TEST_DATA = src_root() / "tests" / "test_files"
TEST_CONTENT_REPO = TEST_DATA / "content_slim"
PACK = TEST_CONTENT_REPO / PACKS_DIR / "Sample01"
UNIT_TEST_DATA = src_root() / "commands" / "create_artifacts" / "tests" / "data"


@contextmanager
def temp_dir():
    """Create Temp directory for test.

     Open:
        - Create temp directory.

    Close:
        - Delete temp directory.
    """
    temp = UNIT_TEST_DATA / "temp"
    try:
        temp.mkdir(parents=True, exist_ok=True)
        yield temp
    finally:
        rmtree(temp)


@pytest.mark.parametrize(
    argnames="attribute, content_type, items",
    argvalues=[
        ("integrations", (Integration,), 3),
        ("scripts", (Script,), 3),
        ("classifiers", (Classifier,), 1),
        ("playbooks", (Playbook,), 3),
        ("incident_fields", (IncidentField,), 3),
        ("incident_types", (IncidentType,), 3),
        ("indicator_fields", (IndicatorField,), 1),
        ("indicator_types", (IndicatorType,), 3),
        ("reports", (Report,), 3),
        ("dashboards", (Dashboard,), 3),
        ("layouts", (LayoutsContainer,), 3),
        ("widgets", (Widget,), 3),
        ("release_notes", (ReleaseNote,), 1),
        ("tools", (AgentTool,), 1),
        ("doc_files", (DocFile,), 1),
        ("test_playbooks", (Script, Playbook), 2),
    ],
)
def test_generators_detection(attribute: str, content_type: Tuple[type], items: int):
    pack = Pack(PACK)
    generator_as_list = list(pack.__getattribute__(attribute))
    # Check detect all objects
    assert len(generator_as_list) == items
    # Check all objects detected correctly
    for item in generator_as_list:
        assert isinstance(item, content_type)


@pytest.mark.parametrize(
    argnames="attribute, content_type",
    argvalues=[
        ("pack_ignore", PackIgnore),
        ("readme", Readme),
        ("pack_metadata", PackMetaData),
        ("secrets_ignore", SecretIgnore),
        ("contributors", Contributors),
    ],
)
def test_detection(attribute: str, content_type: type):
    pack = Pack(PACK)
    assert isinstance(pack.__getattribute__(attribute), content_type)


def test_sign_pack_exception_thrown(repo, mocker, caplog):
    """
    When:
        - Signing a pack.

    Given:
        - Pack object.
        - No signing executable.

    Then:
        - Verify that exceptions are written to the logger.

    """
    import subprocess

    from demisto_sdk.commands.common.content.objects.pack_objects.pack import Pack

    caplog.set_level("ERROR")
    mocker.patch.object(subprocess, "Popen", autospec=True)

    pack = repo.create_pack("Pack1")
    content_object_pack = Pack(pack.path)
    signer_path = Path("./signer")

    content_object_pack.sign_pack(content_object_pack.path, signer_path)
    assert (
        "Error while trying to sign pack Pack1.\n not enough values to unpack (expected 2, got 0)"
        in caplog.text
    )


def test_sign_pack_error_from_subprocess(
    caplog: pytest.LogCaptureFixture, repo, mocker, fake_process, monkeypatch
):
    """
    When:
        - Signing a pack.

    Given:
        - Pack object.
        - subprocess is failing due to an error.

    Then:
        - Verify that exceptions are written to the logger.
    """
    from demisto_sdk.commands.common.content.objects.pack_objects.pack import Pack

    caplog.set_level("ERROR")

    pack = repo.create_pack("Pack1")
    content_object_pack = Pack(pack.path)
    signer_path = Path("./signer")

    fake_process.register_subprocess(
        f"{signer_path} {pack.path} keyfile base64", stderr=["error"]
    )

    content_object_pack.sign_pack(content_object_pack.path, signer_path)

    assert "Failed to sign pack for Pack1 - b'error\\n'" in caplog.text


def test_sign_pack_success(repo, mocker, fake_process, monkeypatch, caplog):
    """
    When:
        - Signing a pack.

    Given:
        - Pack object.

    Then:
        - Verify that success is written to the logger.

    """

    import demisto_sdk.commands.common.content.objects.pack_objects.pack as pack_class
    from demisto_sdk.commands.common.content.objects.pack_objects.pack import Pack

    pack_class.logger = logger

    pack = repo.create_pack("Pack1")
    content_object_pack = Pack(pack.path)
    signer_path = Path("./signer")

    fake_process.register_subprocess(
        f"{signer_path} {pack.path} keyfile base64", stdout=["success"]
    )

    content_object_pack.sign_pack(content_object_pack.path, signer_path)

    assert f"Signed {content_object_pack.path.name} pack successfully" in caplog.text
