"""
COMPREHENSIVE DIAGNOSTIC TOOL
Tests every step of Google Drive connection in detail
"""

import streamlit as st
import io
import sys
import traceback

st.title("🔬 Comprehensive Diagnostic Tool")
st.markdown("---")

# ============================================
# TEST 1: Check Streamlit Environment
# ============================================
st.markdown("## 1️⃣ Streamlit Environment")

try:
    st.success(f"✅ Streamlit version: {st.__version__}")
    st.info(f"🐍 Python version: {sys.version}")
    st.success("✅ Streamlit running OK")
except Exception as e:
    st.error(f"❌ Streamlit error: {e}")

st.markdown("---")

# ============================================
# TEST 2: Check Secrets Availability
# ============================================
st.markdown("## 2️⃣ Secrets Availability")

try:
    if not hasattr(st, 'secrets'):
        st.error("❌ st.secrets not available")
        st.stop()
    
    if 'gcp_service_account' not in st.secrets:
        st.error("❌ gcp_service_account not found in secrets")
        st.write("Available secrets:", list(st.secrets.keys()) if st.secrets else "None")
        st.stop()
    
    st.success("✅ gcp_service_account found in secrets")
    
    # Show what keys are present
    secret_keys = list(st.secrets['gcp_service_account'].keys())
    st.write("Keys present:", secret_keys)
    
    # Validate required keys
    required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
    missing_keys = [k for k in required_keys if k not in secret_keys]
    
    if missing_keys:
        st.error(f"❌ Missing required keys: {missing_keys}")
        st.stop()
    else:
        st.success(f"✅ All required keys present ({len(secret_keys)} total)")
    
    # Show client_email (safe to display)
    client_email = st.secrets['gcp_service_account'].get('client_email', 'N/A')
    st.info(f"📧 Service Account Email: `{client_email}`")
    
    # Check private_key format
    private_key = st.secrets['gcp_service_account'].get('private_key', '')
    st.write(f"🔑 Private key length: {len(private_key)} characters")
    
    if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
        st.error("❌ Private key doesn't start with '-----BEGIN PRIVATE KEY-----'")
        st.write("First 50 chars:", private_key[:50])
    else:
        st.success("✅ Private key starts correctly")
    
    if not private_key.strip().endswith('-----END PRIVATE KEY-----'):
        st.error("❌ Private key doesn't end with '-----END PRIVATE KEY-----'")
        st.write("Last 50 chars:", private_key[-50:])
    else:
        st.success("✅ Private key ends correctly")
    
    # Check for \n in private_key
    if '\\n' in private_key:
        st.success("✅ Private key contains \\n characters (correct)")
    else:
        st.warning("⚠️ Private key might be missing \\n characters")
    
except Exception as e:
    st.error(f"❌ Error checking secrets: {e}")
    st.code(traceback.format_exc())
    st.stop()

st.markdown("---")

# ============================================
# TEST 3: Import Google Libraries
# ============================================
st.markdown("## 3️⃣ Import Google Libraries")

try:
    from google.oauth2 import service_account
    st.success("✅ Imported google.oauth2.service_account")
    
    from googleapiclient.discovery import build
    st.success("✅ Imported googleapiclient.discovery.build")
    
    from googleapiclient.http import MediaIoBaseDownload
    st.success("✅ Imported googleapiclient.http.MediaIoBaseDownload")
    
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.info("Try: pip install google-api-python-client google-auth")
    st.stop()
except Exception as e:
    st.error(f"❌ Unexpected error: {e}")
    st.code(traceback.format_exc())
    st.stop()

st.markdown("---")

# ============================================
# TEST 4: Create Credentials
# ============================================
st.markdown("## 4️⃣ Create Service Account Credentials")

try:
    with st.spinner("Creating credentials..."):
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
    
    st.success("✅ Credentials created successfully")
    st.write(f"Service account email: {credentials.service_account_email}")
    st.write(f"Project ID: {credentials.project_id}")
    
except ValueError as e:
    st.error(f"❌ ValueError creating credentials: {e}")
    st.error("This usually means the private_key format is wrong")
    st.code(traceback.format_exc())
    st.stop()
except Exception as e:
    st.error(f"❌ Error creating credentials: {e}")
    st.code(traceback.format_exc())
    st.stop()

st.markdown("---")

# ============================================
# TEST 5: Build Drive Service
# ============================================
st.markdown("## 5️⃣ Build Google Drive Service")

try:
    with st.spinner("Building Drive service..."):
        service = build('drive', 'v3', credentials=credentials)
    
    st.success("✅ Google Drive service built successfully")
    
except Exception as e:
    st.error(f"❌ Error building service: {e}")
    st.code(traceback.format_exc())
    st.stop()

st.markdown("---")

# ============================================
# TEST 6: Test File Access (Get Metadata)
# ============================================
st.markdown("## 6️⃣ Test File Access - Get Metadata")

TEST_FILE_ID = "1aNNTscWUOew7vnpZV18Y0UhfifejrKEQ"  # market_analysis.parquet
FILE_NAME = "market_analysis.parquet"

st.info(f"Testing file: **{FILE_NAME}**")
st.caption(f"File ID: `{TEST_FILE_ID}`")

try:
    with st.spinner("Getting file metadata..."):
        file_metadata = service.files().get(
            fileId=TEST_FILE_ID, 
            fields='id,name,size,mimeType,createdTime,modifiedTime'
        ).execute()
    
    st.success("✅ File metadata retrieved successfully!")
    
    # Display metadata
    col1, col2 = st.columns(2)
    with col1:
        st.metric("File Name", file_metadata.get('name', 'N/A'))
        st.metric("File ID", file_metadata.get('id', 'N/A'))
        st.metric("MIME Type", file_metadata.get('mimeType', 'N/A'))
    
    with col2:
        size_bytes = int(file_metadata.get('size', 0))
        size_mb = size_bytes / (1024 * 1024)
        st.metric("File Size", f"{size_mb:.2f} MB")
        st.metric("Created", file_metadata.get('createdTime', 'N/A')[:10])
        st.metric("Modified", file_metadata.get('modifiedTime', 'N/A')[:10])
    
    st.json(file_metadata)
    
except Exception as e:
    error_str = str(e)
    st.error(f"❌ Error getting file metadata: {e}")
    
    if "404" in error_str or "not found" in error_str.lower():
        st.warning("""
        **404 Not Found Error**
        - File ID might be wrong
        - File might have been deleted
        - Check the file exists at: https://drive.google.com/file/d/{}/view
        """.format(TEST_FILE_ID))
    
    elif "403" in error_str or "permission" in error_str.lower():
        st.warning(f"""
        **403 Permission Denied Error**
        - File not shared with Service Account
        - Make sure you shared the file with: `{client_email}`
        - Permission should be "Viewer" or "Editor"
        """)
    
    elif "401" in error_str or "unauthorized" in error_str.lower():
        st.warning("""
        **401 Unauthorized Error**
        - Service Account credentials are invalid
        - Check your Streamlit Secrets
        - Verify private_key is correct
        """)
    
    st.code(traceback.format_exc())
    st.stop()

st.markdown("---")

# ============================================
# TEST 7: Download File Content
# ============================================
st.markdown("## 7️⃣ Download File Content")

if st.button("🚀 Test Download File"):
    try:
        with st.spinner(f"Downloading {FILE_NAME}..."):
            request = service.files().get_media(fileId=TEST_FILE_ID)
            
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"Downloaded: {progress}%")
            
            file_buffer.seek(0)
            file_size = len(file_buffer.getvalue())
            
            st.success(f"✅ File downloaded successfully!")
            st.metric("Downloaded Size", f"{file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
            
            # Try to read as parquet
            st.markdown("### 8️⃣ Read as Parquet")
            try:
                import pandas as pd
                df = pd.read_parquet(file_buffer)
                
                st.success(f"✅ Parquet file read successfully!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", f"{len(df):,}")
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    st.metric("Memory", f"{df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")
                
                st.markdown("**Column Names:**")
                st.write(list(df.columns))
                
                st.markdown("**Sample Data (first 5 rows):**")
                st.dataframe(df.head())
                
                st.markdown("**Data Types:**")
                st.write(df.dtypes)
                
            except Exception as e:
                st.error(f"❌ Error reading parquet: {e}")
                st.code(traceback.format_exc())
        
    except Exception as e:
        st.error(f"❌ Error downloading file: {e}")
        st.code(traceback.format_exc())

st.markdown("---")

# ============================================
# TEST 8: Test All 4 Files
# ============================================
st.markdown("## 9️⃣ Test All 4 Files")

FILES_TO_TEST = [
    ("market_analysis.parquet", "1aNNTscWUOew7vnpZV18Y0UhfifejrKEQ"),
    ("industry_analysis.parquet", "18M4_ekSvR4skUl6V9ufDyjXssu-NBLdB"),
    ("ticker_analysis.parquet", "1__PIPDg1IoHvauhBgN-SNyVAiNZKRbtD"),
    ("Map_Complete.xlsx", "1Xl9yKLsNnizAZsEaRWwuCTitxe99JDo5"),
]

if st.button("🔍 Test All 4 Files Metadata"):
    for file_name, file_id in FILES_TO_TEST:
        try:
            with st.spinner(f"Checking {file_name}..."):
                metadata = service.files().get(fileId=file_id, fields='name,size').execute()
                size_mb = int(metadata.get('size', 0)) / (1024 * 1024)
                st.success(f"✅ {file_name}: {size_mb:.2f} MB")
        except Exception as e:
            st.error(f"❌ {file_name}: {str(e)[:100]}")

st.markdown("---")

# ============================================
# Summary
# ============================================
st.markdown("## 📊 Diagnostic Summary")

st.info("""
**If all tests above passed:**
- ✅ Streamlit Secrets configured correctly
- ✅ Service Account credentials valid
- ✅ Google Drive API accessible
- ✅ Files shared correctly
- ✅ Files can be downloaded and read

**Your app should work!** The issue might be:
- Cache (try clearing Streamlit cache)
- Timeout (files too large)
- Different app.py version

**If any test failed:**
- Check the error message above
- Follow the suggested fixes
- Re-run this diagnostic tool
""")

st.markdown("---")
st.caption("Diagnostic Tool v2.0 | Comprehensive Testing")
