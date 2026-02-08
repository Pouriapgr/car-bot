# server_core/testers/run_stt_cuda.py

import os
import sys
import subprocess
import site

def find_nvidia_paths():
    possible_paths = []
    
    # 1. Check Conda Library Path (Standard for Conda installs)
    if 'CONDA_PREFIX' in os.environ:
        conda_lib = os.path.join(os.environ['CONDA_PREFIX'], 'lib')
        if os.path.exists(conda_lib):
            possible_paths.append(conda_lib)

    # 2. Check Python Site-Packages (Standard for Pip installs)
    site_packages = site.getsitepackages() + [site.getusersitepackages()]
    
    for sp in site_packages:
        nvidia_dir = os.path.join(sp, 'nvidia')
        if os.path.exists(nvidia_dir):
            for root, dirs, files in os.walk(nvidia_dir):
                if 'libcublas.so.12' in files or 'libcudnn.so.8' in files or 'libcudnn.so.9' in files:
                    if root not in possible_paths:
                        possible_paths.append(root)

    return possible_paths

def main():
    cuda_paths = find_nvidia_paths()
    
    if not cuda_paths:
        print("Could not find NVIDIA libraries automatically.")
        return

    print(f"Found library paths: {cuda_paths}")


    env = os.environ.copy()
    current_ld = env.get('LD_LIBRARY_PATH', '')
    new_ld = ":".join(cuda_paths) + ":" + current_ld
    env['LD_LIBRARY_PATH'] = new_ld

    cmd = [sys.executable, "-m", "server_core.testers.speech2text_tester"]
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error launching tester: {e}")

if __name__ == "__main__":
    main()
