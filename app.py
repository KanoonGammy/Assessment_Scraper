import streamlit as st
import pandas as pd
from scraper import TreasuryScraper
import time

st.set_page_config(page_title="Treasury Assessment Scraper", layout="wide")

st.title("Treasury Department Assessment Price Scraper")
st.markdown("Scrape data from [assessprice.treasury.go.th](https://assessprice.treasury.go.th/)")

# Sidebar for controls
st.sidebar.header("Configuration")

# Province Selection
provinces = [
    "กระบี่", "กรุงเทพมหานคร", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา", 
    "ชลบุรี", "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่", "ตรัง", "ตราด", "ตาก", "นครนายก", 
    "นครปฐม", "นครพนม", "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน", 
    "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี", "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี", "พระนครศรีอยุธยา", 
    "พะเยา", "พังงา", "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์", "แพร่", "ภูเก็ต", 
    "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยโสธร", "ยะลา", "ร้อยเอ็ด", "ระนอง", "ระยอง", "ราชบุรี", 
    "ลพบุรี", "ลำปาง", "ลำพูน", "เลย", "ศรีสะเกษ", "สกลนคร", "สงขลา", "สตูล", "สมุทรปราการ", 
    "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว", "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี", 
    "สุราษฎร์ธานี", "สุรินทร์", "หนองคาย", "หนองบัวลำภู", "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", 
    "อุตรดิตถ์", "อุทัยธานี", "อุบลราชธานี"
]
# Default to Phuket (index of "ภูเก็ต")
default_index = provinces.index("ภูเก็ต") if "ภูเก็ต" in provinces else 0
province = st.sidebar.selectbox("Select Province (จังหวัด)", provinces, index=default_index)

headless_mode = st.sidebar.checkbox("Run in Headless Mode", value=True)

# Initialize Scraper
if 'scraper' not in st.session_state:
    st.session_state.scraper = TreasuryScraper()

# Update driver if mode changes (basic check)
if st.sidebar.button("Reset Browser"):
    st.session_state.scraper.close_driver()
    st.session_state.scraper.setup_driver(headless=headless_mode)
    st.success("Browser reset!")

# Fetch Property Types (Lazy load)
if 'property_types' not in st.session_state:
    with st.spinner("Fetching property types..."):
        try:
            # Ensure driver is set up with correct mode
            if not st.session_state.scraper.driver:
                st.session_state.scraper.setup_driver(headless=headless_mode)
            
            types = st.session_state.scraper.get_property_types()
            st.session_state.property_types = [t['text'] for t in types]
        except Exception as e:
            st.error(f"Failed to load property types: {e}")
            st.session_state.property_types = []

# Selection
all_types = st.session_state.property_types
selected_types = st.sidebar.multiselect(
    "Select Property Types to Scrape",
    options=all_types,
    default=all_types # Default to all
)

start_btn = st.sidebar.button("Start Scraping")

if start_btn:
    if not selected_types:
        st.warning("Please select at least one property type.")
    else:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create a placeholder for the dataframe
        data_placeholder = st.empty()
        
        total = len(selected_types)
        
        for i, p_type in enumerate(selected_types):
            status_text.text(f"Scraping: {p_type} ({i+1}/{total})")
            
            data = st.session_state.scraper.scrape_data(province, p_type)
            
            if "error" in data:
                st.error(f"Error scraping {p_type}: {data['error']}")
                if "screenshot" in data:
                    st.image(data["screenshot"], caption="Screenshot on Failure")
                if "logs" in data:
                    with st.expander("See Debug Logs"):
                        for log in data["logs"]:
                            st.text(log)
            else:
                # Process rows
                headers = data.get("headers", [])
                rows = data.get("rows", [])
                
                for row in rows:
                    # Create a dict for the row
                    row_dict = {"Property Type": p_type, "Province": province}
                    
                    # Clean headers: remove empty strings
                    clean_headers = [h for h in headers if h]
                    
                    for idx, cell in enumerate(row):
                        col_name = clean_headers[idx] if idx < len(clean_headers) else f"Col_{idx+1}"
                        row_dict[col_name] = cell
                    
                    results.append(row_dict)
            
            # Update progress
            progress_bar.progress((i + 1) / total)
            
            # Update display on the fly
            if results:
                df = pd.DataFrame(results)
                data_placeholder.dataframe(df)
            
            time.sleep(1) # Polite delay

        status_text.text("Scraping Completed!")
        
        if results:
            final_df = pd.DataFrame(results)
            st.success(f"Scraped {len(final_df)} rows.")
            
            # Download CSV
            csv = final_df.to_csv(index=False).encode('utf-8-sig')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "Download CSV",
                    csv,
                    "treasury_data.csv",
                    "text/csv",
                    key='download-csv'
                )
            
            # Download Excel
            with col2:
                # Buffer to write Excel data
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    final_df.to_excel(writer, index=False, sheet_name='Data')
                
                st.download_button(
                    label="Download Excel",
                    data=buffer.getvalue(),
                    file_name="treasury_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key='download-excel'
                )
        else:
            st.warning("No data found.")
