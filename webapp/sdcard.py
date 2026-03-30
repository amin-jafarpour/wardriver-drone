import psutil
import os
import streamlit as st
import ap

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

def selection():
    st.title('SD Card Selection')
    mountpoints = [p['Mountpoint'] for p in get_partitions()]
    with st.form('mountpoint_form'):
        mountpoint_selected = st.selectbox('Select Mountpoint:', mountpoints)
        mount_submit = st.form_submit_button('Load Files')
        if mount_submit:
            st.session_state.mountpoint = mountpoint_selected

    if 'mountpoint' in st.session_state:
        files = get_files(st.session_state.mountpoint)
        with st.form('file_form'):
            file_selected = st.selectbox('Select File', files)
            file_submit = st.form_submit_button('Upload File')
            if file_submit:
                st.session_state.file = file_selected
    
    if 'file' in st.session_state:
        with open(st.session_state.file, 'r') as file:
            content = file.read()
            ap_str_list = ap.WifiAPRecord.readCSV(content)
            st.session_state.ap_str_list = ap_str_list

def extraction():
    if 'ap_str_list' in st.session_state:
        record_list = []
        for ap_str in st.session_state.ap_str_list:
            try:
                record = WifiAPRecord.parse_obj(ap_str)
                record_list.append(record)
            except:
                continue
        st.session_state.record_list = record_list


def recording():
    if 'record_list' in st.session_state:
        collection = ap.WifiAPRecordCollection(st.session_state.record_list)
        collection.filter_invalid_gps_coords()
        collection.filter_duplicates()
        filterd_records = collection.wifi_ap_records
        for record in filterd_records:
            print(record.to_dict())


def main():
    selection()
    extraction()
    recording()

if __name__ == '__main__':
    main()