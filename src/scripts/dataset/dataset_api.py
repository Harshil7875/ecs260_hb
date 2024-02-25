import fetch
import update
import test

bugs_line_tags = ["single-line", "multi-line"]
error_types_tags = ["invalid-condition", "invalid-format-string", "memory-error"]


# search buggy repos
def search_repositories_by_tags(bugs_line_tag:str, error_types_tag:str) -> []:
    return fetch.search_repos(bugs_line_tag, error_types_tag)


# download repos data
def download_buggy_data_by_repo(repository_name:str):
    fetch.download_data_by_repo(repository_name)

def download_buggy_data_by_tags(bugs_line_tag:str, error_types_tag:str):
    fetch.download_data_by_tags(bugs_line_tag, error_types_tag)


# get buggy code/function/files
def get_buggy_function_by_repo(repository_name:str) -> {}:
    return fetch.get_buggy_functions(repository_name)

def get_buggy_function_with_label_repo(repository_name:str) -> {}:
    return fetch.get_buggy_functions_with_label(repository_name)

def get_fixed_function_by_repo(repository_name:str) -> {}:
    return fetch.get_fixed_functions(repository_name)

def get_fixed_function_with_label_repo(repository_name:str) -> {}:
    return fetch.get_fixed_functions_with_label(repository_name)

def get_buggy_function_in_batch(repository_list:[]) -> {}:
    return fetch.get_buggy_functions_in_batch(repository_list)

def get_complete_buggy_codes_by_repo(repository_name:str) -> {}:
    return fetch.get_complete_buggy_codes_by_repo(repository_name)

def get_complete_fixed_codes_by_repo(repository_name:str) -> {}:
    return fetch.get_complete_fixed_codes_by_repo(repository_name)

def get_complete_buggy_codes_in_batch(repository_list:[]) -> {}:
    return fetch.get_complete_buggy_codes_in_batch(repository_list)


# fix buggy code and test
def test_buggy_codes(repository_name:str, fixed_code:str) -> test.TestResult:
    update.update_buggy_code(repository_name, fixed_code)
    build_res = test.build_repo(repository_name)
    test_res = test.TestCasesResult(-1.0, [], [])
    if build_res:
        test_res = test.test_repo(repository_name)
    update.restore_buggy_code(repository_name)
    return test.TestResult(repository_name, build_res, test_res)

def test_default_buggy_codes(repository_name:str) -> test.TestResult:
    build_res = test.build_repo(repository_name)
    test_res = test.test_repo(repository_name)
    return test.TestResult(repository_name, build_res, test_res)

def test_default_fixed_codes(repository_name:str) -> test.TestResult:
    build_res = test.build_repo(repository_name, False)
    test_res = test.test_repo(repository_name, False)
    return test.TestResult(repository_name, build_res, test_res)

