import os
import shutil
import uuid

import docker
from celery_app import app


@app.task(
    bind=True, autoretry_for=(docker.errors.APIError,), retry_kwargs={"max_retries": 3}
)
def execute_code_task(self, language, code, input_data=""):
    client = docker.from_env()
    unique_id = uuid.uuid4()
    temp_dir = f"temp_code/{unique_id}"
    os.makedirs(temp_dir, exist_ok=True)
    max_code_length = 10000

    if len(code) > max_code_length:
        shutil.rmtree(temp_dir)
        return {
            "error": f"Code length exceeds maximum allowed ({max_code_length} characters)."
        }

    if language == "python":
        dockerfile = "Dockerfile.python"
        filename = "user_code.py"
        command = f"cat input.txt | python {filename}"
    elif language == "javascript":
        dockerfile = "Dockerfile.javascript"
        filename = "user_code.js"
        command = f"cat input.txt | node {filename}"
    else:
        shutil.rmtree(temp_dir)
        return {"error": "Unsupported language"}

    code_path = os.path.join(temp_dir, filename)
    with open(code_path, "w") as f:
        f.write(code)

    input_path = os.path.join(temp_dir, "input.txt")
    with open(input_path, "w") as f:
        f.write(input_data)

    try:
        image, logs = client.images.build(
            path=".", dockerfile=dockerfile, tag=f"code_executor_{unique_id}"
        )

        container = client.containers.run(
            f"code_executor_{unique_id}",
            command=command,
            working_dir="/app",
            mem_limit=f"128m",
            cpu_quota=100000,
            network_disabled=True,
            pids_limit=64,
            read_only=True,
            volumes={os.path.abspath(temp_dir): {"bind": "/app", "mode": "rw"}},
            stderr=True,
            stdout=True,
            detach=True,
        )
        container.wait(timeout=10)
        output = container.logs().decode("utf-8")
        if container.status != "exited":
            container.kill()
            output = "Timeout"
        container.remove()
        client.images.remove(f"code_executor_{unique_id}")
        shutil.rmtree(temp_dir)
        return {"output": output.strip(), "error": ""}
    except docker.errors.ContainerError as e:
        error_message = str(e.stderr, "utf-8")
        container.remove()
        client.images.remove(f"code_executor_{unique_id}")
        shutil.rmtree(temp_dir)
        return {"output": "", "error": error_message}
    except docker.errors.BuildError as e:
        error_message = str(e.stderr, "utf-8")
        shutil.rmtree(temp_dir)
        return {"output": "", "error": error_message}
    except Exception as e:
        shutil.rmtree(temp_dir)
        return {"output": "", "error": str(e)}
