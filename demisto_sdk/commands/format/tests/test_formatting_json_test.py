import os
import shutil

import pytest
from demisto_sdk.commands.format.format_module import format_manager
from demisto_sdk.commands.format.update_incidenttype import \
    IncidentTypesJSONFormat
from demisto_sdk.commands.format.update_indicatortype import \
    IndicatorTypeJSONFormat
from demisto_sdk.tests.constants_test import (
    DASHBOARD_PATH, DESTINATION_FORMAT_DASHBOARD_COPY,
    DESTINATION_FORMAT_INCIDENTFIELD_COPY,
    DESTINATION_FORMAT_INCIDENTTYPE_COPY,
    DESTINATION_FORMAT_INDICATORFIELD_COPY,
    DESTINATION_FORMAT_INDICATORTYPE_COPY, DESTINATION_FORMAT_LAYOUT_COPY,
    INCIDENTFIELD_PATH, INCIDENTTYPE_PATH, INDICATORFIELD_PATH,
    INDICATORTYPE_PATH, INVALID_OUTPUT_PATH, LAYOUT_PATH,
    SOURCE_FORMAT_DASHBOARD_COPY, SOURCE_FORMAT_INCIDENTFIELD_COPY,
    SOURCE_FORMAT_INCIDENTTYPE_COPY, SOURCE_FORMAT_INDICATORFIELD_COPY,
    SOURCE_FORMAT_INDICATORTYPE_COPY, SOURCE_FORMAT_LAYOUT_COPY)


class TestFormattingJson:
    FORMAT_FILES = [
        (SOURCE_FORMAT_INCIDENTFIELD_COPY, DESTINATION_FORMAT_INCIDENTFIELD_COPY, INCIDENTFIELD_PATH, 0),
        (SOURCE_FORMAT_INCIDENTTYPE_COPY, DESTINATION_FORMAT_INCIDENTTYPE_COPY, INCIDENTTYPE_PATH, 0),
        (SOURCE_FORMAT_INDICATORFIELD_COPY, DESTINATION_FORMAT_INDICATORFIELD_COPY, INDICATORFIELD_PATH, 0),
        (SOURCE_FORMAT_INDICATORTYPE_COPY, DESTINATION_FORMAT_INDICATORTYPE_COPY, INDICATORTYPE_PATH, 0),
        (SOURCE_FORMAT_LAYOUT_COPY, DESTINATION_FORMAT_LAYOUT_COPY, LAYOUT_PATH, 0),
        (SOURCE_FORMAT_DASHBOARD_COPY, DESTINATION_FORMAT_DASHBOARD_COPY, DASHBOARD_PATH, 0),
    ]

    @pytest.mark.parametrize('source, target, path, answer', FORMAT_FILES)
    def test_format_file(self, source, target, path, answer):
        os.makedirs(path)
        shutil.copyfile(source, target)
        res = format_manager(input=target, output=target)
        os.remove(target)
        os.rmdir(path)

        assert res is answer

    @pytest.mark.parametrize('invalid_output', [INVALID_OUTPUT_PATH])
    def test_output_file(self, invalid_output):
        try:
            res_invalid = format_manager(input=invalid_output, output=invalid_output)
            assert res_invalid
        except Exception as e:
            assert str(e) == "The given output path is not a specific file path.\nOnly file path can be a output path." \
                             "  Please specify a correct output."


def test_update_id_indicatortype_positive(mocker, tmpdir):
    from demisto_sdk.commands.format import update_indicatortype
    mocker.patch.object(update_indicatortype, 'IndicatorTypeJSONFormat')

    indicator_formater = IndicatorTypeJSONFormat(input='test', output=tmpdir)
    indicator_formater.data = {'id': '1234', 'details': '12345'}
    indicator_formater.update_id()
    assert indicator_formater.data['id'] == indicator_formater.data['details']


def test_update_id_indicatortype_negativ(mocker, tmpdir):
    from demisto_sdk.commands.format import update_indicatortype
    mocker.patch.object(update_indicatortype, 'IndicatorTypeJSONFormat')
    indicator_formater = IndicatorTypeJSONFormat(input='test', output=tmpdir)
    indicator_formater.data = {'id': '1234'}
    try:
        indicator_formater.update_id()
    except Exception as error:
        assert error.args[0] == 'Missing "details" field in file test - add this field manually'


def test_update_id_incidenttype_positive(mocker, tmpdir):
    from demisto_sdk.commands.format import update_incidenttype
    mocker.patch.object(update_incidenttype, 'IncidentTypesJSONFormat')

    incident_formater = IncidentTypesJSONFormat(input='test', output=tmpdir)
    incident_formater.data = {'id': '1234', 'name': '12345'}
    incident_formater.update_id()
    assert incident_formater.data['id'] == incident_formater.data['name']


def test_update_id_incidenttype_negativ(mocker, tmpdir):
    from demisto_sdk.commands.format import update_incidenttype
    mocker.patch.object(update_incidenttype, 'IncidentTypesJSONFormat')
    incident_formater = IncidentTypesJSONFormat(input='test', output=tmpdir)
    incident_formater.data = {'id': '1234'}
    try:
        incident_formater.update_id()
    except Exception as error:
        assert error.args[0] == 'Missing "name" field in file test - add this field manually'
