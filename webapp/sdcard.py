"""
    $ pip install psutil
"""
import psutil
import os

def get_partitions():
    partitions = [
            p for p in psutil.disk_partitions()
            if all(x not in p.device for x in ['loop', 'nvme'])
    ]
    partition_list = []
    for p in partitions:
        partition_list.append({'Partition': p.device, 'Mountpoint': p.mountpoint, 'Filesystem': p.fstype}) 
    return partition_list

def get_files(mountpoint):
    file_list = []
    for root, _, files in os.walk(mountpoint):
        file_list.extend([os.path.join(root, file) for file in files])
    return file_list

