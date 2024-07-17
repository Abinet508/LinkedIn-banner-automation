import json
import pandas as pd
from playwright.async_api import async_playwright,Page,Browser,BrowserContext,Playwright
import asyncio, os,time
from dotenv import load_dotenv

class LinkedinApi:
    """
    This class is used to update the linkedin banner image of the user.
    """
    def __init__(self):
        self.current_path = os.path.dirname(os.path.realpath(__file__))
        load_dotenv(os.path.join(self.current_path,'CREDENTIALS','.env'))
        self.storage_path = os.path.join(self.current_path,'CREDENTIALS','linkedin.json')
        self.screenshot_path = os.path.join(self.current_path,'SCREENSHOTS')
        os.makedirs(self.screenshot_path,exist_ok=True)
        os.makedirs(os.path.join(self.current_path,'BANNER_IMAGES'),exist_ok=True)
        try:
            for file in os.listdir(self.screenshot_path):
                os.remove(os.path.join(self.screenshot_path,file))
        except:
            pass
        self.username = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.headless = True
        self.playwright: Playwright = None
        self.browser:Browser = None
        self.context:BrowserContext = None
        self.page:Page = None
        self.logged_in = True
        self.colors = {}
        self.final_adjustments = {}
        self.image_index = 0
    
    async def get_local_values(self):
        """
        This function is used to get the values from the excel file and the json file.
        
        Args:
            None
        Returns:
            None
        """
        df = pd.read_excel(os.path.join(self.current_path,'DEPENDENCY','data.xlsx'))
        df = df.fillna(0)
        for column in df.columns:
            if df[column].dtype == 'float64':
                df[column] = df[column].astype(int)
    
        for index,row in df.iterrows():
            
            Excel_CROP = {
                "STRAIGHTEN": df['STRAIGHTEN'][1],
                "ZOOM": df['ZOOM'][1]
            }
            
            Excel_FILTERS = {
                "ORIGINAL": row['ORIGINAL'],
                "STUDIO": row['STUDIO'],
                "SPOTLIGHT": row['SPOTLIGHT'],
                "PRIME": row['PRIME'],
                "CLASSIC": row['CLASSIC'],
                "EDGE": row['EDGE'],
                "LUMINATE": row['LUMINATE']
            }
            Excel_ADJUST = {
                "BRIGHTNESS": df['BRIGHTNESS'][1],
                "CONTRAST": df['CONTRAST'][1],
                "SATURATION": df['SATURATION'][1],
                "VIGNETTE": df['VIGNETTE'][1]
            }
            break
        if not os.path.isabs(row['IMAGE']) and not os.path.exists(row['IMAGE']):
            self.image_path = row['IMAGE'].replace('..',self.current_path)
        else:
            self.image_path = row['IMAGE']
        with open(os.path.join(self.current_path,'DEPENDENCY','adjustable.json'),'r') as f:
            self.selectors = json.load(f)
        Json_CROP = self.selectors['CROP']
        Json_FILTERS = self.selectors['FILTERS']
        Json_ADJUST = self.selectors['ADJUST']
        self.final_crop = {}
        for key,value in Excel_CROP.items():
            if value-Json_CROP[key]['THRESHOLD'] != Json_CROP[key]['DEFAULT']:
                self.final_crop[key] = value-Json_CROP[key]['THRESHOLD']
        self.final_adjust = {}
        for key,value in Excel_ADJUST.items():
            if value-Json_ADJUST['THRESHOLD'] != Json_ADJUST['DEFAULT']:
                self.final_adjust[key] = value-Json_ADJUST['THRESHOLD']
                
        self.final_filters = {}
        for key,value in Excel_FILTERS.items():
            if value != Json_FILTERS[key]['DEFAULT'] and value:
                self.final_filters[key] = value
        self.final_adjustments = {
            "CROP": self.final_crop,
            "ADJUST": self.final_adjust,
            "FILTERS": self.final_filters
        }
    
    async def get_colors(self):
        """
        This function is used to get the colors for the terminal.
        
        Args:
            None
        Returns:
            None        
        """
        self.colors = {
    "black": "\033[0;30m{}\033[0m",
    "red": "\033[0;31m{}\033[0m",
    "green": "\033[0;32m{}\033[0m",
    "yellow": "\033[0;33m{}\033[0m",
    "blue": "\033[0;34m{}\033[0m",
    "magenta": "\033[0;35m{}\033[0m",
    "cyan": "\033[0;36m{}\033[0m",
    "light_gray": "\033[0;37m{}\033[0m",
    "dark_gray": "\033[1;30m{}\033[0m",
    "light_red": "\033[1;31m{}\033[0m",
    "light_green": "\033[1;32m{}\033[0m",
    "light_yellow": "\033[1;33m{}\033[0m",
    "light_blue": "\033[1;34m{}\033[0m",
    "light_magenta": "\033[1;35m{}\033[0m",
    "light_cyan": "\033[1;36m{}\033[0m",
    "white": "\033[1;37m{}\033[0m"
}
    
    async def get_image_dependency(self):
        """
        This function is used to get the image dependency.
        """
        await self.print_text('GETTING REQUIRED VALUES ...',color='yellow')
        await self.get_local_values()
        await self.print_text('VALUES FETCHED ...',color='green')
        
    async def apply_filters(self,filter_name:str,value:int,filter_image:bool=False,adjust_image:bool=False):
        """
        This function is used to apply the filters on the image.

        Args:
            filter_name (str): name of the filter to be applied.
            value (int): value of the filter to be applied.
            filter_image (bool, optional): if the filter is to be applied on the image. Defaults to False.
            adjust_image (bool, optional): if the filter is to be adjusted. Defaults to False.
        """
        if not adjust_image:
            await self.page.get_by_label(filter_name.capitalize()).click()
        else:
            await self.page.get_by_role("button", name=filter_name.capitalize()).click()
        self.image_index+=1
        await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}{filter_name}.png'))
        await self.print_text(f'APPLYING {filter_name} ...',color='yellow')
        if not filter_image:
            await self.page.get_by_label(filter_name.capitalize()).fill(str(value))
            self.image_index+=1
            await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}{filter_name}{value}.png'))

    async def filter_image(self,filters:dict):
        """
        This function is used to filter the image.

        Args:
            filters (dict): dictionary containing the filters to be applied.
        """
        if not filters:
            return
        await self.page.get_by_role("tab", name="Filters").click()
        self.image_index+=1
        await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Filters.png'))
        await self.print_text('APPLYING FILTERS ...',color='yellow')
        for key,value in filters.items():
            await self.apply_filters(key,value,filter_image=True)
            self.image_index+=1
            await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Filter{key}.png'))
            await self.print_text(f'{key} FILTER APPLIED ...',color='green')
            
    async def crop_image(self,crop_values:dict):
        """
        This function is used to zoom and straighten the image.

        Args:
            crop_values (dict): dictionary containing the values for zoom and straighten.
        """
        if not crop_values:
            return
        await self.page.get_by_role("tab", name="Crop").click()
        self.image_index+=1
        await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Crop.png'))
        await self.print_text('CROPPING IMAGE ...',color='yellow')
        for key,value in crop_values.items():
            await self.apply_filters(key,value)
            self.image_index+=1
            await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Crop{key}.png'))
            await self.print_text(f'{key} SET TO {value} ...',color='green')
            
    async def adjust_image(self,adjust_values:dict):
        """
        This function is used to adjust the image.

        Args:
            adjust_values (dict): dictionary containing the values for adjusting the image.
        """
        if not adjust_values:
            return
        await self.page.get_by_role("tab", name="Adjust").click()
        self.image_index+=1
        await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Adjust.png'))
        await self.print_text('ADJUSTING IMAGE ...',color='yellow')
        for key,value in adjust_values.items():
            
            await self.apply_filters(key,value,filter_image = False, adjust_image=True)
            self.image_index+=1
            await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Adjust{key}.png'))
            await self.print_text(f'{key} ADJUSTED TO {value} ...',color='green')
    
    async def print_text(self,text:str, color:str='black'):
        """
        This function is used to print the text in the terminal.

        Args:
            text (str): text to be printed.
            color (str, optional): color of the text. Defaults to 'black'.
        """
        print(self.colors[color].format(text))
        
    async def login(self):
        """
        This function is used to login to the linkedin account.

        Raises:
            Exception: if the authentication is required.

        Returns:
            bool: if the user is logged in or not.
        """
        loaded = False
        while not loaded:
            try:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
                if os.path.exists(self.storage_path):
                    self.context = await self.browser.new_context(storage_state=self.storage_path)
                else:
                    self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
                await self.print_text('OPENING LINKEDIN ...',color='yellow')
                await self.page.goto('https://www.linkedin.com/in/')
                await self.page.wait_for_load_state('load')
                await self.print_text('LINKEDIN OPENED ...',color='green')
                if self.page.url.startswith('https://www.linkedin.com/in/') and  'https://www.linkedin.com/in/?' not in self.page.url:
                    await self.print_text('AUTHENTICATED ...',color='green')
                    self.image_index+=1
                    await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Feed.png'))
                    return self.logged_in
                elif self.page.url.startswith('https://www.linkedin.com/feed/') and 'https://www.linkedin.com/feed/?' not in self.page.url:
                    await self.print_text('AUTHENTICATED ...',color='green')
                    self.image_index+=1
                    await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Feed.png'))
                    await self.page.goto('https://www.linkedin.com/in/')
                    await self.page.wait_for_load_state('load')
                    self.image_index+=1
                    await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Profile.png'))
                    self.logged_in = True
                    return self.logged_in
                else:
                    if self.headless:
                        self.headless = False
                        await self.print_text('AUTHENTICATION REQUIRED ...',color='yellow')
                        raise Exception('Authentication Required')
                await self.page.goto('https://www.linkedin.com/login')
                await self.page.wait_for_load_state('load')
                self.image_index+=1
                await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Login.png'))
                await self.page.fill('input[name="session_key"]',self.username)
                await self.page.fill('input[name="session_password"]',self.password)
                await self.page.click('button[type="submit"]')
                await self.page.wait_for_load_state('load')
                self.image_index+=1
                await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Feed.png')) 
                await self.print_text('SUCCESSFULLY AUTHENTICATED ...',color='green')
                while 'checkpoint' in self.page.url:
                    time.sleep(2)
                await self.page.goto('https://www.linkedin.com/in/')
                await self.context.storage_state(path=self.storage_path)
                await self.page.wait_for_load_state('load')
                self.image_index+=1
                await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Profile.png'))
                self.logged_in = True
                if self.headless:
                    self.headless = False
                    raise Exception('Authentication Required')
                return self.logged_in
            
            except Exception as e:
                await self.browser.close()
                await self.playwright.stop()
                self.logged_in = False
    
    async def update_linkedin_profile_banner(self):
        """
        This function is used to update the linkedin profile banner image.
        
        Returns:
            None
        """
        if self.logged_in:
            self.image_index+=1
            while not 'https://www.linkedin.com/in/' in self.page.url:
                time.sleep(2)
            await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}Profile.png'))
            await self.page.get_by_label("Edit profile background").click()
            await self.page.wait_for_load_state('domcontentloaded',timeout=10000)
            self.image_index+=1
            time.sleep(2)
            await self.page.screenshot(path=os.path.join(self.current_path,"BANNER_IMAGES",f'BEFORE.png'))
            async with self.page.expect_file_chooser(timeout=10000) as file_chooser:
                await self.page.get_by_role("button", name="Change photo").click()
                file_chooser = await file_chooser.value
                await file_chooser.set_files(self.image_path)
                
            await self.print_text('BANNER IMAGE SELECTED ...',color='green') 
            time.sleep(2)
            await self.page.screenshot(path=os.path.join(self.current_path,"BANNER_IMAGES",f'AFTER.png'))
            await self.crop_image(self.final_adjustments['CROP'])
            await self.adjust_image(self.final_adjustments['ADJUST'])
            await self.filter_image(self.final_adjustments['FILTERS'])
            apply_enebled = await self.page.get_by_role("button", name="Apply").is_enabled()
            apply_disabled = await self.page.get_by_label("Edit profile background").is_disabled()
            while not apply_enebled or apply_disabled:
                time.sleep(2)
                
                apply_enebled = await self.page.get_by_role("button", name="Apply").is_enabled()
                apply_disabled = await self.page.get_by_label("Edit profile background").is_disabled()
            if apply_enebled:
                await self.page.get_by_role("button", name="Apply").dispatch_event('click')        
                time.sleep(2)

            self.image_index+=1
            apply_text = await self.page.get_by_role("button", name="Apply").all_inner_texts()
            while 'Apply' in apply_text:
                time.sleep(2)
                apply_text = await self.page.get_by_role("button", name="Apply").all_inner_texts()
            await self.print_text('BANNER APPLIED ...',color='green')
            self.image_index+=1
            await self.page.screenshot(path=os.path.join(self.screenshot_path,f'{self.image_index}BannerApplied.png'))
        else:
            return None
     
    async def main(self):
        """
        This function is used to run the main function.
        """
        await self.get_colors()
        await self.get_image_dependency()
        await self.login()
        await self.update_linkedin_profile_banner()
        await self.browser.close()
        await self.playwright.stop()

if __name__ == '__main__':
    api = LinkedinApi()
    asyncio.run(api.main())

# python linkedin_api.py