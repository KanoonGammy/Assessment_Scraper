import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Fallback list from user provided HTML
FALLBACK_PROPERTY_TYPES = [
    {"value": "101", "text": "บ้านพักอาศัยไม้ชั้นเดียว"},
    {"value": "102", "text": "บ้านพักอาศัยไม้ชั้นเดียวใต้ถุนสูง"},
    {"value": "103", "text": "บ้านพักอาศัยตึกชั้นเดียว"},
    {"value": "104", "text": "บ้านพักอาศัยไม้สองชั้น"},
    {"value": "105", "text": "บ้านพักอาศัยตึกสองชั้น"},
    {"value": "106", "text": "บ้านพักอาศัยครึ่งตึกครึ่งไม้สองชั้น"},
    {"value": "107", "text": "บ้านพักอาศัยตึกสามชั้น"},
    {"value": "108", "text": "บ้านพักอาศัยแฝดตึกสองชั้น"},
    {"value": "109", "text": "บ้านพักอาศัยแฝดตึกสามชั้น"},
    {"value": "110", "text": "บ้านทรงไทยไม้ชั้นเดียวใต้ถุนสูง"},
    {"value": "111", "text": "บ้านทรงไทยครึ่งตึกครึ่งไม้สองชั้น"},
    {"value": "112", "text": "บ้านพักอาศัยแฝดตึกชั้นเดียว"},
    {"value": "201", "text": "บ้านแถว (ทาวน์เฮาส์) ชั้นเดียว"},
    {"value": "202", "text": "บ้านแถว (ทาวน์เฮาส์) สองชั้น"},
    {"value": "203", "text": "บ้านแถว (ทาวน์เฮาส์) สามชั้น"},
    {"value": "204", "text": "บ้านแถว (ทาวน์เฮาส์) สี่ชั้น"},
    {"value": "301", "text": "ห้องแถวไม้ชั้นเดียว"},
    {"value": "302", "text": "ห้องแถวไม้สองชั้น"},
    {"value": "303", "text": "ห้องแถวครึ่งตึกครึ่งไม้สองชั้น"},
    {"value": "401", "text": "ตึกแถวชั้นเดียว"},
    {"value": "402", "text": "ตึกแถวสองชั้น"},
    {"value": "403", "text": "ตึกแถวสองชั้นครึ่ง"},
    {"value": "404", "text": "ตึกแถวสามชั้น"},
    {"value": "405", "text": "ตึกแถวสามชั้นครึ่ง"},
    {"value": "406", "text": "ตึกแถวสี่ชั้น"},
    {"value": "407", "text": "ตึกแถวสี่ชั้นครึ่ง"},
    {"value": "408", "text": "ตึกแถวห้าชั้น"},
    {"value": "409", "text": "ตึกแถวหกชั้น"},
    {"value": "501", "text": "คลังสินค้า พื้นที่ไม่เกิน 300 ตารางเมตร"},
    {"value": "502", "text": "คลังสินค้า พื้นที่เกินกว่า 300 ตาราง เมตรขึ้นไป"},
    {"value": "503", "text": "เรือนคนใช้ /ครัว"},
    {"value": "504", "text": "โรงจอดรถ"},
    {"value": "505", "text": "สถานศึกษา"},
    {"value": "506/1", "text": "โรงแรม ความสูงไม่เกิน 5 ชั้น"},
    {"value": "506/2", "text": "โรงแรม ความสูงเกินกว่า 5 ชั้นขึ้นไป"},
    {"value": "507", "text": "โรงมหรสพ"},
    {"value": "508", "text": "สถานพยาบาล"},
    {"value": "509/1", "text": "สำนักงาน ความสูงไม่เกิน 5 ชั้น"},
    {"value": "509/2", "text": "สำนักงาน ความสูงเกินกว่า 5 ชั้นขึ้นไป"},
    {"value": "510", "text": "ภัตตาคาร"},
    {"value": "511/1", "text": "ห้างสรรพสินค้า"},
    {"value": "511/2", "text": "อาคารพาณิชยกรรม ประเภทค้าปลีกค้าส่ง"},
    {"value": "512", "text": "สถานีบริการน้ำมันเชื้อเพลิง"},
    {"value": "513", "text": "โรงงาน"},
    {"value": "514", "text": "ตลาด พื้นที่ไม่เกิน 1,000 ตารางเมตร"},
    {"value": "515", "text": "ตลาด พื้นที่เกินกว่า 1,000 ตารางเมตรขึ้นไป"},
    {"value": "516", "text": "อาคารพาณิชย์ ประเภทโฮมออฟฟิศ"},
    {"value": "517", "text": "โรงเลี้ยงสัตว์"},
    {"value": "518", "text": "โรงงานซ่อมรถยนต์"},
    {"value": "519", "text": "อาคารจอดรถ"},
    {"value": "520/1", "text": "อาคารอยู่อาศัยรวม ความสูงไม่เกิน 5 ชั้น"},
    {"value": "520/2", "text": "อาคารอยู่อาศัยรวม ความสูงเกินกว่า 5 ชั้นขึ้นไป"},
    {"value": "521", "text": "ป้อมยาม"},
    {"value": "522", "text": "อาคารพาณิชย์ ประเภทโชว์รูมรถยนต์"},
    {"value": "523", "text": "ห้องน้ำรวม"},
    {"value": "601", "text": "รั้วคอนกรีต"},
    {"value": "602", "text": "รั้วลวดหนาม"},
    {"value": "603", "text": "รั้วสังกะสี"},
    {"value": "604", "text": "รั้วลวดถัก"},
    {"value": "605", "text": "รั้วไม้"},
    {"value": "606", "text": "รั้วเหล็กดัด"},
    {"value": "607", "text": "รั้วอัลลอยด์"},
    {"value": "608", "text": "สระว่ายน้ำ"},
    {"value": "609", "text": "ลานกีฬาอเนกประสงค์"},
    {"value": "610", "text": "ถนนคอนกรีต"},
    {"value": "611", "text": "ลานคอนกรีต"},
    {"value": "612", "text": "ถนนลาดยาง"},
    {"value": "613", "text": "ป้ายโฆษณา"},
    {"value": "614", "text": "ท่าเทียบเรือ"}
]

class TreasuryScraper:
    def __init__(self):
        self.driver = None
        self.base_url = "https://assessprice.treasury.go.th/"

    def setup_driver(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def get_property_types(self):
        """
        Navigates to the page and extracts available property types from the dropdown.
        Returns FALLBACK_PROPERTY_TYPES if extraction fails.
        """
        if not self.driver:
            self.setup_driver()
        
        try:
            self.driver.get(self.base_url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            
            # Try to find the dropdown items directly
            time.sleep(2) 
            items = self.driver.find_elements(By.CSS_SELECTOR, "li.amos-list-li-item")
            
            property_types = []
            for item in items:
                text = item.get_attribute("data-amos-prop-displayed-value")
                value = item.get_attribute("data-amos-prop-value")
                if text and value:
                    property_types.append({"text": text, "value": value})
            
            if property_types:
                # Remove duplicates
                unique_types = []
                seen = set()
                for pt in property_types:
                    if pt['text'] not in seen:
                        unique_types.append(pt)
                        seen.add(pt['text'])
                return unique_types
            else:
                print("No items found, using fallback.")
                return FALLBACK_PROPERTY_TYPES

        except Exception as e:
            print(f"Error getting property types: {e}. Using fallback.")
            return FALLBACK_PROPERTY_TYPES

    def scrape_data(self, province, property_type_text):
        """
        Performs the search and scrapes the result table.
        """
        logs = []
        def log(msg):
            print(msg)
            logs.append(msg)

        # Ensure driver is running
        if not self.driver:
            self.setup_driver(headless=False)
            self.driver.get(self.base_url)
            time.sleep(2)

        try:
            # Force reload to ensure clean state for every iteration
            log("DEBUG: Refreshing page for new search...")
            self.driver.get(self.base_url)
            # time.sleep(1) # Removed fixed wait, relying on page load
            
            # Check if we need to handle the "Buildings" tab again
            # (The reload should put us back at start)

            # 0. Click "สิ่งปลูกสร้าง" (Buildings) Tab
            # Retry logic for tab click
            max_tab_retries = 3
            for attempt in range(max_tab_retries):
                try:
                    # log(f"DEBUG: Attempting to click 'สิ่งปลูกสร้าง' tab (Attempt {attempt+1})...")
                    
                    # Nuke overlays
                    try:
                        self.driver.execute_script("""
                            var overlays = document.querySelectorAll('.amos-panel-underlay');
                            overlays.forEach(function(el) { el.style.display = 'none'; });
                        """)
                    except:
                        pass

                    tab = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'สิ่งปลูกสร้าง')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", tab)
                    # log("DEBUG: Clicked 'สิ่งปลูกสร้าง' tab via JS.")
                    
                    time.sleep(0.2) # Minimal wait for animation start
                    
                    # Verify if input appears
                    try:
                        WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((By.ID, "uniqName_19_0"))
                        )
                        # log("DEBUG: Tab switch successful (Input found).")
                        break # Success
                    except:
                        log("DEBUG: Input not found yet, retrying tab click...")
                except Exception as e:
                    log(f"DEBUG: Tab click failed: {e}")

            # 1. Input Province (uniqName_19_0)
            try:
                # log("DEBUG: Step 1 - Input Province")
                
                # Try to find the PARENT widget first and click it to activate
                try:
                    parent_widget = self.driver.find_element(By.ID, "amos_uniqName_19_0")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", parent_widget)
                    parent_widget.click()
                    # log("DEBUG: Clicked parent widget") # Reduce noise
                    # time.sleep(0.1)
                except:
                    pass # Ignore parent click failure

                # Target the specific ID provided by user
                # Wait for VISIBILITY now, not just presence
                prov_input = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "uniqName_19_0"))
                )
                
                try:
                    prov_input.click()
                    prov_input.clear()
                    prov_input.send_keys(province)
                except Exception as e:
                    # log(f"DEBUG: Standard type failed ({e}), trying JS...")
                    self.driver.execute_script("arguments[0].value = arguments[1];", prov_input, province)
                    # Trigger events
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", prov_input)
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", prov_input)
                
                time.sleep(0.2) # Minimal wait for dropdown
                
                # Try to select from the dropdown if it appears
                try:
                    # Wait for dropdown item "ภูเก็ต"
                    prov_item = WebDriverWait(self.driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, f"//li[contains(text(), '{province}')]"))
                    )
                    prov_item.click()
                    # log(f"DEBUG: Selected '{province}' from dropdown.")
                except:
                    # log(f"DEBUG: Could not click dropdown item for '{province}'. Trying Enter key.")
                    from selenium.webdriver.common.keys import Keys
                    prov_input.send_keys(Keys.RETURN)

            except Exception as e:
                return {"error": f"Step 1 (Input Province) failed: {str(e)}", "logs": logs}
            
            # 2. Select Property Type (uniqName_19_4)
            try:
                # log(f"DEBUG: Step 2 - Select Property Type: {property_type_text}")
                
                # Try to find the PARENT widget first and click it to activate
                try:
                    # Assuming pattern amos_uniqName_19_4 based on province
                    parent_widget = self.driver.find_element(By.ID, "amos_uniqName_19_4")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", parent_widget)
                    parent_widget.click()
                    # time.sleep(0.1)
                except:
                    pass

                # Target the specific ID provided by user for property type
                prop_input = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "uniqName_19_4"))
                )
                
                # Force set value via JS first (most reliable for Dojo)
                self.driver.execute_script("arguments[0].value = arguments[1];", prop_input, property_type_text)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", prop_input)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", prop_input)
                time.sleep(0.2) # Minimal wait for validation
                
                # Verify value
                current_val = prop_input.get_attribute("value")
                if current_val != property_type_text:
                    # log(f"DEBUG: Value mismatch! Expected '{property_type_text}', got '{current_val}'. Retrying JS set...")
                    self.driver.execute_script("arguments[0].value = arguments[1];", prop_input, property_type_text)
                    # time.sleep(1)
                
                # Select from dropdown (optional but good for triggering internal logic)
                try:
                    # The property type text might be long, so we use contains or exact match
                    prop_item = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, f"//li[contains(text(), '{property_type_text}')]"))
                    )
                    prop_item.click()
                    # log(f"DEBUG: Selected '{property_type_text}' from dropdown.")
                except:
                    # log(f"DEBUG: Could not click dropdown item for '{property_type_text}'. Using Enter key as backup.")
                    from selenium.webdriver.common.keys import Keys
                    prop_input.send_keys(Keys.RETURN)

            except Exception as e:
                return {"error": f"Step 2 (Select Property) failed: {str(e)}", "logs": logs}

            # 3. Click Search "ค้นหา"
            try:
                log("DEBUG: Step 3 - Clicking Search")
                # Try multiple selectors for Search button
                search_selectors = [
                    "//label[contains(text(), 'ค้นหา')]",
                    "//div[contains(text(), 'ค้นหา')]",
                    "//button[contains(text(), 'ค้นหา')]",
                    "//*[text()='ค้นหา']"
                ]
                search_btn = None
                for selector in search_selectors:
                    try:
                        search_btn = self.driver.find_element(By.XPATH, selector)
                        if search_btn:
                            break
                    except:
                        continue
                
                if search_btn:
                    # Force click
                    self.driver.execute_script("arguments[0].click();", search_btn)
                    log("DEBUG: Clicked Search button.")
                else:
                    return {"error": "Search button not found", "logs": logs}
            except Exception as e:
                return {"error": f"Step 3 (Click Search) failed: {str(e)}", "logs": logs}
            
            # 4. Wait for "แสดงรายละเอียด" and click
            try:
                log("DEBUG: Waiting for 'แสดงรายละเอียด' button...")
                details_btn = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.lb-detail"))
                )
                # Force click
                self.driver.execute_script("arguments[0].click();", details_btn)
                log("DEBUG: Clicked 'แสดงรายละเอียด'.")
            except Exception as e:
                log(f"DEBUG: 'แสดงรายละเอียด' button not found or clickable: {e}")
                # If no results, this button might not appear.
                pass
            
            # 5. Wait for table and data
            try:
                log("DEBUG: Waiting for table data (tr.row-data)...")
                # Wait for at least one row of data to appear
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tr.row-data"))
                )
                log("DEBUG: Table data found.")
            except:
                # Capture screenshot and values for debugging
                screenshot_path = f"screenshot_no_data_{time.time()}.png"
                self.driver.save_screenshot(screenshot_path)
                log(f"DEBUG: No data rows found. Screenshot saved to {screenshot_path}")
                
                return {
                    "error": "No data rows found (possibly no results)", 
                    "logs": logs,
                    "screenshot": screenshot_path
                }
            
            # 6. Extract Data
            try:
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                # Target the specific table class from user snippet
                table = soup.find('table', class_='amos-table-interactive')
                if not table:
                    table = soup.find('table') # Fallback
                
                if not table:
                    return {"error": "Table element not found in HTML", "logs": logs}
                
                # Extract headers, ignoring hidden ones
                headers = []
                for th in table.find_all('th'):
                    if "amos-hide" not in th.get('class', []):
                        headers.append(th.get_text(strip=True))
                
                rows = []
                tbody = table.find('tbody')
                if tbody:
                    for tr in tbody.find_all('tr'):
                        # Skip hidden rows or non-data rows
                        if "amos-hide" in tr.get('class', []):
                            continue
                        if "row-data" not in tr.get('class', []):
                            continue
                        
                        cells = []
                        for td in tr.find_all('td'):
                            if "amos-hide" not in td.get('class', []):
                                cells.append(td.get_text(strip=True))
                        
                        if cells:
                            rows.append(cells)
                
                log(f"DEBUG: Extracted {len(rows)} rows.")
                if len(rows) == 0:
                    log(f"DEBUG: Table HTML snippet: {str(table)[:500]}")

                return {
                    "headers": headers,
                    "rows": rows,
                    "province": province,
                    "property_type": property_type_text,
                    "logs": logs
                }
            except Exception as e:
                 return {"error": f"Error extracting data: {e}", "logs": logs}

        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "logs": logs}
