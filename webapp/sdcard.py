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

def get_inodes(mountpoint):
    directory_list = []
    file_list = []
    for root, directories, files in os.walk(mountpoint):
        directory_list.append([os.path.join(root, directory) for directory in directories])
        file_list.append([os.path.join(root, file) for file in files])
    return (directory_list, file_list)

