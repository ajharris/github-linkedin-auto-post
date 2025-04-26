import os

def sync_env_example():
    env_file = '.env'
    env_example_file = '.env.example'

    if not os.path.exists(env_file):
        print(f"{env_file} not found.")
        return

    if not os.path.exists(env_example_file):
        print(f"{env_example_file} not found. Creating a new one.")
        open(env_example_file, 'w').close()

    with open(env_file, 'r') as env, open(env_example_file, 'r') as env_example:
        env_vars = {line.split('=')[0] for line in env if '=' in line}
        example_vars = {line.split('=')[0] for line in env_example if '=' in line}

    missing_vars = env_vars - example_vars

    if missing_vars:
        print(f"Adding missing variables to {env_example_file}: {', '.join(missing_vars)}")
        with open(env_example_file, 'a') as env_example:
            for var in missing_vars:
                env_example.write(f"{var}=\n")

    extra_vars = example_vars - env_vars
    if extra_vars:
        print(f"Warning: {env_example_file} contains extra keys not present in {env_file}: {', '.join(extra_vars)}")

if __name__ == "__main__":
    sync_env_example()