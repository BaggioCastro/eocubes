#api_check
import datetime



def check_that(condition, local_msg=None, msg=None):
    if not condition:
        caller = check_identify_caller()
        if not msg:
            msg = "Invalid parameter"
        if local_msg:
            msg = f"{caller}: {local_msg} - {msg}"
        else:
            msg = f"{caller}: {msg}"
        raise ValueError(msg)


def check_identify_caller():
    import inspect
    frame = inspect.currentframe()
    while frame.f_back:
        frame = frame.f_back
    caller = frame.f_globals["__name__"]
    return caller


def check_null(x, local_msg=None, msg=None):
    check_that(x is not None, local_msg=local_msg, msg=msg)


def check_na(x, allow_na=False, local_msg=None, msg=None):
    if not allow_na:
        check_that(not any([item is None for item in x]), local_msg=local_msg, msg=msg)


def check_names(x, is_named=True, is_unique=True, local_msg=None, msg=None):
    if len(x) == 0:
        return
    if is_named:
        check_that(all([item is not None for item in x.keys()]), local_msg=local_msg, msg="Names cannot be None")
        if is_unique:
            check_that(len(x.keys()) == len(set(x.keys())), local_msg=local_msg, msg="Names must be unique")
    else:
        check_that(all([item is None for item in x.keys()]), local_msg=local_msg, msg="Names must be None")


def check_length(x, len_min=0, len_max=2**31 - 1, local_msg=None, msg=None):
    check_that(len(x) >= len_min and len(x) <= len_max, local_msg=local_msg, msg=msg)


def check_apply(x, fn_check, local_msg=None, msg=None):
    check_that(callable(fn_check), local_msg=local_msg, msg=msg)
    for item in x:
        fn_check(item)


def check_lgl_type(x, local_msg=None, msg=None):
    check_that(isinstance(x, bool), local_msg=local_msg, msg=msg)


def check_num_type(x, is_integer=False, local_msg=None, msg=None):
    check_that(isinstance(x, (int, float)), local_msg=local_msg, msg=msg)
    if is_integer:
        check_that(isinstance(x, int), local_msg=local_msg, msg=msg)


def check_chr_type(x, local_msg=None, msg=None):
    check_that(isinstance(x, str), local_msg=local_msg, msg=msg)


def check_lst_type(x, local_msg=None, msg=None):
    check_that(isinstance(x, list), local_msg=local_msg, msg=msg)


def check_lgl(x, allow_na=False, len_min=0, len_max=2**31 - 1, allow_null=False, is_named=False, local_msg=None, msg=None):
    if allow_null and x is None:
        return
    check_null(x, local_msg=local_msg, msg=msg)
    check_lgl_type(x, local_msg=local_msg, msg=msg)
    check_length(x, len_min=len_min, len_max=len_max, local_msg=local_msg, msg=msg)
    if not allow_na:
        check_na(x, local_msg=local_msg, msg=msg)
    check_names(x, is_named=is_named, local_msg=local_msg, msg=msg)


def check_num(x, allow_na=False, min_val=-float('inf'), max_val=float('inf'), exclusive_min=-float('inf'), exclusive_max=float('inf'), len_min=0, len_max=2**31 - 1, allow_null=False, is_integer=False, is_named=False, is_odd=False, tolerance=0, local_msg=None, msg=None):
    if allow_null and x is None:
        return
    check_null(x, local_msg=local_msg, msg=msg)
    check_num_type(x, is_integer=is_integer, local_msg=local_msg, msg=msg)
    check_length(x, len_min=len_min, len_max=len_max, local_msg=local_msg, msg=msg)
    if not allow_na:
        check_na(x, local_msg=local_msg, msg=msg)
    check_names(x, is_named=is_named, local_msg=local_msg, msg=msg)
    if is_odd:
        check_that(x % 2 != 0, local_msg=local_msg, msg=msg)
    check_that(min_val <= x <= max_val, local_msg=local_msg, msg=msg)
    check_that(exclusive_min < x < exclusive_max, local_msg=local_msg, msg=msg)


def check_chr(x, allow_na=False, allow_empty=True, allow_duplicate=True, len_min=0, len_max=2**31 - 1, allow_null=False, is_named=False, has_unique_names=True, regex=None, local_msg=None, msg=None):
    if allow_null and x is None:
        return
    check_null(x, local_msg=local_msg, msg=msg)
    check_chr_type(x, local_msg=local_msg, msg=msg)
    check_length(x, len_min=len_min, len_max=len_max, local_msg=local_msg, msg=msg)
    if not allow_na:
        check_na(x, local_msg=local_msg, msg=msg)
    if not allow_empty:
        check_that(len(x) > 0, local_msg=local_msg, msg=msg)
    if not allow_duplicate:
        check_that(len(x) == len(set(x)), local_msg=local_msg, msg=msg)
    check_names(x, is_named=is_named, has_unique_names=has_unique_names, local_msg=local_msg, msg=msg)
    if regex:
        import re
        check_that(bool(re.match(regex, x)), local_msg=local_msg, msg=msg)


def check_bbox_format(bbox, msg="Invalid bounding box parameter!"):
    if not (isinstance(bbox, list) and len(bbox) == 4 and all(isinstance(coord, (int, float)) for coord in bbox)):
        raise ValueError(msg)
    


def validate_dates(start_date, end_date):
    try:
        _start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        _end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        check_that(_end_date > _start_date, msg="Start date must be before end date.")
        return start_date, end_date
    except ValueError:
        raise AttributeError("Dates are not correctly formatted, should be %Y-%m-%d")
    
def check_date_format(date_string, msg="Incorrect date format, should be YYYY-MM-DD"):
    import datetime
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        raise ValueError(msg)


def check_date_range(start_date: str, end_date: str):
    """
    Check if the start_date and end_date are correctly formatted and if the start_date is before end_date.

    Parameters:
    - start_date (str): Start date formatted as "yyyy-mm-dd".
    - end_date (str): End date formatted as "yyyy-mm-dd".

    Raises:
    - ValueError: If the start date is greater than the end date or if the dates are not correctly formatted.
    """
    try:
        _start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        _end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        if _end_date <= _start_date:
            raise ValueError("Start date is greater than end date!")
    except ValueError:
        raise AttributeError("Dates are not correctly formatted, should be %Y-%m-%d")