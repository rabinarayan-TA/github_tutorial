import numpy as np
import pytest
from os import get_blocking
from preprocessing_helper import (
    convert_to_int,
    get_data_as_numpy_array,
    split_into_training_and_testing_sets,
)


def test_on_string_with_one_comma():
    test_argument = "2,081"
    expected = 2081
    actual = convert_to_int(test_argument)
    # Format the string with the actual return value
    message = "convert_to_int('2,081') should return the int 2081, but it actually returned {0}".format(actual)
    # Write the assert statement which prints message on failure
    assert actual == expected, message


# def test_on_clean_file():
#    expected = np.array([[2081.0, 314942.0], [1059.0, 186606.0], [1148.0, 206186.0]])
#    actual = get_data_as_numpy_array("example_clean_data.txt", num_columns=2)
#    message = "Expected return value: {0}, Actual return value: {1}".format(expected, #actual)
#    # Complete the assert statement
#    assert actual == pytest.approx(expected), message


import numpy as np
import pytest
from preprocessing_helper import split_into_training_and_testing_sets, row_to_list


def test_on_one_row():
    test_argument = np.array([[1382.0, 390167.0]])
    # Store information about raised ValueError in exc_info
    with pytest.raises(ValueError) as exc_info:
        split_into_training_and_testing_sets(test_argument)
    expected_error_msg = "Argument data_array must have at least 2 rows, it actually has just 1"
    # Check if the raised ValueError contains the correct message
    assert exc_info.match(expected_error_msg)


def test_on_no_tab_no_missing_value():  # (0, 0) boundary value
    # Assign actual to the return value for the argument "123\n"
    actual = row_to_list("123\n")
    assert actual is None, "Expected: None, Actual: {0}".format(actual)
