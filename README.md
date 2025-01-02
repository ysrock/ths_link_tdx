# ths_link_tdx
获取同花顺正在浏览的股票代码,并联动通达信
1 按照"同花顺基址"中的方法,找到同花顺正在浏览的股票代码的内存基址
2 用找到的内存基址,替换memory_monitor.py文件中的基址地址 base_offset =0x017944D8    
3 使用memory_monitor.py 监控基址数值变化并联动通达信
