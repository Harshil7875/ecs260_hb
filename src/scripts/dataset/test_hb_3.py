import os
import time
from datetime import datetime
import json
from openai import OpenAI
import exp_utils_dev
import dataset_api
import exprq2_utils_dev

base_path = '/workspaces/ecs260_hb/src/scripts/dataset/gpt_results'

MAX_CONVERSATION_TRIES = 5
RQ3_REPO_LIST = ["berry-1", "berry-2", "berry-3", "berry-4", "berry-5", 
                 "libtiff-1", "libtiff-2", "libtiff-3", "libtiff-4", "libtiff-5",
                 "libucl-1", "libucl-2", "libucl-3", "libucl-4"]


def run_gpt(user_message, model="gpt-3.5-turbo-0125"):
    # client = OpenAI(api_key=""my_key")
    messages = [
        {"role": "user", "content": f"{user_message}"}
    ]
    chat_response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature = 0.7,
        top_p = 1
    )
    return (chat_response.choices[0].message.content)

def run_exps_RQ2_from_buggyrepolist(buggy_repo_list: list):

    print('*' * 80)
    print(f'Input Buggy Repo List is: {buggy_repo_list}')
    print('-' * 35 + 'Test Begins:' + '-' * 35)
    print('\n')

    total_patch_num = 0
    compilable_patch_num = 0
    plausible_patch_num = 0
    total_llm_response_time = 0

    buggy_repo_num = len(buggy_repo_list)
    total_conversation_num = 0 # can calculate the average llm response time

    compilable_patch_name_list = []
    plausible_patch_name_list = []
    # list to record repo-avg-stat
    repo_stat_list = []

    for i in range(buggy_repo_num):
        isRQ3_repo = False
        buggy_repo_name = buggy_repo_list[i]
        if buggy_repo_name in RQ3_REPO_LIST: 
            isRQ3_repo = True
            print(f'Repo Info: {buggy_repo_name} is a RQ3 Repo.')

        # Initialization metrics
        Inrepo_total_patch_num = 0
        Inrepo_compilable_patch_num = 0
        Inrepo_plausible_patch_num = 0
        # can calculate average
        Inrepo_total_llm_response_time = 0
        # Inrepo_total_pass_rate = 0

        # A Plausible Patch List
        Plausible_Patch_Str_List = []

        # Now we should Construct our Initial Prompt
        # Get buggy function string from the repo name
        buggy_func_str,_ ,_ = exp_utils_dev.buggyFuncStrGetter(buggy_repo_name, isRQ3_repo)
        # Do a initial Test on original buggy function to obtain the test failure information
        test_fail_info_str, test_fail_code_str = exprq2_utils_dev.getOriginalTestFailureInfo(buggy_repo_name)
        # construct our initial prompt
        initialPrompt = exprq2_utils_dev.constructRQ2InitialPrompt(buggy_func_str, test_fail_info_str, test_fail_code_str)

        print('^' * 65)
        print(f'Repo: {buggy_repo_name} Conversation Repair Starts! ----------------------------------------------------------------------------- ')
        print('^' * 65)

        # while loop to begin our multiple queries to LLM
        conversation_counter = 1
        retry_counter = 0
        skip_flag = False

        inputPrompt = exprq2_utils_dev.formatLLMResponse(initialPrompt)

        while conversation_counter <= MAX_CONVERSATION_TRIES:
            retry_flag = False
            conversation_try_dir_name = "Conversation_" + str(int(conversation_counter))
            output_dir = os.path.join(base_path, buggy_repo_name, conversation_try_dir_name)

            # Add a token number check here to see our inputPrompt's token number
            tokenNum = exprq2_utils_dev.num_tokens_from_string(inputPrompt)
            if(tokenNum > 4000): 
                print(f"Warning: In Repo {buggy_repo_name} -- Conversation {conversation_counter}: Token number exceeds 4k: {tokenNum}.")

            # We can save the InputPrompt For Reference (If Parsing fails, this file will be overwritten)
            exprq2_utils_dev.saveInputPromptTXT(output_dir, inputPrompt)

            # Initialize retry counter outside the loop if it's not already
            retry_counter = 0
            max_retries = 5
            
            while retry_counter <= max_retries:
                try:
                    start_t = time.time()
                    LLM_respond_str = run_gpt(inputPrompt)
                    end_t = time.time()
                    print(f"Query successful. Time taken: {end_t - start_t} seconds")
                    break  # Exit the loop if the function call is successful
                except Exception as error:  # Catch a general exception
                    print(f'ERROR: Exception occurred! Details: {error}')
                    retry_counter += 1
                    if retry_counter > max_retries:
                        print(f"Warning: In Repo {buggy_repo_name}: Retry limit reached. Skipping...")
                        break  # Exit the loop after reaching the maximum number of retries
                    else:
                        print(f"Retry {retry_counter} out of {max_retries}.")
                        time.sleep(1)  # Wait for a second before retrying
            
            if skip_flag: break
            if retry_flag: continue

            # the first step after receiving LLM's response is to check if it can be correctly parsed
            try:
                repairedFunc_byLLM = exp_utils_dev.extractFuncStrFromLLMResponse(LLM_respond_str)
            except (IndexError) as Error:
                print(f"ERROR: Failed to extract from LLM's response! Details: {Error}")
                print(f"Retry Query: Repeat {conversation_counter}.")
                retry_flag = True
                if retry_counter > 5: 
                    print(f"Warning: In Repo {buggy_repo_name}: Retry Number Meets Maximum. Skip it!")
                    skip_flag = True
                retry_counter += 1

            if skip_flag: break 
            if retry_flag: continue

            # Now we parsed LLM's output with no problem
            elapsed_time = end_t - start_t
            print('-' * 65) 
            print(f'Repo: {buggy_repo_name} -- Current Conversation: {conversation_counter}. Parse Response Succefully! Time: {elapsed_time} seconds.')
            exp_utils_dev.saveLLMReply(output_dir, LLM_respond_str)

            Inrepo_total_patch_num += 1
            Inrepo_total_llm_response_time += elapsed_time

            # Test LLM's repaired function using Musheng's API
            # first only test the original failure test case
            if not isRQ3_repo: test_oricase_result_obj = dataset_api.test_buggy_codes_with_failed_tcs(buggy_repo_name, repairedFunc_byLLM)
            else: test_oricase_result_obj = dataset_api.test_buggy_codes_with_failed_tcs_rq3(buggy_repo_name, repairedFunc_byLLM)
            exp_utils_dev.saveTestResultTXTwithName(output_dir, test_oricase_result_obj, "test_original_failure.txt", isRQ2=True)

            temp_patch_name = buggy_repo_name + "_Conversation-" + str(int(conversation_counter))

            if not test_oricase_result_obj.build_result:
                print(f'Repo: {buggy_repo_name} -- Current Conversation Tries: {conversation_counter}. The Patch Generated By LLM Fails to Compile')

                # it means the patch generated by LLM contains a compilation error
                compile_failure_info = test_oricase_result_obj.build_output

                # Construct the new prompt based on the compilation error and LLM_repaired_func
                compileinfoPrompt = exprq2_utils_dev.constructRQ2CompileFailPrompt(initialPrompt, repairedFunc_byLLM, compile_failure_info)
                inputPrompt = exprq2_utils_dev.formatLLMResponse(compileinfoPrompt)
            else:
                # Enter into here means the patch generated By LLM can compile
                Inrepo_compilable_patch_num += 1
                compilable_patch_name_list.append(temp_patch_name)
                ori_test_passrate = test_oricase_result_obj.test_cases_result.pass_rate

                if ori_test_passrate == 0:
                    # The llm_patch fails to pass the original failure test case
                    print(f'Repo: {buggy_repo_name} -- Current Conversation Tries: {conversation_counter}. The Patch Generated By LLM Fails to Pass the Original Test Case!')

                    # Consturct the new prompt based on the original test case failure information
                    oritestfailPrompt = exprq2_utils_dev.constructRQ2OriTestFailPrompt(initialPrompt, repairedFunc_byLLM)
                    inputPrompt = exprq2_utils_dev.formatLLMResponse(oritestfailPrompt)

                elif ori_test_passrate == 1:
                    # The llm_patch pass the original failure test case
                    print(f'Repo: {buggy_repo_name} -- Current Conversation Tries: {conversation_counter}. The Patch Generated By LLM Pass the Original Test Case!')
                    print(f'Repo: {buggy_repo_name} -- Current Conversation Tries: {conversation_counter}. Begins Eval On The Whole Test Suite')

                    test_wholesuite_result_obj = dataset_api.test_buggy_codes(buggy_repo_name, repairedFunc_byLLM)
                    exp_utils_dev.saveTestResultTXT(output_dir, test_wholesuite_result_obj)

                    # Check the Pass Rate On the Whole Test Suites:
                    whole_test_passrate = test_wholesuite_result_obj.test_cases_result.pass_rate
                    if whole_test_passrate > 0.999:
                        # Now we Have a Plausible Patch
                        Inrepo_plausible_patch_num += 1
                        plausible_patch_name_list.append(temp_patch_name)

                        print(f'Repo: {buggy_repo_name} -- Current Conversation Tries: {conversation_counter}. The Patch Generated By LLM Pass All Test Cases!')
                        Plausible_Patch_Str_List.append(repairedFunc_byLLM)

                        # Construct the New Prompt based on the Plausible_Patch_Str_List
                        plausiblelistPrompt = exprq2_utils_dev.constructRQ2PlausiblePrompt(initialPrompt, Plausible_Patch_Str_List)
                        inputPrompt = exprq2_utils_dev.formatLLMResponse(plausiblelistPrompt)
                    else:
                        # Enter here means the patch generated by LLM passes the original test case but fails on another
                        # Now we don't consider this situation and roll back the input prompt to be initial
                        print(f'Warning: Repo: {buggy_repo_name} -- Current Conversation Tries: {conversation_counter}. The Patch Fails On {test_wholesuite_result_obj.test_cases_result.fail_test_cases}.')
                        print(f'Warning: Repo: {buggy_repo_name} -- Current Conversation Tries: {conversation_counter}. Roll Back to Initial Prompt!')

                        inputPrompt = exprq2_utils_dev.formatLLMResponse(initialPrompt)

                else:
                    print(f'Warning: Repo: {buggy_repo_name} -- Current Conversation Tries: {conversation_counter}. The Original Test Pass Rate is {ori_test_passrate}.')

            conversation_counter += 1

        total_conversation_num += conversation_counter - 1

        Inrepo_average_llm_response_time = -99
        if conversation_counter > 1:
            Inrepo_average_llm_response_time = Inrepo_total_llm_response_time / (conversation_counter-1)

        print('^' * 65)   
        print(f'Repo: {buggy_repo_name} Conversation Ends. Actual Repeat Number: {conversation_counter-1}. Inrepo Total Patch Number: {Inrepo_total_patch_num}, Inrepo Compilable Patch Number: {Inrepo_compilable_patch_num}, Inrepo Plausible Patch Number: {Inrepo_plausible_patch_num},  Average LLM Response Time: {Inrepo_average_llm_response_time}. ')

        # record repo-specific test statistics to a list
        temp_avgstat_list = []
        temp_avgstat_list.append(buggy_repo_name)
        temp_avgstat_list.append(conversation_counter-1)
        temp_avgstat_list.append(Inrepo_total_patch_num)
        temp_avgstat_list.append(Inrepo_compilable_patch_num)
        temp_avgstat_list.append(Inrepo_plausible_patch_num)
        temp_avgstat_list.append(Inrepo_average_llm_response_time)
        repo_stat_list.append(temp_avgstat_list)

        # write repo-specific test statistics to a txt file
        avg_stat_filename = buggy_repo_name + '_ConversationRepair_' + 'avgstat.txt'
        avg_stat_dir = os.path.join(base_path, buggy_repo_name)
        avg_stat_f = open(os.path.join(avg_stat_dir, avg_stat_filename), 'w')
        avg_stat_f.write(f'Test_Repo: {buggy_repo_name}\n')
        avg_stat_f.write(f'Conversation_Num: {conversation_counter-1}\n')
        avg_stat_f.write(f'Total_Patch_Num: {Inrepo_total_patch_num}\n')
        avg_stat_f.write(f'Compilable_Patch_Num: {Inrepo_compilable_patch_num}\n')
        avg_stat_f.write(f'Plausible_Patch_Num: {Inrepo_plausible_patch_num}\n')
        avg_stat_f.write(f'Average_Response_Time: {Inrepo_average_llm_response_time}\n')
        avg_stat_f.close()
        print(f"  Success: write {avg_stat_filename} into {avg_stat_dir} .")
        print('^' * 65)
        print('\n')

        # contribute to global statistics
        total_patch_num += Inrepo_total_patch_num
        compilable_patch_num += Inrepo_compilable_patch_num
        plausible_patch_num += Inrepo_plausible_patch_num
        total_llm_response_time += Inrepo_total_llm_response_time

    # for End Here
    average_llm_response_time = total_llm_response_time / total_conversation_num

    print(f'All Test Ends. Total Patch Number: {total_patch_num}, Total Compilable Patch Number: {compilable_patch_num}, Total Plausible Patch Number: {plausible_patch_num}, Average LLM Response Time: {average_llm_response_time}. ')
    print('-' * 35 + 'Test   Ends:' + '-' * 35)
    # Write total stat file to a txt file with time stamp
    now = datetime.now()
    timestamp_str = now.strftime("%m%d%Y_%H%M%S")
    total_stat_filename = 'totalstat_ConversationRepair_' + timestamp_str + '.txt'
    total_stat_f = open(os.path.join(base_path, total_stat_filename), "w")
    total_stat_f.write(f'Test_Buggy_Repo_List: {buggy_repo_list}\n')
    total_stat_f.write(f'Total_Patch_Number: {total_patch_num}\n')
    total_stat_f.write(f'Total_Compilable_Patch_Number: {compilable_patch_num}\n')
    total_stat_f.write(f'Total_Plausible_Patch_Number: {plausible_patch_num}\n')
    total_stat_f.write(f'Compilable_Patch_List: {compilable_patch_name_list}\n')
    total_stat_f.write(f'Plausible_Patch_list: {plausible_patch_name_list}\n')
    total_stat_f.close()
    print(f"  Success: write {total_stat_filename} into {base_path} .")

    return repo_stat_list


def main():
    # Total 28 Repos:

    repo_hb = ['yaml_cpp-6']

    rq2_list = ['cpp_peglib-4', 'cppcheck-8', 'cppcheck-9', 'cppcheck-11', 'cppcheck-25', 'exiv2-13', 'exiv2-15', 
                 'openssl-14', 'openssl-24', 'yara-1', 'yara-2', 'dlt_daemon-1', 'exiv2-20', 'yaml_cpp-6']

    rq3_list = ["berry-1", "berry-2", "berry-3", "berry-4", "berry-5",
                 "libtiff-1", "libtiff-2", "libtiff-3", "libtiff-4", "libtiff-5",
                 "libucl-1", "libucl-2", "libucl-3", "libucl-4"]

    rq2_stat_list = run_exps_RQ2_from_buggyrepolist(repo_hb)
    exprq2_utils_dev.saveRQ2RepoAvgStatCSV(base_path, rq2_stat_list)

    # rq3_stat_list = run_exps_RQ2_from_buggyrepolist(rq3_list)
    # exprq2_utils_dev.saveRQ2RepoAvgStatCSV(base_path, rq3_stat_list)

    print('-' * 55 + 'Main Ends:' + '-' * 55)

if __name__ == "__main__":
    main()