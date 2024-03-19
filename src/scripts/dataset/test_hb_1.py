import os
import time
from datetime import datetime
from openai import OpenAI
import exp_utils_dev
import dataset_api

base_path = '/workspaces/ecs260_hb/src/scripts/dataset/gpt_results'

def run_gpt(user_message, model="gpt-3.5-turbo"):
    client = OpenAI()
    messages = [
        {"role": "system", "content": "You are an assistant skilled in debugging and explaining code."},
        {"role": "user", "content": f"{user_message}"}
    ]
    chat_response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        top_p=1,
    )
    return chat_response.choices[0].message['content']

def run_conversational_repair(buggy_repo_name, prompt_ind, max_conversation_counter=5):
    # This function is a placeholder for the initialization of the conversational repair process
    initial_prompt = exp_utils_dev.get_initial_prompt(buggy_repo_name, prompt_ind)  # Assume this function gets the initial prompt based on repo and prompt index
    pPatch_list = []

    conversation_counter = 0
    while conversation_counter < max_conversation_counter:
        # Adjust input_prompt based on the conversational repair algorithm's logic
        input_prompt = initial_prompt if not pPatch_list else f"{initial_prompt}. Previous patches: {'; '.join(pPatch_list)}"

        llm_patch = run_gpt(input_prompt)
        conversation_counter += 1

        # Mock functions to check compilation and testing, replace these with your actual logic
        compilation_success = exp_utils_dev.check_compilation(llm_patch)
        if not compilation_success:
            initial_prompt += " The patch contains a compilation error."
            continue

        original_test_success = exp_utils_dev.check_original_test_case(llm_patch)
        if not original_test_success:
            initial_prompt += " The patch fails the original test case."
            continue

        all_tests_success = exp_utils_dev.check_all_tests(llm_patch)
        if all_tests_success:
            pPatch_list.append(llm_patch)
            initial_prompt += " Please generate an alternative fix function."
        else:
            # If it fails on a different test, ignore due to time constraint
            initial_prompt = exp_utils_dev.get_initial_prompt(buggy_repo_name, prompt_ind)

        print(f"Conversation {conversation_counter}: {llm_patch}")

    return pPatch_list

def main():
    buggy_repo_name = 'example-repo-1'  # Example repository name
    prompt_ind = 1  # Example prompt index
    repeat_time = 3  # Example repeat time

    plausible_patches = run_conversational_repair(buggy_repo_name, prompt_ind, repeat_time)
    print("Plausible patches found:", plausible_patches)

if __name__ == "__main__":
    main()