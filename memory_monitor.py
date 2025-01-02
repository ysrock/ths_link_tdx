import pymem
import time
import platform
from ctypes import windll

class MemoryMonitor:
    def __init__(self):
        # 初始化 Windows API
        self.user32 = windll.user32

    def connect_tdx(self, stock_code):
        """
        向通达信广播股票代码
        """
        if stock_code.startswith('6'):  # 上海证券交易所
            TDX_code = '7' + str(stock_code)
        else:  # 深圳证券交易所
            TDX_code = '6' + str(stock_code)
        
        if platform.system() == 'Windows':
            # 注册自定义消息
            UWM_STOCK = self.user32.RegisterWindowMessageW("stock")
            # 发送消息到通达信
            self.user32.PostMessageW(0xFFFF, UWM_STOCK, int(TDX_code), 0)
            print(f"已广播股票代码: {TDX_code}")
        else:
            print("非 Windows 系统，无法广播")

    def monitor_memory(self, process_name, base_offset, pointer_offset, interval=1):
        """
        监控内存地址的值变化，并广播到通达信
        """
        try:
            # 打开进程
            pm = pymem.Pymem(process_name)
            
            # 获取模块基址
            base_address = pymem.process.module_from_name(pm.process_handle, process_name).lpBaseOfDll
            
            # 计算最终地址
            final_address = base_address + base_offset
            
            # 初始化上一次的值
            last_value = None
            
            print(f"开始监控内存地址: {hex(final_address)}")
            while True:
                # 读取指针地址
                pointer_address = pm.read_uint(final_address)
                
                # 读取指针指向的字符串数据
                current_value = pm.read_string(pointer_address + pointer_offset, 7)
                
                # 如果值发生变化
                if current_value != last_value:
                    print(f"值发生变化: {last_value} -> {current_value}")
                    
                    # 取最新字符串的后六位
                    new_value = current_value[-6:] if len(current_value) >= 6 else current_value
                    print(f"后六位字符串: {new_value}")
                    
                    # 向通达信广播
                    self.connect_tdx(new_value)
                    
                    # 更新上一次的值
                    last_value = current_value
                
                # 等待指定的间隔时间
                time.sleep(interval)
        
        except pymem.exception.ProcessNotFound:
            print(f"未找到进程: {process_name}")
        except pymem.exception.MemoryReadError:
            print("无法读取内存")
        except KeyboardInterrupt:
            print("监控已停止")
        except Exception as e:
            print(f"发生错误: {e}")

# 示例：在其他模块中调用
if __name__ == "__main__":
    # 创建 MemoryMonitor 实例
    monitor = MemoryMonitor()
    
    # 设置监控参数
    process_name = "hexin.exe"  # 目标进程名称
    base_offset = 0x017944D8    # 基址偏移量
    pointer_offset = 0x0        # 指针偏移量（如果需要）
    interval = 1                # 监控间隔时间（秒）
    
    # 开始监控
    monitor.monitor_memory(process_name, base_offset, pointer_offset, interval)
