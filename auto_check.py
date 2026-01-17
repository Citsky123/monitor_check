from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager  
from selenium.webdriver.chrome.service import Service as ChromeService  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoInspection:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """设置浏览器驱动"""
        try:
            # 自动下载并配置Chrome驱动
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("浏览器驱动设置完成")
        except Exception as e:
            logger.error(f"驱动设置失败: {e}")
            raise
    
    def login(self):
        """登录系统"""
        try:
            logger.info("正在导航到登录页面...")
            self.driver.get("http://192.168.51.146:3002/#/mom_app/pages/login/login")
            
            # 等待页面加载
            time.sleep(5)
            
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
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"登录失败: {e}")
            # 尝试截图保存当前页面状态
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
            # 注意：根据实际页面调整选择器
            inspection_task_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '点检任务')]"))
            )
            inspection_task_link.click()
            time.sleep(3)
            logger.info("已进入点检任务页面")
        except Exception as e:
            logger.error(f"导航到点检任务失败: {e}")
            raise
    
    def process_inspection_tasks(self):
        """处理所有点检任务"""
        task_count = 0
        
        while True:
            try:
                # 等待任务列表加载
                time.sleep(2)
                
                # 查找任务列表中的任务项
                # 注意：根据实际页面结构调整选择器
                task_items = self.driver.find_elements(By.CSS_SELECTOR, "uni-view.card-box1")
                
                if not task_items:
                    logger.info("没有找到更多点检任务，任务完成！")
                    break
                
                logger.info(f"找到 {len(task_items)} 个任务，开始处理第一个任务...")
                
                # 点击第一个任务
                task_items[0].click()
                time.sleep(2)
                
                # 处理任务详情页
                if self.process_task_detail():
                    task_count += 1
                    logger.info(f"成功完成第 {task_count} 个点检任务")
                else:
                    logger.warning("任务处理失败，继续下一个任务")
                
                # 等待返回设备点检界面
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"处理任务时出错: {e}")
                # 尝试返回设备点检界面
                try:
                    self.driver.back()
                    time.sleep(2)
                except:
                    pass
        
        return task_count
    
    
    def process_task_detail(self):

        try:
            logger.info("正在处理任务详情...")
            click_count = 0  # 记录总点击次数
            
            # 1. 连续点击5次OK按钮（1秒1次）
            ok_buttons = self.driver.find_elements(By.XPATH, "//uni-view[contains(text(), 'OK')]")
            if ok_buttons:
                logger.info("开始连续点击5次OK按钮")
                for i in range(5):
                    ok_buttons[0].click()
                    click_count += 1
                    logger.debug(f"第 {i+1}/5 次点击OK按钮（总点击次数：{click_count}）")
                    time.sleep(1)  # 每次点击间隔1秒
            else:
                logger.warning("未找到OK按钮，无法执行连续点击操作")
                return False
            
            # 2. 查找并点击保存按钮
            logger.info("开始查找保存按钮")
            save_buttons = self.driver.find_elements(By.XPATH, "//uni-view[contains(text(), '保存')]")
            if save_buttons:
                save_buttons[0].click()
                logger.info("点击保存按钮完成")
            else:
                logger.warning("未找到保存按钮，流程中断")
                return False
            
            # 3. 等待2秒，确保页面跳转至任务栏
            logger.info("等待2秒，页面自动跳转到任务栏...")
            time.sleep(2)
            
            return True  # 流程正常完成
            
        except Exception as e:
            logger.error(f"处理任务详情失败: {e}")
            return False


    
    def run(self):
        """运行自动点检程序"""
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