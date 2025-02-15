import pickle
import tempfile
import subprocess
import os

def run_subprocess(input_data):
    # Serialize input data to bytes
    input_bytes = pickle.dumps(input_data)

    # Create a temporary file to store input data
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as temp_file:
        temp_file.write(input_bytes)  # Write serialized data
        temp_file_path = temp_file.name  # Get file path

    try:
        # Run subprocess with the temp file as an argument
        result = subprocess.run(
            ["python3", "-c",
             "import pickle, sys; data = pickle.load(open(sys.argv[1], 'rb')); print('Received:', data)",
             temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            input=None,  # No need to use stdin
            timeout=5,
            text=True,
            check=True,
        )

        # Decode output
        stdout_output = result.stdout.strip()
        stderr_output = result.stderr.strip()

    except subprocess.CalledProcessError as e:
        stdout_output = e.stdout.decode() if e.stdout else ""
        stderr_output = e.stderr.decode() if e.stderr else "Error occurred"

    finally:
        # Cleanup: Delete temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return stdout_output, stderr_output


# Example usage
input_data = {"name": "Alice", "age": 25}
stdout, stderr = run_subprocess(input_data)

print("STDOUT:", stdout)
print("STDERR:", stderr)
