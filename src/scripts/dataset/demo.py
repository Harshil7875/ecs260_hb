
corrected_code = '''static void free_suffix(bfuncinfo *finfo, bexpdesc *e)
{
    int idx = e->v.ss.idx;
    int nlocal = be_list_count(finfo->local);
    /* release suffix register */
    if (!isK(idx) && idx >= nlocal) {
        be_code_freeregs(finfo, 1);
    }
    /* release object register */
    if (e->v.ss.tt == ETREG && (int)e->v.ss.obj >= nlocal && (e->v.ss.obj + 1 >= finfo->freereg)) {
        be_code_freeregs(finfo, 1);
    }
}'''


def main():
    buggy_repo = 'berry-5'

    print(dataset_api.search_repositories_by_tags(dataset_api.bugs_line_tags[0], dataset_api.error_types_tags[0]))

    # download repo data
    dataset_api.download_buggy_data_by_repo(buggy_repo)

    # get buggy code
    buggy_functions = dataset_api.get_buggy_function_by_repo(buggy_repo)
    print(f'{buggy_repo} buggy_function: {buggy_functions}')

    complete_codes = dataset_api.get_complete_buggy_codes_by_repo(buggy_repo)
    print(f'{buggy_repo} buggy_codes: {complete_codes}')

    # test
    # output initial test result
    print('-' * 20 + 'Initial' + '-' * 20)
    result = dataset_api.test_default_buggy_codes(buggy_repo)
    print('test_result:')
    print(f'{result.repo_name}: ')
    print(f'  build_result: {result.build_result}')
    print(f'  test_cases_result: ')
    print(f'    pass_rate: {result.test_cases_result.pass_rate}')
    print(f'    pass_test_cases: {result.test_cases_result.pass_test_cases}')
    print(f'    fail_test_cases: {result.test_cases_result.fail_test_cases}')

    print('-' * 20 + 'Fixed' + '-' * 20)
    fixed_code = ' '
    # fixed_code = corrected_code
    result = dataset_api.test_buggy_codes(buggy_repo, fixed_code)
    print('test_result:')
    print(f'{result.repo_name}: ')
    print(f'  build_result: {result.build_result}')
    print(f'  test_cases_result: ')
    print(f'    pass_rate: {result.test_cases_result.pass_rate}')
    print(f'    pass_test_cases: {result.test_cases_result.pass_test_cases}')
    print(f'    fail_test_cases: {result.test_cases_result.fail_test_cases}')


if __name__ == "__main__":
    import dataset_api

    main()