import psutil
import GPUtil
from typing import Dict, List, Optional, Union, Any
from database.db_interface import DBInterface
from database.models import PcStats, GpuStats
from operations.models import PcStatsCreateData, GpuStatsCreateData
gpu_interface = DBInterface(GpuStats)
pc_interface = DBInterface(PcStats)

def get_pc_stats() -> Optional[List[Dict[str, Union[float, int, None]]]]:
    """
    Gathers important PC and GPU statistics, validates both PC and GPU stats with Pydantic,
    and returns them as a single list of dictionaries suitable for direct database insertion.

    Returns:
        Optional[List[Dict[str, Union[float, int, None]]]]:
            A list where:
            - The first element is a dictionary containing PC statistics (validated by PcStatsCreateData).
            - Subsequent elements are dictionaries for each detected GPU (validated by GpustatsCreateData).
            Returns None if a critical error occurs during data collection.
    """
    pc_data_dict = {}
    gpu_data_list = []

    try:
        # --- Collect CPU Stats ---
        pc_data_dict['pc_usage'] = psutil.cpu_percent(interval=None) # Non-blocking call

        cpu_freq = psutil.cpu_freq()
        pc_data_dict['pc_freq'] = round(cpu_freq.current, 2) if cpu_freq else None

        # --- Collect Memory (RAM) Stats ---
        memory = psutil.virtual_memory()
        # Changed key from 'ram_usage' to 'ram_use' to match SQLAlchemy model
        pc_data_dict['ram_usage'] = round(memory.used / (1024**3), 2) # Used RAM in GB
        pc_data_dict['ram_available'] = round(memory.available / (1024**3), 2) # Available RAM in GB

        # --- Collect Network I/O Stats ---
        net_io = psutil.net_io_counters()
        # Changed key from 'internet_receive' to 'pc_internet_receive' to match SQLAlchemy model
        pc_data_dict['internet_receive'] = round(net_io.bytes_recv / (1024**2), 2) # Received MB
        # Changed key from 'internet_sent' to 'pc_internet_sent' to match SQLAlchemy model
        pc_data_dict['internet_sent'] = round(net_io.bytes_sent / (1024**2), 2) # Sent MB

        # Validate with PcStatsCreateData, but the original dict will be returned
        # This step ensures data conforms to the Pydantic model's schema and types
        _ = PcStatsCreateData(**pc_data_dict) # Validation only

        # --- Collect GPU Stats using GPUtil ---
        try:
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                gpu_dict = {
                    'gpu_id': gpu.id,
                    'ram_usage': round(gpu.memoryUsed, 2), # GPU memory used in MB
                    'ram_available': round(gpu.memoryFree, 2), # GPU memory free in MB
                    'temp': round(gpu.temperature, 2) # GPU temperature in Celsius
                }
                # Validate with GpustatsCreateData, but the original dict will be returned
                _ = GpuStatsCreateData(**gpu_dict) # Validation only
                gpu_data_list.append(gpu_dict)
        except Exception as gpu_e:
            print(f"Warning: Could not retrieve GPU stats (GPUtil might not be installed or compatible): {gpu_e}")
            # gpu_data_list will remain empty if an error occurs, which is handled gracefully.

        # Return a single list with pc_data_dict as the first element, followed by each gpu_dict
        return [pc_data_dict] + gpu_data_list

    except Exception as e:
        print(f"An error occurred while gathering PC stats: {e}")
        return None # Return None if a critical error prevents data collection

async def insert_stats_to_db(stats_list: List[Dict[str, Union[float, int, None]]]) -> None:
    """
    Inserts PC and GPU statistics from a list into the database.
    This function will now raise any exceptions encountered during database insertion.

    Args:
        stats_list (List[Dict[str, Union[float, int, None]]]):
            A list where:
            - The first element is a dictionary containing PC statistics.
            - Subsequent elements are dictionaries for each detected GPU.
    """
    if not stats_list:
        print("No stats to insert.")
        return

    pc_stats_inserted_count = 0
    gpu_stats_inserted_count = 0

    for item in stats_list:
        # Check if the dictionary contains a 'gpu_id' key to differentiate
        if 'gpu_id' in item:
            print(f"Inserting GPU stats for GPU ID: {item.get('gpu_id')}...")
            # Changed from GpustatsCreateData.create to GpuStatsDBInterface.create
            await gpu_interface.create(item)
            gpu_stats_inserted_count += 1
        else:
            # Assuming any dictionary without 'gpu_id' is PC stats
            # And that there should only be one PC stats entry
            if pc_stats_inserted_count == 0:
                print("Inserting PC stats...")
                # Changed from PcStatsCreateData.create to PcStatsDBInterface.create
                await pc_interface.create(item)
                pc_stats_inserted_count += 1
            else:
                print(f"Warning: Skipping additional PC stats entry: {item}")

    if pc_stats_inserted_count > 0:
        print(f"{pc_stats_inserted_count} PC stats entry inserted successfully.")
    if gpu_stats_inserted_count > 0:
        print(f"{gpu_stats_inserted_count} GPU stats entries inserted successfully.")
    if pc_stats_inserted_count == 0 and gpu_stats_inserted_count == 0:
        print("No valid stats found to insert.")
        
async def gather_stats_pipeline():
    try:
        stats = await get_pc_stats()
        await insert_stats_to_db(stats)
    except:
        return "something happened idk sorry"
    return




    