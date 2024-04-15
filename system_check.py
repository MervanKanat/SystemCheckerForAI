

import wmi
import subprocess
from rich.console import Console
from rich.table import Table

def get_system_info():
    system_info = {"cpu": "", "gpu": []}
    try:
        c = wmi.WMI()
        for processor in c.Win32_Processor():
            system_info["cpu"] = processor.Name.strip()
        for gpu in c.Win32_VideoController():
            system_info["gpu"].append(gpu.Name.strip())
    except Exception as e:
        print(f"Error: {e}")
    return system_info

def has_avx_support():
    try:
        result = subprocess.check_output("wmic cpu get Caption, DeviceID, Name, NumberOfCores, MaxClockSpeed, SecondLevelAddressTranslationExtensions, VirtualizationFirmwareEnabled, VMMonitorModeExtensions, SocketDesignation", shell=True)
        if "AVX" in str(result):
            return True, "AVX support found."
        else:
            return False, "This CPU does not have AVX support. Some versions of TensorFlow may not work on this CPU."
    except subprocess.CalledProcessError as e:
        return False, f"Error checking AVX support: {e}"

def has_cuda_compatible_gpu(system_info):
    for gpu in system_info["gpu"]:
        if "nvidia" in gpu.lower():
            return True, f"CUDA compatible NVIDIA GPU found: {gpu}. GPU acceleration available."
    return False, "No CUDA compatible NVIDIA GPU found in system. GPU acceleration unavailable."

def check_ai_library_compatibility(system_info):
    compatible = {"TensorFlow": {"CPU": [False, ""], "GPU": [False, ""]}, "PyTorch": {"CPU": [False, ""], "GPU": [False, ""]}}
    
    avx_support, avx_message = has_avx_support()
    cuda_gpu, cuda_message = has_cuda_compatible_gpu(system_info)
    
    compatible["TensorFlow"]["CPU"] = [avx_support, avx_message]
    compatible["PyTorch"]["CPU"] = [True, "PyTorch can run on CPU without AVX support."]
    
    if cuda_gpu:
        compatible["TensorFlow"]["GPU"] = [True, cuda_message]
        compatible["PyTorch"]["GPU"] = [True, cuda_message]
    else:
        compatible["TensorFlow"]["GPU"] = [False, "No suitable NVIDIA GPU found for TensorFlow GPU acceleration."]
        compatible["PyTorch"]["GPU"] = [False, "No suitable NVIDIA GPU found for PyTorch GPU acceleration."]

    return compatible

def main():
    console = Console()
    system_info = get_system_info()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("System Feature", style="dim", width=20)
    table.add_column("Value", style="bold")
    
    table.add_row("CPU", system_info["cpu"])
    table.add_row("GPU", ', '.join(system_info["gpu"]) if system_info["gpu"] else "Not Found")
    
    compatible = check_ai_library_compatibility(system_info)
    for lib, compat_info in compatible.items():
        for platform, (is_compatible, message) in compat_info.items():
            table.add_row(f"{lib} ({platform})", message)

    console.print(table)

if __name__ == "__main__":
    main()
