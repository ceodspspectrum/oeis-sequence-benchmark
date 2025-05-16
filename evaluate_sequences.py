import os
import subprocess
import json

def load_sequences(filename):
    """
    Load integer sequences from the given file.

    Args:
        filename (str): Path to the 'stripped' file.

    Returns:
        dict: A dictionary mapping sequence IDs to their integer sequences.
    """
    sequences = {}
    try:
        with open(filename, 'r') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # Skip comments and empty lines
                parts = line.split(',')
                if len(parts) < 2:
                    print(f"Warning: Line {line_number} in {filename} is malformed.")
                    continue
                seq_id = parts[0].strip()
                sequence = [x.strip() for x in parts[1:] if x.strip()]
                sequences[seq_id] = sequence
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading '{filename}': {e}")
        sys.exit(1)
    return sequences

def load_offset(seq_id):
    """
    Load the offset for the given sequence ID from the OEIS cache.

    Args:
        seq_id (str): The sequence ID (e.g., 'A000001').

    Returns:
        int: The offset of the sequence.
    """
    cache_file = os.path.join("oeis_cache", f"{seq_id}.json")
    if not os.path.exists(cache_file):
        print(f"Warning: No cache file found for sequence {seq_id}. Defaulting offset to 0.")
        return 0

    try:
        with open(cache_file, 'r') as cf:
            data = json.load(cf)
            if isinstance(data, list) and "offset" in data[0]:
                offset_str = data[0]["offset"]
                offset = int(offset_str.split(',')[0])
                return offset
            else:
                print(f"Warning: No valid offset found for sequence {seq_id}. Defaulting offset to 0.")
                return 0
    except Exception as e:
        print(f"Error loading offset for {seq_id}: {e}")
        return 0

def run_python_file(python_file, input_value, timeout):
    """
    Run a Python script with the given input and capture its output.

    Args:
        python_file (str): Path to the Python script.
        input_value (int): The input value to provide via stdin.
        timeout (int): Maximum time in seconds to wait for the script to execute.

    Returns:
        str or None: The output from the script as a string, or None if an error occurred.
    """
    try:
        process = subprocess.Popen(
            ['python3', python_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            stdout, stderr = process.communicate(input=str(input_value), timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            #print(f"Error: Execution of '{python_file}' with input {input_value} timed out after {timeout} seconds.")
            return None

        if stderr:
            #print(f"Error in '{python_file}' with input {input_value}: {stderr.strip()}")
            return None

        output = stdout.strip()
        return output
    except FileNotFoundError:
        print(f"Error: The file '{python_file}' does not exist.")
        return None
    except Exception as e:
        print(f"Failed to run '{python_file}' with input {input_value}: {e}")
        return None

def evaluate_model(sequence, python_file, input_offset, timeout, debug=False):
    """
    Evaluate a single model's Python script against the provided sequence.

    Args:
        sequence (list of str): The expected sequence values as strings.
        python_file (str): Path to the Python script to evaluate.
        input_offset (int): The starting index offset for inputs.
        timeout (int): Time limit for each script execution in seconds.
        debug (bool): Whether to print detailed mismatch information.

    Returns:
        int: The number of correct outputs.
        int: The total number of evaluations attempted.
    """
    correct = 0
    total = 0
    for index, expected in enumerate(sequence):
        input_value = index + input_offset  # Adjust for offset
        output = run_python_file(python_file, input_value, timeout=timeout)
        if output is None:
            total += 1
            continue
        if output == expected:
            correct += 1
        else:
            if debug:
                print(f"Mismatch in '{python_file}': Input {input_value} | Expected '{expected}' | Got '{output}'")
        total += 1
    return correct, total

def evaluate_all_sequences(sequence_file, model_dirs, score_dirs, debug=False):
    """
    Evaluate all sequences against models in the specified directories, recording the results.

    Args:
        sequence_file (str): Path to the 'stripped' file containing sequences.
        model_dirs (list of str): List of directories containing model Python scripts.
        score_dirs (list of str): List of directories where scores will be saved.
        debug (bool): Whether to print detailed mismatch information.
    """
    sequences = load_sequences(sequence_file)
    timeouts = [0.5, 1, 2, 4]  # Different timeouts for evaluation

    for model_dir, score_dir in zip(model_dirs, score_dirs):
        # Create the score directory if it doesn't exist
        os.makedirs(score_dir, exist_ok=True)

        python_files = [f for f in os.listdir(model_dir) if f.endswith('.py')]

        for python_file in python_files:
            seq_id = python_file.replace('.py', '')
            if seq_id not in sequences:
                print(f"  {model_dir}: Sequence '{seq_id}' not found in the sequence file. Skipping...")
                continue

            sequence = sequences[seq_id]
            cheated_file = os.path.join(model_dir, f"{seq_id}.cheated")
            
            for timeout in timeouts:
                score_file = os.path.join(score_dir, f"{seq_id}_timeout_{timeout}.score")

                if os.path.exists(score_file):
                    print(f"  {model_dir}: Score for '{seq_id}' with timeout {timeout} already exists. Skipping...")
                    continue

                offset = load_offset(seq_id)
                cheated = False

                if os.path.isfile(cheated_file):
                    with open(cheated_file, 'r') as cf:
                        if cf.read().strip() == '1':
                            cheated = True

                if cheated:
                    print(f"  {model_dir}: Cheating detected in '{python_file}'. Setting score to 0 for timeout {timeout}.")
                    score = 0
                else:
                    print(f"  Evaluating '{python_file}' with timeout {timeout} seconds...")
                    correct, total = evaluate_model(sequence, os.path.join(model_dir, python_file), offset, timeout, debug)
                    score = (correct / total) * 100 if total > 0 else 0
                    print(f"    Correct: {correct}/{total}")
                    print(f"    Accuracy: {score:.2f}% for timeout {timeout} seconds")

                with open(score_file, 'w') as sf:
                    sf.write(f"{score}\n")

def main():
    """
    Main entry point of the script.
    Evaluates all models against sequences and saves results to score files.
    """
    sequence_file = "stripped"
    model_dirs = [
        "SequenceEasyCodes_gpt-4o-mini", 
        "SequenceEasyCodes_o1-mini", 
        "SequenceEasyCodes_o1-preview", 
        "SequenceHardCodes_gpt-4o", 
        "SequenceHardCodes_gpt-4o-mini", 
        "SequenceHardCodes_o1-mini",
        "SequenceHardCodes_o1-preview",
        "SequenceEasyCodes_gpt-4o",
        "SequenceEasyCodes_claude-3-5-sonnet-20241022", 
        "SequenceHardCodes_claude-3-5-sonnet-20241022", 
        "SequenceEasyCodes_llama-405b", 
        "SequenceHardCodes_llama-405b", 
        "SequenceEasyCodes_llama-70b", 
        "SequenceHardCodes_llama-70b", 
        "SequenceEasyCodes_gemini-1.5-flash", 
        "SequenceHardCodes_gemini-1.5-flash", 
        "SequenceEasyCodes_gemini-1.5-pro", 
        "SequenceHardCodes_gemini-1.5-pro", 
        "SequenceEasyCodes_gpt-3.5-turbo-1106", 
        "SequenceHardCodes_gpt-3.5-turbo-1106", 
        "SequenceEasyCodes_o1", 
        "SequenceHardCodes_o1", 
        "SequenceEasyCodes_llama33-70b", 
        "SequenceHardCodes_llama33-70b", 
        #"SequenceEasyCodes_", 
        #"SequenceHardCodes_", 
    ]
    score_dirs = [
        "SequenceEasyScores_gpt-4o-mini", 
        "SequenceEasyScores_o1-mini", 
        "SequenceEasyScores_o1-preview", 
        "SequenceHardScores_gpt-4o", 
        "SequenceHardScores_gpt-4o-mini", 
        "SequenceHardScores_o1-mini",
        "SequenceHardScores_o1-preview",
        "SequenceEasyScores_gpt-4o",
        "SequenceEasyScores_claude-3-5-sonnet-20241022", 
        "SequenceHardScores_claude-3-5-sonnet-20241022", 
        "SequenceEasyScores_llama-405b", 
        "SequenceHardScores_llama-405b", 
        "SequenceEasyScores_llama-70b", 
        "SequenceHardScores_llama-70b", 
        "SequenceEasyScores_gemini-1.5-flash", 
        "SequenceHardScores_gemini-1.5-flash", 
        "SequenceEasyScores_gemini-1.5-pro", 
        "SequenceHardScores_gemini-1.5-pro", 
        "SequenceEasyScores_gpt-3.5-turbo-1106", 
        "SequenceHardScores_gpt-3.5-turbo-1106", 
        "SequenceEasyScores_o1", 
        "SequenceHardScores_o1", 
        "SequenceEasyScores_llama33-70b", 
        "SequenceHardScores_llama33-70b", 
        #"SequenceEasyScores_", 
        #"SequenceHardScores_", 
    ]

    debug = False  # Change to True for debugging

    evaluate_all_sequences(sequence_file, model_dirs, score_dirs, debug)

if __name__ == "__main__":
    main()

