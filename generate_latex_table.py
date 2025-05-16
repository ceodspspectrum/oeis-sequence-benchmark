import os

def escape_latex_special_chars(text):
    """
    Escape LaTeX special characters in a string.

    Args:
        text (str): The string to escape.

    Returns:
        str: The escaped string.
    """
    return text.replace('_', '\\_')

def calculate_average_score_and_cheating_percentage(score_dir, model_dir, timeout):
    """
    Calculate the average score and the percentage of cheating examples for a specific timeout.

    Args:
        score_dir (str): The directory containing the .score files.
        model_dir (str): The directory containing the .cheated files.
        timeout (float): The timeout value for the current set of scores.

    Returns:
        tuple: (average_score, cheating_percentage), or (None, cheating_percentage) if there are no valid scores.
    """
    scores = []
    cheating_count = 0
    total_count = 0

    for score_file in os.listdir(score_dir):
        if score_file.endswith(f'_timeout_{timeout}.score'):
            score_file_path = os.path.join(score_dir, score_file)
            try:
                with open(score_file_path, 'r') as sf:
                    score = float(sf.read().strip())
                    scores.append(score)
            except ValueError:
                print(f"Warning: Could not read score from {score_file_path}. Skipping...")
        
        seq_id = score_file.split('_')[0]  # Extract the sequence ID before the first underscore

        # Look for the .cheated file in the model directory
        cheated_file_path = os.path.join(model_dir, f"{seq_id}.cheated")
        if os.path.exists(cheated_file_path):
            with open(cheated_file_path, 'r') as cf:
                if cf.read().strip() == '1':
                    cheating_count += 1
        total_count += 1

    # Compute the average score
    average_score = sum(scores) / len(scores) if scores else None

    # Compute the cheating percentage
    cheating_percentage = (cheating_count / total_count * 100) if total_count > 0 else 0

    return average_score, cheating_percentage

def calculate_average_scores_and_cheating_for_models(score_dirs, model_dirs, timeouts):
    """
    Calculate and print the average score and cheating percentage for each model and timeout in LaTeX table format.

    Args:
        score_dirs (dict): Dictionary mapping benchmarks to directories containing .score files.
        model_dirs (dict): Dictionary mapping benchmarks to directories containing .cheated files.
        timeouts (list): List of timeouts to consider.
    """
    print("\\begin{table}[h!]")
    print("\\centering")
    print("\\begin{tabular}{|l|c|c c|c c|}")
    print("\\hline")
    print("Model & Timeout & \\multicolumn{2}{c|}{SequenceEasy} & \\multicolumn{2}{c|}{SequenceHard} \\\\")
    print(" & & Avg. Score & \\% Cheating & Avg. Score & \\% Cheating \\\\")
    print("\\hline")

    # Iterate over models and timeouts
    models = ["o1-preview", "o1-mini", "claude-sonnet-3.5", "gpt-4o", "gpt-4o-mini", "llama-405b", "gemini-1.5-pro", "llama-70b", "gemini-1.5-flash", "gpt-3.5-turbo-1106", "o1", "llama33-70b"]
    for model in models:
        print(f"\\multirow{{{escape_latex_special_chars(model)}}}")  # Multirow for each model

        for i, timeout in enumerate(timeouts):
            # Get directories for SequenceEasy and SequenceHard
            easy_score_dir = score_dirs["SequenceEasy"][model]
            easy_model_dir = model_dirs["SequenceEasy"][model]
            hard_score_dir = score_dirs["SequenceHard"][model]
            hard_model_dir = model_dirs["SequenceHard"][model]

            # Calculate values for SequenceEasy
            easy_avg_score, easy_cheating_pct = calculate_average_score_and_cheating_percentage(easy_score_dir, easy_model_dir, timeout)
            easy_avg_str = f"{easy_avg_score:.1f}" if easy_avg_score is not None else "N/A"
            easy_cheat_str = f"{easy_cheating_pct:.1f}\\%"

            # Calculate values for SequenceHard
            hard_avg_score, hard_cheating_pct = calculate_average_score_and_cheating_percentage(hard_score_dir, hard_model_dir, timeout)
            hard_avg_str = f"{hard_avg_score:.1f}" if hard_avg_score is not None else "N/A"
            hard_cheat_str = f"{hard_cheating_pct:.1f}\\%"

            # Print LaTeX row for this model and timeout
            if i == 0:
                print(f" & {timeout} & {easy_avg_str} & {easy_cheat_str} & {hard_avg_str} & {hard_cheat_str} \\\\")
            else:
                print(f"      & {timeout} & {easy_avg_str} & {easy_cheat_str} & {hard_avg_str} & {hard_cheat_str} \\\\")
        print("\\hline")

    print("\\end{tabular}")
    print("\\caption{Evaluation of Average Scores and Cheating Percentages by Timeout}")
    print("\\end{table}")

def main():
    """
    Main entry point of the script.
    Calculates and prints the average score and cheating percentage for each model and timeout,
    formatted as a LaTeX table with SequenceEasy and SequenceHard columns.
    """
    # Directories for SequenceEasy and SequenceHard
    score_dirs = {
        "SequenceEasy": {
            "gpt-4o": "SequenceEasyScores_gpt-4o",
            "gpt-4o-mini": "SequenceEasyScores_gpt-4o-mini",
            "o1-mini": "SequenceEasyScores_o1-mini",
            "o1-preview": "SequenceEasyScores_o1-preview",
            "o1": "SequenceEasyScores_o1",
            "claude-sonnet-3.5": "SequenceEasyScores_claude-3-5-sonnet-20241022",
            "llama-405b": "SequenceEasyScores_llama-405b",
            "llama-70b": "SequenceEasyScores_llama-70b",
            "llama33-70b": "SequenceEasyScores_llama33-70b",
            "gemini-1.5-flash": "SequenceEasyScores_gemini-1.5-flash",
            "gemini-1.5-pro": "SequenceEasyScores_gemini-1.5-pro",
            "gpt-3.5-turbo-1106": "SequenceEasyScores_gpt-3.5-turbo-1106",
        },
        "SequenceHard": {
            "gpt-4o": "SequenceHardScores_gpt-4o",
            "gpt-4o-mini": "SequenceHardScores_gpt-4o-mini",
            "o1-mini": "SequenceHardScores_o1-mini",
            "o1-preview": "SequenceHardScores_o1-preview",
            "o1": "SequenceHardScores_o1",
            "claude-sonnet-3.5": "SequenceHardScores_claude-3-5-sonnet-20241022",
            "llama-405b": "SequenceHardScores_llama-405b",
            "llama-70b": "SequenceHardScores_llama-70b",
            "llama33-70b": "SequenceHardScores_llama33-70b",
            "gemini-1.5-flash": "SequenceHardScores_gemini-1.5-flash",
            "gemini-1.5-pro": "SequenceHardScores_gemini-1.5-pro",
            "gpt-3.5-turbo-1106": "SequenceHardScores_gpt-3.5-turbo-1106",
        }
    }

    model_dirs = {
        "SequenceEasy": {
            "gpt-4o": "SequenceEasyCodes_gpt-4o",
            "gpt-4o-mini": "SequenceEasyCodes_gpt-4o-mini",
            "o1-mini": "SequenceEasyCodes_o1-mini",
            "o1-preview": "SequenceEasyCodes_o1-preview",
            "o1": "SequenceEasyCodes_o1",
            "claude-sonnet-3.5": "SequenceEasyCodes_claude-3-5-sonnet-20241022",
            "llama-405b": "SequenceEasyCodes_llama-405b",
            "llama-70b": "SequenceEasyCodes_llama-70b",
            "llama33-70b": "SequenceEasyCodes_llama33-70b",
            "gemini-1.5-flash": "SequenceEasyCodes_gemini-1.5-flash",
            "gemini-1.5-pro": "SequenceEasyCodes_gemini-1.5-pro",
            "gpt-3.5-turbo-1106": "SequenceEasyCodes_gpt-3.5-turbo-1106",
        },
        "SequenceHard": {
            "gpt-4o": "SequenceHardCodes_gpt-4o",
            "gpt-4o-mini": "SequenceHardCodes_gpt-4o-mini",
            "o1-mini": "SequenceHardCodes_o1-mini",
            "o1-preview": "SequenceHardCodes_o1-preview",
            "o1": "SequenceHardCodes_o1",
            "claude-sonnet-3.5": "SequenceHardCodes_claude-3-5-sonnet-20241022",
            "llama-405b": "SequenceHardCodes_llama-405b",
            "llama-70b": "SequenceHardCodes_llama-70b",
            "llama33-70b": "SequenceHardCodes_llama33-70b",
            "gemini-1.5-flash": "SequenceHardCodes_gemini-1.5-flash",
            "gemini-1.5-pro": "SequenceHardCodes_gemini-1.5-pro",
            "gpt-3.5-turbo-1106": "SequenceHardCodes_gpt-3.5-turbo-1106",
        }
    }

    # Timeouts to consider
    #timeouts = [0.5, 1, 2, 4]
    timeouts = [0.5, 4]

    calculate_average_scores_and_cheating_for_models(score_dirs, model_dirs, timeouts)

if __name__ == "__main__":
    main()

