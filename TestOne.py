import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 配置 Chrome 选项
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式（若需可视化，可注释此行）
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# 启动浏览器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

try:
    # 1. 打开目标页面
    url = "https://www.chinamoney.com.cn/english/bdInfo/"
    driver.get(url)
    print("页面加载中...")
    time.sleep(3)  # 给 JavaScript 渲染时间

    # 2. 定位 Bond Type 下拉框（通过 ID）
    bond_type_select = wait.until(EC.presence_of_element_located((By.ID, "Bond_Type_select")))
    Select(bond_type_select).select_by_value("100001")  # Treasury Bond 的值
    print("已选择 Bond Type: Treasury Bond")

    # 3. 定位 Issue Year 下拉框（通过 ID）
    year_select = wait.until(EC.presence_of_element_located((By.ID, "Issue_Year_select")))
    Select(year_select).select_by_value("2023")
    print("已选择 Issue Year: 2023")

    # 4. 点击 Search 按钮（通过文本 "Search" 定位）
    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Search')]")))
    search_btn.click()
    print("已点击 Search 按钮")

    # 5. 等待表格出现数据（等待表格容器出现，并至少有一行数据）
    wait.until(EC.presence_of_element_located((By.ID, "sheet-bond-market")))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#sheet-bond-market tbody tr")))
    print("表格数据已加载")

    # 6. 解析表格数据
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table_div = soup.find('div', id="sheet-bond-market")
    table = table_div.find('table')

    # 提取表头（注意：表头在 <thead> 中使用 <td>）
    headers = []
    thead = table.find('thead')
    if thead:
        headers = [th.get_text(strip=True) for th in thead.find_all('td')]
    else:
        # 若没有 thead，从第一行 tr 中取 th/td
        first_row = table.find('tr')
        if first_row:
            headers = [cell.get_text(strip=True) for cell in first_row.find_all(['th', 'td'])]

    # 提取数据行
    data = []
    tbody = table.find('tbody')
    rows = tbody.find_all('tr') if tbody else table.find_all('tr')[1:]  # 跳过表头行
    for row in rows:
        cols = row.find_all('td')
        if cols:
            row_data = [col.get_text(strip=True) for col in cols]
            data.append(row_data)

    # 7. 筛选所需列
    required_cols = ['ISIN', 'Bond Code', 'Issuer', 'Bond Type', 'Issue Date', 'Latest Rating']
    if headers:
        col_indices = {name: idx for idx, name in enumerate(headers) if name in required_cols}
        filtered_data = []
        for row in data:
            filtered_row = [row[col_indices[col]] for col in required_cols if col in col_indices]
            filtered_data.append(filtered_row)
        final_headers = [col for col in required_cols if col in col_indices]
    else:
        # 如果连表头都没有，直接保存原始数据（并提示）
        print("警告：未检测到表头，将直接保存原始数据")
        final_headers = [f"col_{i}" for i in range(len(data[0]))] if data else []
        filtered_data = data

    # 8. 保存为 CSV
    df = pd.DataFrame(filtered_data, columns=final_headers)
    df.to_csv('bond_data.csv', index=False, encoding='utf-8-sig')
    print(f"成功保存 {len(df)} 条数据到 bond_data.csv")

except Exception as e:
    print(f"发生错误: {e}")
    # 调试：保存当前页面源码及截图
    with open("page_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.save_screenshot("debug_screenshot.png")
    print("已保存页面源码和截图，请检查调试文件")

finally:
    driver.quit()