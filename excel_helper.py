"""
Helper để tạo Excel Processor tự động detect local vs cloud
"""

import os
import streamlit as st
from components.excel_processor import ExcelProcessorAdvanced


def get_excel_processor(
    local_file_path: str = None,
    gdrive_file_id: str = None,
    file_name: str = "excel_file"
) -> ExcelProcessorAdvanced:
    """
    Tạo ExcelProcessorAdvanced tự động detect môi trường
    - Local: dùng file path
    - Cloud: dùng Google Drive
    
    Args:
        local_file_path: Đường dẫn file local (VD: "D:/data/Map.xlsx")
        gdrive_file_id: Google Drive File ID (dùng khi deploy)
        file_name: Tên file (để hiển thị thông báo)
    
    Returns:
        ExcelProcessorAdvanced instance
    
    Example:
        # Trong app.py
        processor = get_excel_processor(
            local_file_path="D:/aifinance_project/data/raw/Map_Complete.xlsx",
            gdrive_file_id="your_google_drive_file_id",
            file_name="Map_Complete.xlsx"
        )
        
        # Tự động:
        # - Ở local → dùng local_file_path
        # - Trên cloud → dùng gdrive_file_id
    """
    
    # Detect môi trường: kiểm tra xem có secrets không
    is_cloud = hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets
    
    if is_cloud:
        # Môi trường Cloud → dùng Google Drive
        if not gdrive_file_id:
            raise ValueError("gdrive_file_id là bắt buộc khi chạy trên cloud")
        
        from utils.data_loader import download_file_from_drive
        
        st.info(f"🌐 Chạy trên Cloud - Đang tải {file_name} từ Google Drive...")
        file_buffer = download_file_from_drive(gdrive_file_id, file_name)
        
        if file_buffer is None:
            st.error(f"❌ Không thể tải {file_name} từ Google Drive")
            st.stop()
        
        return ExcelProcessorAdvanced(file_buffer)
    
    else:
        # Môi trường Local → dùng file path
        if not local_file_path:
            raise ValueError("local_file_path là bắt buộc khi chạy local")
        
        if not os.path.exists(local_file_path):
            st.error(f"❌ File không tồn tại: {local_file_path}")
            st.stop()
        
        st.info(f"💻 Chạy Local - Đang tải {file_name} từ {local_file_path}")
        return ExcelProcessorAdvanced(local_file_path)


# Ví dụ sử dụng
if __name__ == "__main__":
    # Test
    processor = get_excel_processor(
        local_file_path="D:/aifinance_project/data/raw/Map_Complete.xlsx",
        gdrive_file_id="your_file_id_here",
        file_name="Map_Complete.xlsx"
    )
    
    result = processor.to_nested_dict(
        ['company', 'bank'],
        key_hierarchy=['CAL_GROUP', 'COL'],
        value_columns='ALGO'
    )
    print(result)