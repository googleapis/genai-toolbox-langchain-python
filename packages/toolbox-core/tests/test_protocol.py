# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import inspect
from inspect import Parameter

import pytest

from toolbox_core.protocol import ParameterSchema


def test_parameter_schema_float():
    """Tests ParameterSchema with type 'float'."""
    schema = ParameterSchema(name="price", type="float", description="The item price")
    expected_type = float
    # Use internal method directly for type check, though testing to_param implicitly tests it
    assert schema._ParameterSchema__get_type() == expected_type

    param = schema.to_param()
    assert isinstance(param, Parameter)
    assert param.name == "price"
    assert param.annotation == expected_type
    assert param.kind == Parameter.POSITIONAL_OR_KEYWORD
    assert param.default == Parameter.empty  # No default specified


def test_parameter_schema_boolean():
    """Tests ParameterSchema with type 'boolean'."""
    schema = ParameterSchema(
        name="is_active", type="boolean", description="Activity status"
    )
    expected_type = bool
    assert schema._ParameterSchema__get_type() == expected_type

    param = schema.to_param()
    assert isinstance(param, Parameter)
    assert param.name == "is_active"
    assert param.annotation == expected_type
    assert param.kind == Parameter.POSITIONAL_OR_KEYWORD


def test_parameter_schema_array_string():
    """Tests ParameterSchema with type 'array' containing strings."""
    item_schema = ParameterSchema(
        name="", type="string", description=""
    )  # Name/desc not relevant for item type
    schema = ParameterSchema(
        name="tags", type="array", description="List of tags", items=item_schema
    )
    # Note: Direct comparison with list[str] might differ slightly depending on Python version's typing internals
    # We check the Parameter annotation which uses the correct runtime representation
    # assert schema._ParameterSchema__get_type() == list[str] # This might fail equality check

    param = schema.to_param()
    assert isinstance(param, Parameter)
    assert param.name == "tags"
    # Check annotation for list of strings. How typing represents this can vary slightly.
    # Using get_origin and get_args is robust across Python versions >= 3.8
    if hasattr(inspect, "get_origin"):  # Python 3.8+
        from typing import get_args, get_origin

        assert get_origin(param.annotation) is list
        assert get_args(param.annotation) == (str,)
    else:  # Fallback for older versions (might need adjustment)
        assert param.annotation == list[str]  # For older typing

    assert param.kind == Parameter.POSITIONAL_OR_KEYWORD


def test_parameter_schema_array_integer():
    """Tests ParameterSchema with type 'array' containing integers."""
    item_schema = ParameterSchema(name="", type="integer", description="")
    schema = ParameterSchema(
        name="scores", type="array", description="List of scores", items=item_schema
    )

    param = schema.to_param()
    assert isinstance(param, Parameter)
    assert param.name == "scores"
    assert param.annotation == list[int]
    assert param.kind == Parameter.POSITIONAL_OR_KEYWORD


def test_parameter_schema_array_no_items_error():
    """Tests that 'array' type raises error if 'items' is None."""
    schema = ParameterSchema(
        name="bad_list", type="array", description="List without item type"
    )

    expected_error_msg = "Unexpected value: type is 'list' but items is None"
    with pytest.raises(Exception, match=expected_error_msg):
        schema._ParameterSchema__get_type()

    # Also test via to_param()
    with pytest.raises(Exception, match=expected_error_msg):
        schema.to_param()


def test_parameter_schema_unsupported_type_error():
    """Tests that an unsupported type raises ValueError."""
    unsupported_type = "datetime"
    schema = ParameterSchema(
        name="event_time", type=unsupported_type, description="When it happened"
    )

    expected_error_msg = f"Unsupported schema type: {unsupported_type}"
    with pytest.raises(ValueError, match=expected_error_msg):
        schema._ParameterSchema__get_type()  # Call the method that raises

    # Also test via to_param()
    with pytest.raises(ValueError, match=expected_error_msg):
        schema.to_param()
