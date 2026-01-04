import cfspider

# 基本用法
result = cfspider.mirror("https://www.baidu.com", open_browser=True)
print(f"保存位置: {result.index_file}")

# 指定保存目录
result = cfspider.mirror(
    "https://www.baidu.com",
    save_dir="./my_mirror",
    open_browser=False
)
