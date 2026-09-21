import streamlit as st
import convertapi
import os
import base64
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx

# 1. ⚠️ YOU MUST REPLACE THIS STRING WITH YOUR REAL CONVERTAPI TOKEN ⚠️
# Get your free token by signing up at https://www.convertapi.com
CONVERTAPI_SECRET = "YOUR_CONVERTAPI_SECRET_HERE"
convertapi.api_credentials = CONVERTAPI_SECRET

st.set_page_config(page_title="Universal File Converter", page_icon="🔄")

st.title("🔄 Universal File Converter")
st.write("Convert between 250+ formats with instant automatic download!")

# File uploader mechanism
uploaded_file = st.file_uploader("Choose a file to convert", type=None)

if uploaded_file is not None:
    file_name = uploaded_file.name
    # Extract file extension safely
    file_extension = os.path.splitext(file_name)[1].replace(".", "").lower()
    
    st.info(f"Detected format: **{file_extension.upper()}**")
    
    # Enter target extension manually
    target_format = st.text_input("Enter target format extension (e.g., pdf, docx, png, mp3):").strip().lower()
    
    if st.button("Convert File"):
        if not target_format:
            st.error("Please specify a target format.")
        elif target_format == file_extension:
            st.warning("Source and target formats are identical.")
        elif CONVERTAPI_SECRET == "YOUR_CONVERTAPI_SECRET_HERE":
            st.error("Missing API Key! Please register at convertapi.com and replace the placeholder token in the code.")
        else:
            with st.spinner(f"Converting {file_extension} to {target_format}..."):
                try:
                    # Create temporary folder
                    temp_dir = "temp_files"
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_input_path = os.path.join(temp_dir, file_name)
                    
                    # Save uploaded file structure 
                    with open(temp_input_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Execute conversion via ConvertAPI
                    result = convertapi.convert(
                        target_format, 
                        {'File': temp_input_path}, 
                        from_format=file_extension
                    )
                    
                    # FIXED: Correct path naming by properly indexing the splitext tuple
                    only_base_name = os.path.splitext(file_name)[0]
                    output_filename = f"{only_base_name}.{target_format}"
                    temp_output_path = os.path.join(temp_dir, output_filename)
                    
                    # Save converted file to local storage 
                    result.save_files(temp_output_path)
                    
                    # Read converted file back into memory
                    with open(temp_output_path, "rb") as file_ready:
                        file_bytes = file_ready.read()
                    
                    st.success("🎉 Conversion successful! Your download should start automatically.")
                    
                    # --- AUTO DOWNLOAD LOGIC ---
                    b64 = base64.b64encode(file_bytes).decode()
                    
                    js_download = f"""
                        <script>
                            var a = document.createElement('a');
                            a.href = 'data:application/octet-stream;base64,{b64}';
                            a.download = '{output_filename}';
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        </script>
                    """
                    
                    def render_download():
                        st.components.v1.html(js_download, height=0, width=0)
                    
                    ctx_thread = threading.Thread(target=render_download)
                    add_script_run_ctx(ctx_thread)
                    ctx_thread.start()
                    ctx_thread.join()
                    # ----------------------------------
                    
                    # Fallback download button
                    st.download_button(
                        label="⬇️ Click here if download didn't start automatically",
                        data=file_bytes,
                        file_name=output_filename,
                        mime="application/octet-stream"
                    )
                    
                    # Cleanup temporary files
                    if os.path.exists(temp_input_path):
                        os.remove(temp_input_path)
                    if os.path.exists(temp_output_path):
                        os.remove(temp_output_path)
                    
                except Exception as e:
                    st.error(f"An error occurred during conversion: {e}")
                    st.info("Check if your ConvertAPI free plan balances are exhausted or if the format transition is supported.")
