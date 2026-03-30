import streamlit as st
import folium
from streamlit_folium import st_folium

import sdcard
import ap

def selection():
    st.title('SD Card Selection')
    mountpoints = [p['Mountpoint'] for p in sdcard.get_partitions()]
    with st.form('mountpoint_form'):
        mountpoint_selected = st.selectbox('Select Mountpoint:', mountpoints)
        mount_submit = st.form_submit_button('Load Files')
        if mount_submit:
            st.session_state.mountpoint = mountpoint_selected

    if 'mountpoint' in st.session_state:
        files = sdcard.get_files(st.session_state.mountpoint)
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
            #st.subheader('File Content')
            # st.text(content)

def extraction():
    if 'ap_str_list' in st.session_state:
        record_list = []
        for ap_str in st.session_state.ap_str_list:
            try:
                record = ap.WifiAPRecord(ap_str[0], ap_str[1], ap_str[2], ap_str[3], ap_str[4], ap_str[5], ap_str[6])
                record.ssid = ap_str[7]
                record.primary_channel = ap_str[8]
                record.second_channel = ap_str[9]
                record.rssi = ap_str[10]
                record.authmode = ap_str[11]
                record.pairwise_cipher = ap_str[12]
                record.group_cipher = ap_str[13]
                record._ant = ap_str[14]
                record.country_code = ap_str[15]
                record.country_start_channel = ap_str[16]
                record.country_end_channel = ap_str[17]
                record.max_tx_power = ap_str[18]
                record.country_policy = ap_str[19]
                record.wifi_AP_HE = ap_str[20]
                record.bss_color = ap_str[21]
                record.partial_bss_color = ap_str[22]
                record.bss_color_disabled = ap_str[23]
                record.bssid_index = ap_str[24]
                record.bandwidth = ap_str[25]
                record.vht_ch_freq1 = ap_str[26]
                record.vht_ch_freq2 = ap_str[27]
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