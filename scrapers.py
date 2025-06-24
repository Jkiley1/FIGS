import asyncio
import requests
import os
import pandas as pd
import concurrent.futures
from playwright.async_api import async_playwright
import datetime
import zipfile
from io import BytesIO

def url_to_df(url: str) -> pd.DataFrame:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(BytesIO(response.content))
def entire_vix_process() -> pd.DataFrame:
    async def fetch_vix_futures( cutoff_year: int = None, cutoff_month: int = 1, cutoff_day: int = 1) -> None:
        if cutoff_year:
            if isinstance(cutoff_year, int) or cutoff_year.isdigit():
                cutoff_year = int(cutoff_year)
            else:
                raise TypeError(f"Argument expected int, got {cutoff_year} of type {type(cutoff_year).__name__!r}")
        if isinstance(cutoff_month, int) or cutoff_month.isdigit():
            cutoff_month = int(cutoff_month)
        else:
            raise TypeError(f"Argument expected int, got {cutoff_month} of type {type(cutoff_month).__name__!r}")
        if isinstance(cutoff_day, int) or cutoff_day.isdigit():
            cutoff_day = int(cutoff_day)
        else:
            raise TypeError(f"Argument expected int, got {cutoff_day} of type {type(cutoff_day).__name__!r}")
        async with async_playwright() as p:
            # Choose browser: chromium, firefox, or webkit
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("https://www.cboe.com/us/futures/market_statistics/historical_data/")
            links = page.locator('a', has_text=r"VXT/")
            count = await links.count()
            hrefs = [await links.nth(i).get_attribute("href") for i in range(count)]
            hrefs = [(i[-14:-4].replace('-',''), i) for i in hrefs]
            hrefs = [(datetime.date(int(one[0:4]), int(one[4:6]), int(one[6:])), two) for one, two in hrefs]
            if cutoff_year:
                slicer = datetime.date(cutoff_year, cutoff_month, cutoff_day)
            else: 
                slicer = datetime.date.today()
            hrefs.append((slicer, None))
            hrefs = sorted(hrefs)
            hrefs = [i for _, i in hrefs if slicer < _]
            hrefs = hrefs[:5]
            await browser.close()

        def vix_df():
            dfs = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
                for df_ in pool.map(url_to_df, hrefs):
                    dfs.append(df_)
            return dfs
        df = pd.concat(vix_df())
        df = df[['Settle','Trade Date', 'Open Interest', 'Futures']]
        df.set_index('Trade Date', inplace=True)
        df = df.pivot(values=['Settle', 'Open Interest'],
                   columns='Futures')
        df.dropna(inplace=True)
        return df
    return asyncio.run(fetch_vix_futures())


def AD_line_lol():
    df = pd.read_excel(
    "https://www.mcoscillator.com/data/osc_data/OSC-DATA.xls",
    sheet_name=0)
    df = df.dropna()
    df = df.loc[:, df.columns[0]:df.columns[4]]
    df.columns = ['Date', 'Advances', 'Declines', 'Up Volume', 'Down Volume']
    df.set_index('Date', inplace=True)



async def finra_hy_ig():
    async with async_playwright() as p:
        """Load Page"""
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://www.finra.org/finra-data/fixed-income/market-activity')    

        """Filter only 'CORP' bonds"""
        button = page.locator('finra-button').nth(2)
        await button.wait_for(state="visible")
        await button.click()
        
        await page.locator('input[type="search"]').click()

        await page.locator('span:has-text("Type")').click()

        # I guess these are equivalent??
        # type_button = page.get_by_text("Type", exact=True)
        

        # Filter bonds for corporate bonds
        filter_bar = page.locator("finra-text-filter")
        
        await filter_bar.click()
        await filter_bar.type('CORP')
        await page.get_by_text('Apply Filter').click()

        # Adjust Date Filter
        date = datetime.date.today() - datetime.timedelta(days=200)

        await page.locator('input[type="search"]').click()
        await page.get_by_role("treeitem", name="Date").locator("span").click()
        await page.locator("finra-dropdown").click()
        await page.locator("finra-dropdown-option").filter(has_text="Greater than").click()

        date_filter_bar = page.get_by_role("textbox", name="YYYY-MM-DD")
        await date_filter_bar.click()
        await date_filter_bar.type(str(date))

        await page.get_by_text('Apply Filter').click()
        await page.get_by_text('Done').click()

        await page.locator('finra-button').filter(has_text='Export').click()
        async with page.expect_download() as download_info:
            await page.get_by_text("EXPORT", exact=True).click()

        download = await download_info.value

        """ Apparently the path needs to be 'permanent' """
        download_path = await download.path()

        import shutil
        permanent_path = f'finra_data'

        shutil.copy(download_path, permanent_path)
        await browser.close()
        
        return permanent_path
    
async def process_finra():
    zip_file_path = await finra_hy_ig()

    with open(zip_file_path, 'rb') as f:
        zip_data = f.read()

    zip_buffer = BytesIO(zip_data)

    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        print("Files in zip:", zip_file.namelist())

        for filename in zip_file.namelist():
            if filename.endswith(".csv"):
                csv_data = zip_file.read(filename)
                df = pd.read_csv(BytesIO(csv_data))
                print(df.head)
    # os.remove(zip_file_path)
    return df

def finra_cleaner(df):
    df.rename(columns={'Unnamed: 0': "Metrics"}, inplace=True)

    df = df.pivot_table(
    index=['Date'],
    columns='Metrics',
    values=['High Yield', 'Investment Grade']
    )

    df[('High Yield', 'AD')] = (df[('High Yield', 'Advances')] - df[('High Yield', 'Declines')]).cumsum()
    df[('Investment Grade', 'AD')] = (df[('Investment Grade', 'Advances')] - df[('Investment Grade', 'Declines')]).cumsum()

    df[('High Yield', 'Net Highs')] = (df[('High Yield', '52 Week High')] - df[('High Yield', '52 Week Low')])
    df[('Investment Grade', 'Net Highs')] = (df[('Investment Grade', '52 Week High')] - df[('Investment Grade', '52 Week Low')])
    return df

AD_line_lol()

# df = asyncio.run(process_finra())
# df = finra_cleaner(df)
# df.to_csv('clearned_finra-ya.csv')


# Next up: three dimensional plot of vix curve
#   Scrape: interest rates, put/call ratios