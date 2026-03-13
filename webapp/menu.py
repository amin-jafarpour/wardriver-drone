import streamlit as st
import sdcard

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
            st.subheader('File Content')
            st.text(content)

def main():
    selection()

if __name__ == '__main__':
    main()