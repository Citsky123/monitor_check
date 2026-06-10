from encodings.punycode import T

from flask.scaffold import F
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import logging
import sys
import io

# ===================== 【编码修复】 =====================
# 解决繁体系统下日志乱码问题
if sys.platform == 'win32':
    # Windows下使用UTF-8编码输出
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ===================== 【固定配置】 =====================
CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
CHROME_DRIVER_PATH = r"D:\VScode\check\chromedriver-win32\chromedriver.exe"
USER_ACCOUNT = "H033679"
USER_PWD = "H033679"
HEADLESS_MODE = True  # 无头模式开关：True=无头模式(速度快)，False=可视化模式(便于调试)
# =================================================================

# 设置日志（UTF-8编码）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
    encoding='utf-8' if sys.version_info >= (3, 9) else None
)
logger = logging.getLogger(__name__)

class AutoInspection:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """设置浏览器驱动【性能优化：无头模式+减少等待】"""
        try:
            options = webdriver.ChromeOptions()
            options.binary_location = CHROME_PATH

            # ========== 性能优化：无头模式（根据配置启用/禁用）==========
            if HEADLESS_MODE:
                options.add_argument('--headless=new')
                logger.info("无头模式已启用（运行速度更快）")
            else:
                logger.info("可视化模式（便于调试）")
            
            # 性能优化参数
            options.add_argument('--disable-images')  # 禁用图片
            options.add_argument('--disable-extensions')  # 禁用扩展
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            
            # 防检测参数
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 页面加载策略优化
            options.page_load_strategy = 'none'
            
            # 窗口设置（无头模式也需要设置窗口大小）
            options.add_argument('--window-size=1920,1080')
            
            # 绑定本地驱动启动
            service = Service(executable_path=CHROME_DRIVER_PATH)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # 隐藏webdriver标识
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # 智能等待配置（超时时间缩短为5秒）
            self.wait = WebDriverWait(self.driver, 5)
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(15)
            
            logger.info("浏览器驱动设置完成")
        except Exception as e:
            logger.error(f"驱动设置失败: {e}")
            raise
    
    def login(self):
        """登录系统【优化：减少固定等待，使用智能等待】"""
        try:
            logger.info("正在导航到登录页面...")
            self.driver.get("http://192.168.51.146:3002/#/mom_app/pages/login/login")

            # 智能等待：等待输入框出现
            logger.info("正在输入登录信息...")

            # 账号输入框
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "uni-input input"))
            )
            username_input.clear()
            username_input.send_keys("H033679")
            logger.info("已输入账号")

            # 密码输入框
            password_inputs = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "uni-input input"))
            )
            if len(password_inputs) >= 2:
                password_inputs[1].clear()
                password_inputs[1].send_keys("H033679")
                logger.info("已输入密码")
            else:
                # 备选方案
                logger.info("使用备选方案查找密码输入框...")
                password_input = self.driver.find_element(By.XPATH, "//uni-view[contains(text(), '密码')]/following-sibling::uni-view//input")
                password_input.clear()
                password_input.send_keys("H033679")
                logger.info("已输入密码（备选方案）")

            # 点击登录按钮
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//uni-view[contains(@class, 'login-btn') and contains(text(), '登录')]"))
            )
            login_button.click()
            logger.info("登录信息已提交")

            # 智能等待：等待登录完成
            self.wait.until(EC.any_of(
                EC.url_contains("index"),
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '点检任务')]"))
            ))
            logger.info("登录成功")

        except Exception as e:
            logger.error(f"登录失败: {e}")
            try:
                self.driver.save_screenshot("login_error.png")
                logger.info("已保存错误截图: login_error.png")
            except:
                pass
            raise

    def navigate_to_inspection_tasks(self):
        """导航到点检任务页面【优化：减少固定等待】"""
        try:
            logger.info("正在导航到点检任务...")
            # 点击点检任务菜单
            inspection_task_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '点检任务')]"))
            )
            # 强制滚动到元素可见
            self.driver.execute_script("arguments[0].scrollIntoView();", inspection_task_link)
            inspection_task_link.click()
            logger.info("已点击点检任务页面")

            # 智能等待：等待任务列表元素或页面标题
            try:
                self.wait.until(EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "uni-view[class*='card-box1']")),
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '点检任务列表')]"))
                ))
                logger.info("已进入点检任务页面")
            except:
                # 页面可能没有任务，不等待，让后续逻辑判断
                logger.info("智能等待超时，继续后续处理")
        except Exception as e:
            logger.error(f"导航到点检任务失败: {e}")
            # 不抛出异常，让程序继续
            try:
                self.driver.save_screenshot("nav_error.png")
                logger.info("已保存错误截图")
            except:
                pass
    
    def process_inspection_tasks(self):
        """处理所有点检任务【优化：减少固定等待，使用智能等待】"""
        task_count = 0

        while True:
            try:
                # 直接查找任务列表（不使用wait避免超时）
                task_items = self.driver.find_elements(By.CSS_SELECTOR, "uni-view[class*='card-box1']")

                if not task_items:
                    logger.info("没有找到更多点检任务，任务完成！")
                    break

                logger.info(f"找到 {len(task_items)} 个任务，开始处理第一个任务...")
                task_items[0].click()

                # 智能等待：等待任务详情页面加载
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//uni-view[contains(text(), 'OK')]")))
                logger.info("任务详情页面加载完成")

                if self.process_task_detail():
                    task_count += 1
                    logger.info(f"成功完成第 {task_count} 个点检任务")
                    # 保存后等待页面更新
                    time.sleep(2)
                else:
                    logger.warning("任务处理失败，继续下一个任务")
                    # 失败时尝试返回任务列表
                    try:
                        self.driver.back()
                        logger.info("已返回任务列表")
                        time.sleep(3)
                    except:
                        logger.warning("返回任务列表失败")

            except Exception as e:
                logger.error(f"处理任务时出错: {e}")
                # 尝试返回任务列表
                try:
                    self.driver.back()
                    logger.info("异常情况下已返回任务列表")
                    time.sleep(3)
                except:
                    logger.warning("异常情况下返回任务列表失败")

        return task_count
    
    def process_task_detail(self):
        """处理任务详情【优化：减少点击间隔等待】"""
        try:
            logger.info("正在处理任务详情...")
            click_count = 0

            # 智能等待：等待OK按钮出现
            ok_buttons = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//uni-view[contains(text(), 'OK')]")))

            if ok_buttons:
                logger.info("开始连续点击5次OK按钮")
                for i in range(5):
                    try:
                        ok_buttons[0].click()
                        click_count += 1
                        logger.debug(f"第 {i+1}/5 次点击OK按钮（总点击次数：{click_count}）")
                        # 减少等待时间，从1秒降到0.3秒
                        time.sleep(0.3)
                    except Exception as e:
                        logger.error(f"第 {i+1} 次点击OK按钮失败: {e}")
                        # 重新获取按钮
                        ok_buttons = self.driver.find_elements(By.XPATH, "//uni-view[contains(text(), 'OK')]")
                        if not ok_buttons:
                            logger.warning("OK按钮消失，中断点击")
                            break
            else:
                logger.warning("未找到OK按钮，无法执行连续点击操作")
                return False

            logger.info("开始查找保存按钮")
            # 智能等待：等待保存按钮出现
            save_buttons = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//uni-view[contains(text(), '保存')]")))

            if save_buttons:
                save_buttons[0].click()
                logger.info("点击保存按钮完成")
            else:
                logger.warning("未找到保存按钮，流程中断")
                return False

            return True

        except Exception as e:
            logger.error(f"处理任务详情失败: {e}")
            return False

    def run(self):
        """运行自动点检程序【优化：移除input阻塞】"""
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
                logger.info("程序执行完毕，2秒后自动关闭浏览器...")
                time.sleep(2)
                self.driver.quit()
                logger.info("浏览器已关闭")

if __name__ == "__main__":
    auto_inspection = AutoInspection()
    auto_inspection.run()