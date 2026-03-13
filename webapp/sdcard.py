"""
    $ pip install psutil
"""
import psutil

def get_partitions():
    partitions = [
            p for p in psutil.disk_partitions()
            if all(x not in p.device for x in ['loop', 'nvme'])
    ]
    partition_list = []
    for p in partitions:
        partition_list.append({'Partition': p.device, 'Mountpoint': p.mountpoint, 'Filesystem': p.fstype}) 
    return partition_list
