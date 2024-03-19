import os
import time
from datetime import datetime
import json
from openai import OpenAI
import exp_utils_dev
import dataset_api

base_path = '/workspaces/ecs260_hb/src/scripts/dataset/gpt_results'

def run_gpt(user_message, model="gpt-3.5-turbo-0125"):
    client = OpenAI()
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

# only for 1 prompt 
def run_exps_from_buggyrepolist(buggy_repo_list : list, prompt_ind : int, repeat_time : int, single_multi_str = 'single-line') -> list:

    if prompt_ind <=0 or prompt_ind > 4: raise RuntimeError("The index of prompt can only be 1, 2, 3, 4 now.") 
    if repeat_time <=0 or repeat_time > 4: raise RuntimeError("Repeat time should be positive and no larger than 3 to save time.")

    print('*' * 80)
    print(f'Input Buggy Repo List is: {buggy_repo_list}')
    print('-' * 35 + 'Test Begins:' + '-' * 35)
    print('\n')

    total_patch_num = 0
    compilable_patch_num = 0
    plausible_patch_num = 0
    total_llm_response_time = 0

    # list to record specific patch-prompt-repeat
    compilable_patch_list = []
    plausible_patch_list = []
    # list to record repo-avg-stat
    repo_stat_list = []

    buggy_repo_num = len(buggy_repo_list)
    total_exp_num = 0 # can calculate the average llm response time

    for i in range(buggy_repo_num):
        buggy_repo_name = buggy_repo_list[i]
        prompt_dir_name = "prompt_" + str(int(prompt_ind))

        Inrepo_total_patch_num = 0
        Inrepo_compilable_patch_num = 0
        Inrepo_plausible_patch_num = 0
        # can calculate average
        Inrepo_total_llm_response_time = 0
        Inrepo_total_confidence_score = 0
        Inrepo_total_identify_accuracy = 0
        Inrepo_total_pass_rate = 0

        print('^' * 65)
        print(f'Repo: {buggy_repo_name} Test Starts. Using Prompt_id: {prompt_ind}. Input Repeat Number: {repeat_time}. ')
        print('^' * 65)

        # while loop to begin our multiple queries to LLM
        repeat_counter = 0
        retry_counter = 0
        skip_flag = False
        while repeat_counter <= repeat_time - 1:
            retry_flag = False
            repeat_time_dir_name = "repeat_" + str(int(repeat_counter + 1))
            output_dir = os.path.join(base_path, buggy_repo_name, prompt_dir_name, repeat_time_dir_name)

            # get buggy function and error_line_number_list from the repo name
            buggy_func_str, true_errlin_num_list, buggy_func_labeled_str = exp_utils_dev.buggyFuncStrGetter(buggy_repo_name)

            # construct input prompt to LLM using prompt_ind and buggy_func_str(or buggy_func_labeled_str)
            if prompt_ind == 1: input_prompt_str = exp_utils_dev.constructPrompt(buggy_func_str, prompt_ind, buggy_repo_name)
            elif prompt_ind == 2: input_prompt_str = exp_utils_dev.constructPrompt(buggy_func_str, prompt_ind, buggy_repo_name)
            elif prompt_ind == 3: input_prompt_str = exp_utils_dev.constructPrompt(buggy_func_labeled_str, prompt_ind, buggy_repo_name)
            elif prompt_ind == 4: input_prompt_str = exp_utils_dev.constructPrompt(buggy_func_labeled_str, prompt_ind, buggy_repo_name)
            else: raise RuntimeError(f"Input Prompt_ID: {prompt_ind} To be implemented!")

            # Query LLM using input_prompt_str
            start_t = time.time()
            LLM_respond_str = run_gpt(input_prompt_str)
            end_t = time.time()

            # the first step after receiving LLM's response is to check if it can be correctly parsed
            # The part of the function where you get the parsed LLM response
            try:
                parsed_llm_obj = exp_utils_dev.extractLLMOutputFromStr(LLM_respond_str)
                if parsed_llm_obj is None:
                    raise ValueError("Failed to parse LLM response into a structured object.")
            except (IndexError, json.decoder.JSONDecodeError, ValueError) as Error:
                print(f"ERROR: {Error}")
                print(f"Retry Query: Repeat {repeat_counter+1}.")
                retry_flag = True
                if retry_counter > 3: 
                    print(f"Warning: In Repo {buggy_repo_name}: LLM always fails to give structured output. Skip it!")
                    skip_flag = True
                retry_counter += 1
                continue
        

            if skip_flag: break 
            if retry_flag: continue

            # Now we parsed LLM's output with no problem
            elapsed_time = end_t - start_t
            print('-' * 65) 
            print(f'Repo: {buggy_repo_name} -- Prompt_id: {prompt_ind}. Current Repeat: {repeat_counter+1}. Parse Response Succefully! Time: {elapsed_time} seconds.')
            exp_utils_dev.saveLLMReply(output_dir, LLM_respond_str)

            # Test LLM's repaired function using Musheng's API
            if 'repaired_function' in parsed_llm_obj:
                repaired_function_str = parsed_llm_obj['repaired_function']
                test_result_obj = dataset_api.test_buggy_codes(buggy_repo_name, repaired_function_str)
                exp_utils_dev.saveTestResultTXT(output_dir, test_result_obj)
            else:
                print("Repaired function not found in parsed LLM response.")
                # Handle the case where the repaired function is missing
                continue  # Skip this iteration or implement alternative handling

            exp_utils_dev.saveTestResultTXT(output_dir, test_result_obj)

            # Evaulate LLM's reply using test_result_obj and save file
            eval_llm_obj = exp_utils_dev.evalLLMRespondGetter(prompt_ind, true_errlin_num_list, elapsed_time, parsed_llm_obj, test_result_obj)
            print(f'Repo: {buggy_repo_name} -- Prompt_id: {prompt_ind}. Current Repeat: {repeat_counter+1}. Eval Response Done! Confidence: {eval_llm_obj.confidence}, Build Result: {eval_llm_obj.build_result}, Identify Accuracy: {eval_llm_obj.identify_accuracy}, Pass Rate: {eval_llm_obj.pass_rate}.')
            exp_utils_dev.saveEvalLLMObjTXT(output_dir, eval_llm_obj)
            print('-' * 65)
            # Now we should update experiment metrics here:
            temp_patch_name = buggy_repo_name + "_Prompt-" + str(prompt_ind) + "_Repeat-" + str(repeat_counter+1)
            Inrepo_total_patch_num += 1
            if eval_llm_obj.build_result: 
                Inrepo_compilable_patch_num += 1
                compilable_patch_list.append(temp_patch_name)
            if eval_llm_obj.pass_rate > 0.999: 
                Inrepo_plausible_patch_num += 1
                plausible_patch_list.append(temp_patch_name)

            Inrepo_total_llm_response_time += elapsed_time
            Inrepo_total_confidence_score += eval_llm_obj.confidence
            Inrepo_total_identify_accuracy += eval_llm_obj.identify_accuracy
            # when compilation fails, pass rate = 0
            if eval_llm_obj.pass_rate < 0: Inrepo_total_pass_rate += 0
            else:     Inrepo_total_pass_rate += eval_llm_obj.pass_rate

            # update repeat counter!
            repeat_counter += 1

        total_exp_num += repeat_counter
        Inrepo_average_llm_response_time = 0 
        Inrepo_average_confidence_score = 0
        Inrepo_average_identify_accuracy = 0
        Inrepo_average_pass_rate = 0
        if repeat_counter > 0:
            Inrepo_average_llm_response_time = Inrepo_total_llm_response_time / repeat_counter 
            Inrepo_average_confidence_score = Inrepo_total_confidence_score / repeat_counter
            Inrepo_average_identify_accuracy = Inrepo_total_identify_accuracy / repeat_counter
            Inrepo_average_pass_rate = Inrepo_total_pass_rate / repeat_counter   
        print('^' * 65)   
        print(f'Repo: {buggy_repo_name} Test Ends. -- Prompt_id: {prompt_ind}. Actual Repeat Number: {repeat_counter}. Inrepo Total Patch Number: {Inrepo_total_patch_num}, Inrepo Compilable Patch Number: {Inrepo_compilable_patch_num}, Inrepo Plausible Patch Number: {Inrepo_plausible_patch_num}. ')
        print(f'Repo: {buggy_repo_name} Test Statistic -- Average LLM Response Time: {Inrepo_average_llm_response_time}, Average LLM Confidence: {Inrepo_average_confidence_score}, Average Identify Accuracy: {Inrepo_average_identify_accuracy}, Average Pass Rate: {Inrepo_average_pass_rate}. ')

        # record repo-specific test statistics to a list
        temp_avgstat_list = []
        temp_avgstat_list.append(buggy_repo_name)
        temp_avgstat_list.append(prompt_ind)
        temp_avgstat_list.append(repeat_counter)
        temp_avgstat_list.append(Inrepo_total_patch_num)
        temp_avgstat_list.append(Inrepo_compilable_patch_num)
        temp_avgstat_list.append(Inrepo_plausible_patch_num)
        temp_avgstat_list.append(Inrepo_average_llm_response_time)
        temp_avgstat_list.append(Inrepo_average_confidence_score)
        temp_avgstat_list.append(Inrepo_average_identify_accuracy)
        temp_avgstat_list.append(Inrepo_average_pass_rate)
        repo_stat_list.append(temp_avgstat_list)

        # write repo-specific test statistics to a txt file
        avg_stat_filename = buggy_repo_name + '_Prompt-' + str(prompt_ind) + '_' + 'avgstat.txt'
        avg_stat_dir = os.path.join(base_path, buggy_repo_name, prompt_dir_name)
        avg_stat_f = open(os.path.join(avg_stat_dir, avg_stat_filename), 'w')
        avg_stat_f.write(f'Test_Repo: {buggy_repo_name}\n')
        avg_stat_f.write(f'Prompt_ID: {prompt_ind}\n')
        avg_stat_f.write(f'Repeat_Num: {repeat_counter}\n')
        avg_stat_f.write(f'Total_Patch_Num: {Inrepo_total_patch_num}\n')
        avg_stat_f.write(f'Compilable_Patch_Num: {Inrepo_compilable_patch_num}\n')
        avg_stat_f.write(f'Plausible_Patch_Num: {Inrepo_plausible_patch_num}\n')
        avg_stat_f.write(f'Average_Response_Time: {Inrepo_average_llm_response_time}\n')
        avg_stat_f.write(f'Average_Confidence: {Inrepo_average_confidence_score}\n')
        avg_stat_f.write(f'Average_Identify_Accuracy: {Inrepo_average_identify_accuracy}\n')
        avg_stat_f.write(f'Average_Pass_Rate: {Inrepo_average_pass_rate}\n')
        avg_stat_f.close()
        print(f"  Success: write {avg_stat_filename} into {avg_stat_dir} .")
        print('^' * 65)
        print('\n')

        # contribute to global statistics
        total_patch_num += Inrepo_total_patch_num
        compilable_patch_num += Inrepo_compilable_patch_num
        plausible_patch_num += Inrepo_plausible_patch_num
        total_llm_response_time += Inrepo_total_llm_response_time

    average_llm_response_time = total_llm_response_time / total_exp_num

    print(f'All Test Ends. Total Patch Number: {total_patch_num}, Total Compilable Patch Number: {compilable_patch_num}, Total Plausible Patch Number: {plausible_patch_num}, Average LLM Response Time: {average_llm_response_time}. ')
    print('-' * 35 + 'Test   Ends:' + '-' * 35)
    # Write total stat file to a txt file with time stamp
    now = datetime.now()
    timestamp_str = now.strftime("%m%d%Y_%H%M%S")
    total_stat_filename = 'totalstat_Prompt-' + str(prompt_ind) + '_' + timestamp_str + '.txt'
    total_stat_f = open(os.path.join(base_path, total_stat_filename), "w")
    total_stat_f.write(f'Test_Buggy_Repo_List: {buggy_repo_list}\n')
    total_stat_f.write(f'Total_Patch_Number: {total_patch_num}\n')
    total_stat_f.write(f'Total_Compilable_Patch_Number: {compilable_patch_num}\n')
    total_stat_f.write(f'Total_Plausible_Patch_Number: {plausible_patch_num}\n')
    total_stat_f.write(f'Compilable_Patch_List: {compilable_patch_list}\n')
    total_stat_f.write(f'Plausible_Patch_list: {plausible_patch_list}\n')
    total_stat_f.close()
    print(f"  Success: write {total_stat_filename} into {base_path} .")

    return repo_stat_list

def main():
    test_list = ['libtiff-5']  # Specify the repository you're focusing on
    prompt_id = 4  # Use the second prompt for the experiment
    repeat_time = 3  # Number of times you want to repeat the experiment

    # Run the experiment with the specified parameters
    rp1_prompt1_stat_list = run_exps_from_buggyrepolist(test_list, prompt_id, repeat_time)

    # Save the statistical summary of the experiment results
    exp_utils_dev.saveRepoAvgStatCSV(base_path, rp1_prompt1_stat_list, prompt_id)

if __name__ == "__main__":
    main()