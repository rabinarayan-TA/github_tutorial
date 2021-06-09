def row_to_list(row):
    row = row.rstrip()
    separated_entries = row.split("\\t")
    if len(separated_entries) == 2:
        return separated_entries
    return None


def convert_to_int(number_with_commas):
    return number_with_commas.replace(",", "")


def get_data_as_numpy_array(clean_data_file_path, num_columns):
    result = np.empty((0, num_columns))
    with open(clean_data_file_path, "r") as f:
        rows = f.readlines()
        for row_num in range(len(rows)):
            try:
                row = np.array([rows[row_num].rstrip("\n").split("\t")], dtype=float)
            except ValueError:
                raise ValueError("Line {0} of {1} is badly formatted".format(row_num + 1, clean_data_file_path))
            else:
                if row.shape != (1, num_columns):
                    raise ValueError(
                        "Line {0} of {1} does not have {2} columns".format(
                            row_num + 1, clean_data_file_path, num_columns
                        )
                    )
            result = np.append(result, row, axis=0)
    return result


import numpy as np


def split_into_training_and_testing_sets(data_array):
    dim = data_array.ndim
    if dim != 2:
        raise ValueError("Argument data_array must be two dimensional. Got {0} dimensional array instead!".format(dim))
    num_rows = data_array.shape[0]
    if num_rows < 2:
        raise ValueError("Argument data_array must have at least 2 rows, it actually has just {0}".format(num_rows))
    num_training = int(0.75 * data_array.shape[0])
    permuted_indices = np.random.permutation(data_array.shape[0])
    return data_array[permuted_indices[:num_training], :], data_array[permuted_indices[num_training:], :]
