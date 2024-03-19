import fetch
import update
import test
from typing import List, Dict
from enum import Enum

bugs_line_tags = ["single-line", "multi-line"]
error_types_tags = ["invalid-condition", "invalid-format-string", "memory-error"]


class RepairScenario(Enum):
    REPAIR_SCENARIO_1 = 1  # single-line - invalid-condition
    REPAIR_SCENARIO_2 = 2  # single-line - invalid-format-string
    REPAIR_SCENARIO_3 = 3  # single-line - memory-error
    REPAIR_SCENARIO_4 = 4  # multi-line - invalid-condition
    REPAIR_SCENARIO_5 = 5  # multi-line - invalid-format-string
    REPAIR_SCENARIO_6 = 6  # multi-line - memory-error


# RS_1: single-line - invalid-condition: , num: 26
repair_scenarios_1_repos = ['berry-5', 'coreutils-1', 'coreutils-2', 'cpp_peglib-4', 'cppcheck-4', 'cppcheck-8',
                            'cppcheck-9', 'cppcheck-10', 'cppcheck-11', 'cppcheck-24', 'cppcheck-25', 'exiv2-13',
                            'exiv2-15', 'libchewing-8', 'libtiff-1', 'libtiff-2', 'libtiff_sanitizer-2', 'md4c-6',
                            'md4c-8', 'md4c-9', 'openssl-14', 'openssl-24', 'yaml_cpp-5', 'yara-1', 'yara-2', 'zsh-3']
# RS_2: single-line - invalid-format-string: , num: 4
repair_scenarios_2_repos = ['cpp_peglib-8', 'dlt_daemon-1', 'exiv2-20', 'yaml_cpp-6']
# RS_3: single-line - memory-error: , num: 14
repair_scenarios_3_repos = ['coreutils-1', 'coreutils-2', 'cpp_peglib-1', 'cpp_peglib-3', 'dlt_daemon-1', 'exiv2-5',
                            'jerryscript-2', 'jerryscript-6', 'jerryscript-9', 'jerryscript-10', 'libtiff-1',
                            'libtiff-2', 'ndpi-1', 'yaml_cpp-1']
# RS_4: multi-line - invalid-condition: , num: 31
repair_scenarios_4_repos = ['berry-3', 'cppcheck-13', 'cppcheck-14', 'cppcheck-15', 'cppcheck-19', 'cppcheck-20',
                            'cppcheck-26', 'cppcheck-27', 'cppcheck-30', 'exiv2-1', 'exiv2-3', 'exiv2-11', 'exiv2-14',
                            'jerryscript-5', 'jerryscript-7', 'libchewing-4', 'libxml2-4', 'md4c-4', 'ndpi-3',
                            'openssl-2', 'openssl-15', 'openssl-18', 'openssl-22', 'proj-21', 'proj-28', 'wget2-1',
                            'wget2-2', 'wget2-3', 'wireshark-1', 'wireshark-4', 'yaml_cpp-7']
# RS_5: multi-line - invalid-format-string: , num: 7
repair_scenarios_5_repos = ['exiv2-9', 'openssl-27', 'proj-14', 'yaml_cpp-3', 'yaml_cpp-4', 'yaml_cpp-7', 'zsh-4']
# RS_6: multi-line - memory-error: , num: 17
repair_scenarios_6_repos = ['cpp_peglib-2', 'cpp_peglib-6', 'cppcheck-1', 'exiv2-2', 'exiv2-3', 'exiv2-4', 'exiv2-12',
                            'jerryscript-1', 'jerryscript-5', 'libtiff-5', 'libtiff_sanitizer-1', 'openssl-1',
                            'openssl-18', 'wireshark-6', 'xbps-2', 'yaml_cpp-10', 'zsh-2']


# search buggy repos
def search_repositories_by_rs(repair_scenario: RepairScenario) -> List[str]:
    if repair_scenario == RepairScenario.REPAIR_SCENARIO_1:
        return repair_scenarios_1_repos
    elif repair_scenario == RepairScenario.REPAIR_SCENARIO_2:
        return repair_scenarios_2_repos
    elif repair_scenario == RepairScenario.REPAIR_SCENARIO_3:
        return repair_scenarios_3_repos
    elif repair_scenario == RepairScenario.REPAIR_SCENARIO_4:
        return repair_scenarios_4_repos
    elif repair_scenario == RepairScenario.REPAIR_SCENARIO_5:
        return repair_scenarios_5_repos
    elif repair_scenario == RepairScenario.REPAIR_SCENARIO_6:
        return repair_scenarios_6_repos


def search_repositories_by_tags(bugs_line_tag: str, error_types_tag: str) -> List[str]:
    return fetch.search_repos(bugs_line_tag, error_types_tag)


# download repos data
def download_buggy_data_by_rs(repair_scenario: RepairScenario):
    repos = search_repositories_by_rs(repair_scenario)
    for repo in repos:
        fetch.download_data_by_repo(repo)


def download_buggy_data_by_repo(repository_name: str):
    fetch.download_data_by_repo(repository_name)


def download_buggy_data_by_tags(bugs_line_tag: str, error_types_tag: str):
    fetch.download_data_by_tags(bugs_line_tag, error_types_tag)


# get buggy code/function/files
def get_buggy_function_by_repo(repository_name: str) -> Dict[str, str]:
    return fetch.get_buggy_functions(repository_name)


def get_buggy_function_with_label_repo(repository_name: str) -> Dict[str, str]:
    return fetch.get_buggy_functions_with_label(repository_name)


def get_buggy_function_by_repo_rq3(repository_name: str) -> Dict[str, str]:
    buggy_function = {}
    buggy_data = fetch.get_rq3_buggy_data(repository_name)
    buggy_function[buggy_data['buggy_file']] = {'function': buggy_data['buggy_function'],
                                                'buggy_line_no': buggy_data['buggy_line_no']}
    return buggy_function


def get_buggy_function_with_label_repo_rq3(repository_name: str) -> Dict[str, str]:
    buggy_function = {}
    buggy_data = fetch.get_rq3_buggy_data(repository_name)
    buggy_function[buggy_data['buggy_file']] = {'function': buggy_data['buggy_function_with_label'],
                                                'buggy_line_no': buggy_data['buggy_line_with_label_no']}
    return buggy_function


def get_fixed_function_by_repo(repository_name: str) -> Dict[str, str]:
    return fetch.get_fixed_functions(repository_name)


def get_fixed_function_with_label_repo(repository_name: str) -> Dict[str, str]:
    return fetch.get_fixed_functions_with_label(repository_name)


def get_buggy_function_in_batch(repository_list: List[str]) -> Dict[str, str]:
    return fetch.get_buggy_functions_in_batch(repository_list)


def get_complete_buggy_codes_by_repo(repository_name: str) -> Dict[str, str]:
    return fetch.get_complete_buggy_codes_by_repo(repository_name)


def get_complete_fixed_codes_by_repo(repository_name: str) -> Dict[str, str]:
    return fetch.get_complete_fixed_codes_by_repo(repository_name)


def get_complete_buggy_codes_in_batch(repository_list: List[str]) -> Dict[str, str]:
    return fetch.get_complete_buggy_codes_in_batch(repository_list)


# fix buggy code and test
def test_buggy_codes(repository_name: str, fixed_code: str) -> test.TestResult:
    update.update_buggy_code(repository_name, fixed_code)
    build_res = test.build_repo(repository_name)
    test_res = test.TestCasesResult(-1.0, [], [], [])
    if build_res.build_res:
        test_res = test.test_repo(repository_name)
    update.restore_buggy_code(repository_name)
    return test.TestResult(repository_name, build_res.build_res, build_res.build_output, test_res)


def test_buggy_codes_rq3(repository_name: str, fixed_code: str) -> test.TestResult:
    update.update_buggy_code_for_rq3(repository_name, fixed_code)
    build_res = test.build_repo(repository_name)
    test_res = test.TestCasesResult(-1.0, [], [], [])
    if build_res.build_res:
        test_res = test.test_repo(repository_name)
    update.restore_buggy_code(repository_name)
    return test.TestResult(repository_name, build_res.build_res, build_res.build_output, test_res)


def test_default_buggy_codes(repository_name: str) -> test.TestResult:
    build_res = test.build_repo(repository_name)
    test_res = test.test_repo(repository_name)
    return test.TestResult(repository_name, build_res.build_res, build_res.build_output, test_res)


def test_default_fixed_codes(repository_name: str) -> test.TestResult:
    build_res = test.build_repo(repository_name, False)
    test_res = test.test_repo(repository_name, False)
    return test.TestResult(repository_name, build_res.build_res, build_res.build_output, test_res)


def test_buggy_codes_with_failed_tcs(repository_name: str, fixed_code: str) -> test.TestResult:
    test_cases = test.get_repo_failed_test_cases(repository_name)
    return test_buggy_codes_with_tcs(repository_name, fixed_code, test_cases)


def test_buggy_codes_with_failed_tcs_rq3(repository_name: str, fixed_code: str) -> test.TestResult:
    test_cases = test.get_repo_failed_test_cases(repository_name)
    return test_buggy_codes_with_tcs_rq3(repository_name, fixed_code, test_cases)


def test_default_buggy_codes_with_failed_tcs(repository_name: str) -> test.TestResult:
    test_cases = test.get_repo_failed_test_cases(repository_name)
    return test_default_buggy_codes_with_tcs(repository_name, test_cases)


def test_default_fixed_codes_with_failed_tcs(repository_name: str) -> test.TestResult:
    test_cases = test.get_repo_failed_test_cases(repository_name)
    return test_default_fixed_codes_with_tcs(repository_name, test_cases)


def test_buggy_codes_with_tcs(repository_name: str, fixed_code: str, test_cases: List[str]) -> test.TestResult:
    update.update_buggy_code(repository_name, fixed_code)
    build_res = test.build_repo(repository_name)
    test_res = test.TestCasesResult(-1.0, [], [], [])
    if build_res.build_res:
        test_res = test.test_repo_with_tcs(repository_name, test_cases)
    update.restore_buggy_code(repository_name)
    return test.TestResult(repository_name, build_res.build_res, build_res.build_output, test_res)


def test_buggy_codes_with_tcs_rq3(repository_name: str, fixed_code: str, test_cases: List[str]) -> test.TestResult:
    update.update_buggy_code_for_rq3(repository_name, fixed_code)
    build_res = test.build_repo(repository_name)
    test_res = test.TestCasesResult(-1.0, [], [], [])
    if build_res.build_res:
        test_res = test.test_repo_with_tcs(repository_name, test_cases)
    update.restore_buggy_code(repository_name)
    return test.TestResult(repository_name, build_res.build_res, build_res.build_output, test_res)


def test_default_buggy_codes_with_tcs(repository_name: str, test_cases: List[str]) -> test.TestResult:
    build_res = test.build_repo(repository_name)
    test_res = test.test_repo_with_tcs(repository_name, test_cases)
    return test.TestResult(repository_name, build_res.build_res, build_res.build_output, test_res)


def test_default_fixed_codes_with_tcs(repository_name: str, test_cases: List[str]) -> test.TestResult:
    build_res = test.build_repo(repository_name, False)
    test_res = test.test_repo_with_tcs(repository_name, test_cases)
    return test.TestResult(repository_name, build_res.build_res, build_res.build_output, test_res)