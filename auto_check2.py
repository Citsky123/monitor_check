from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import logging

# ===================== 【固定配置】 =====================
CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
CHROME_DRIVER_PATH = r"D:\VScode\check\chromedriver-win32\chromedriver.exe"
USER_ACCOUNT = "H033679"
USER_PWD = "H033679"
# =================================================================

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoInspection:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """设置浏览器驱动【新增窗口最大化】"""
        try:
            options = webdriver.ChromeOptions()
            options.binary_location = CHROME_PATH
            
            # +防检测参数
            options.add_argument('--disable-version-check')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.page_load_strategy = 'none'
            options.add_argument('--disable-images')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--mute-audio')
            options.add_argument('--disable-popup-blocking')

            # 绑定本地驱动启动
            service = Service(executable_path=CHROME_DRIVER_PATH)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # 隐藏webdriver标识
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # ========== 新增：窗口最大化【解决视窗过小的核心基础】 ==========
            self.driver.maximize_window()
            
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("浏览器驱动设置完成，窗口已最大化")
        except Exception as e:
            logger.error(f"驱动设置失败: {e}")
            raise
    
    def login(self):
        """登录系统"""
        try:
            logger.info("正在导航到登录页面...")
            self.driver.get("http://192.168.51.146:3002/#/mom_app/pages/login/login")
            
            # 等待页面加载
            time.sleep(3)
            
            # 根据你提供的HTML结构，使用正确的选择器
            logger.info("正在输入登录信息...")
            
            # 账号输入框 - 使用uni-input组件内的input
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "uni-input input"))
            )
            username_input.clear()
            username_input.send_keys("H033679")
            logger.info("已输入账号")
            
            # 密码输入框 - 同样使用uni-input组件内的input，通过索引获取第二个
            password_inputs = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "uni-input input"))
            )
            if len(password_inputs) >= 2:
                password_inputs[1].clear()
                password_inputs[1].send_keys("H033679")
                logger.info("已输入密码")
            else:
                # 备选方案：通过XPath定位密码输入框
                password_input = self.driver.find_element(By.XPATH, "//uni-view[contains(text(), '密码')]/following-sibling::uni-view//input")
                password_input.clear()
                password_input.send_keys("H033679")
            
            # 点击登录按钮 - 可能需要根据实际按钮文本调整
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//uni-view[contains(@class, 'login-btn') and contains(text(), '登录')]"))
            )
            login_button.click()
            logger.info("登录信息已提交")
            
            # 等待登录完成
            time.sleep(5)

        except Exception as e:
            logger.error(f"登录失败: {e}")
            try:
                self.driver.save_screenshot("login_error.png")
                logger.info("已保存错误截图: login_error.png")
            except:
                pass
            raise

    def navigate_to_inspection_tasks(self):
        """导航到点检任务页面"""
        try:
            logger.info("正在导航到点检任务...")
            # 点击点检任务菜单
            inspection_task_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '点检任务')]"))
            )
            # ========== 新增这两行修复代码 开始 ==========
            self.driver.execute_script("arguments[0].scrollIntoView();", inspection_task_link)  # 强制滚动到元素可见，无兼容问题
            time.sleep(0.3)  # 等待滚动完成，不影响你的业务sleep
            # ========== 新增这两行修复代码 结束 ==========
            inspection_task_link.click()
            time.sleep(3)
            logger.info("已进入点检任务页面")
        except Exception as e:
            logger.error(f"导航到点检任务失败: {e}")
            raise
    
    def process_inspection_tasks(self):
        """处理所有点检任务【无修改，保留所有原逻辑+sleep】"""
        task_count = 0
        
        while True:
            try:
                time.sleep(3)
                task_items = self.driver.find_elements(By.CSS_SELECTOR, "uni-view[class*='card-box1']")
                
                if not task_items:
                    logger.info("没有找到更多点检任务，任务完成！")
                    break
                
                logger.info(f"找到 {len(task_items)} 个任务，开始处理第一个任务...")
                task_items[0].click()
                time.sleep(2)
                
                if self.process_task_detail():
                    task_count += 1
                    logger.info(f"成功完成第 {task_count} 个点检任务")
                else:
                    logger.warning("任务处理失败，继续下一个任务")
                
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"处理任务时出错: {e}")
                try:
                    self.driver.back()
                    time.sleep(2)
                except:
                    pass
        
        return task_count
    
    def process_task_detail(self):
        """处理任务详情【无修改，保留所有原逻辑+sleep+点击次数】"""
        try:
            logger.info("正在处理任务详情...")
            click_count = 0  

            ok_buttons = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//uni-view[contains(text(), 'OK')]")))
            if ok_buttons:
                logger.info("开始连续点击5次OK按钮")
                for i in range(5):
                    ok_buttons[0].click()
                    click_count += 1
                    logger.debug(f"第 {i+1}/5 次点击OK按钮（总点击次数：{click_count}）")
                    time.sleep(1)
            else:
                logger.warning("未找到OK按钮，无法执行连续点击操作")
                return False
            
            logger.info("开始查找保存按钮")
            save_buttons = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//uni-view[contains(text(), '保存')]")))
            if save_buttons:
                save_buttons[0].click()
                logger.info("点击保存按钮完成")
            else:
                logger.warning("未找到保存按钮，流程中断")
                return False
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"处理任务详情失败: {e}")
            return False

    def run(self):
        """运行自动点检程序【无修改】"""
        try:
            logger.info("开始自动点检程序...")
            self.setup_driver()
            self.login()
            self.navigate_to_inspection_tasks()
            
            total_tasks = self.process_inspection_tasks()
            
            logger.info(f"自动点检完成！共处理了 {total_tasks} 个任务")
            
        except Exception as e:
            logger.error(f"程序运行失败: {e}")
        finally:
            if self.driver:
                input("按Enter键关闭浏览器...")
                self.driver.quit()
                logger.info("浏览器已关闭")

if __name__ == "__main__":
    auto_inspection = AutoInspection()
    auto_inspection.run()