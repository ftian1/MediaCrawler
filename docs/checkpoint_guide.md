# 断点续传功能使用指南 (Checkpoint Resume Feature Guide)

## 功能简介 (Feature Overview)

断点续传功能允许爬虫在中断后从上次停止的位置继续爬取,避免重复爬取已经获取的数据。

The checkpoint resume feature allows the crawler to continue from where it left off after interruption, avoiding duplicate crawling of already fetched data.

## 核心特性 (Core Features)

✅ **自动保存进度** - 每页爬取完成后自动保存checkpoint
✅ **智能恢复** - 启动时自动检测并从上次中断位置继续
✅ **多任务支持** - 支持多个平台、多个关键词独立管理进度
✅ **完成自动清理** - 任务完成后自动清除checkpoint
✅ **灵活配置** - 可通过配置文件启用/禁用

## 快速开始 (Quick Start)

### 1. 启用断点续传功能

编辑 `config/base_config.py` 文件:

```python
# 启用断点续传功能
ENABLE_CHECKPOINT_RESUME = True

# 断点文件保存路径 (可选,默认值如下)
CHECKPOINT_FILE_PATH = "data/checkpoint/crawler_checkpoint.json"
```

### 2. 运行爬虫

正常运行爬虫命令:

```bash
# 小红书关键词搜索
python main.py --platform xhs --lt qrcode --type search

# 抖音创作者主页
python main.py --platform dy --lt qrcode --type creator
```

### 3. 中断和恢复

- **中断**: 按 `Ctrl+C` 或关闭终端窗口
- **恢复**: 重新运行相同的命令,爬虫将自动从上次位置继续

## 工作原理 (How It Works)

### 保存时机

爬虫在每页数据爬取完成后保存checkpoint,包含:
- 平台名称 (platform)
- 爬取类型 (crawler_type)
- 当前关键词/创作者ID
- 最后成功爬取的页码
- 最后爬取的内容ID
- 时间戳

### 恢复逻辑

1. 启动时检查是否存在checkpoint
2. 如果存在,从保存的页码继续
3. 如果不存在,从配置的起始页开始

### Checkpoint文件格式

```json
{
  "xhs_search_编程副业": {
    "platform": "xhs",
    "crawler_type": "search",
    "keyword": "编程副业",
    "creator_id": null,
    "last_page": 5,
    "last_item_id": "note_abc123",
    "timestamp": "2025-01-20T12:30:45.123456",
    "extra_data": {}
  },
  "dy_creator_user_123456": {
    "platform": "dy",
    "crawler_type": "creator",
    "keyword": null,
    "creator_id": "user_123456",
    "last_page": 3,
    "last_item_id": "video_xyz789",
    "timestamp": "2025-01-20T13:15:30.987654",
    "extra_data": {}
  }
}
```

## 使用场景 (Use Cases)

### 场景1: 大量关键词爬取

```python
# config/base_config.py
KEYWORDS = "编程副业,编程兼职,Python教程,AI开发,前端开发"
CRAWLER_MAX_NOTES_COUNT = 1000
ENABLE_CHECKPOINT_RESUME = True
```

如果在爬取过程中网络中断或程序崩溃,重新运行时将从上次中断的关键词和页码继续。

### 场景2: 定时爬取任务

使用cron或定时任务每天爬取新数据:

```bash
# 每天凌晨2点运行
0 2 * * * cd /path/to/MediaCrawler && python main.py --platform xhs --type search
```

启用checkpoint后,即使任务被系统重启中断,也能在下次运行时继续。

### 场景3: 服务器资源受限

在资源受限的服务器上,可以分批爬取:

```python
# 每次运行爬取50条
CRAWLER_MAX_NOTES_COUNT = 50
ENABLE_CHECKPOINT_RESUME = True
```

多次运行直到完成目标数量。

## 高级配置 (Advanced Configuration)

### 自定义Checkpoint路径

```python
# 使用自定义路径
CHECKPOINT_FILE_PATH = "/custom/path/my_checkpoint.json"
```

### 手动管理Checkpoint

```python
from tools.checkpoint import CheckpointManager

# 创建管理器
manager = CheckpointManager("data/checkpoint/custom.json")

# 保存checkpoint
manager.save_checkpoint(
    platform="xhs",
    crawler_type="search",
    keyword="测试关键词",
    last_page=10,
    last_item_id="note_123"
)

# 加载checkpoint
checkpoint = manager.load_checkpoint(
    platform="xhs",
    crawler_type="search",
    keyword="测试关键词"
)

# 清除checkpoint
manager.clear_checkpoint(
    platform="xhs",
    crawler_type="search",
    keyword="测试关键词"
)

# 清除所有checkpoint
manager.clear_all_checkpoints()
```

## 注意事项 (Important Notes)

### ⚠️ 与数据存储配合使用

建议配合数据库存储模式使用,以利用自动去重功能:

```python
SAVE_DATA_OPTION = "db"  # 或 "sqlite"
ENABLE_CHECKPOINT_RESUME = True
```

这样即使checkpoint丢失,数据库也能防止重复数据。

### ⚠️ 配置变更影响

以下配置变更可能导致checkpoint不匹配:
- 修改关键词列表
- 修改平台设置
- 修改爬取类型

建议配置变更前手动清除checkpoint:

```bash
# 删除checkpoint文件
rm data/checkpoint/crawler_checkpoint.json
```

### ⚠️ 多进程并发

当前版本不支持多进程并发爬取同一任务。如需并发,请:
1. 使用不同的checkpoint文件路径
2. 或分配不同的关键词给不同进程

## 故障排除 (Troubleshooting)

### 问题1: Checkpoint未生效

**症状**: 重新运行后从第一页开始

**解决方案**:
1. 检查 `ENABLE_CHECKPOINT_RESUME = True`
2. 确认checkpoint文件存在: `ls data/checkpoint/`
3. 检查日志中是否有 "Resuming from checkpoint" 消息

### 问题2: Checkpoint文件损坏

**症状**: 启动时报JSON解析错误

**解决方案**:
```bash
# 删除损坏的checkpoint文件
rm data/checkpoint/crawler_checkpoint.json
# 重新运行爬虫
python main.py --platform xhs --type search
```

### 问题3: 想要强制重新爬取

**解决方案**:
```python
# 方法1: 临时禁用checkpoint
ENABLE_CHECKPOINT_RESUME = False

# 方法2: 删除checkpoint文件
rm data/checkpoint/crawler_checkpoint.json

# 方法3: 使用代码清除
from tools.checkpoint import CheckpointManager
manager = CheckpointManager()
manager.clear_all_checkpoints()
```

## 性能影响 (Performance Impact)

- **CPU**: 几乎无影响 (仅JSON序列化)
- **内存**: 每个checkpoint约1-2KB
- **磁盘**: checkpoint文件通常 < 100KB
- **网络**: 无影响

## 兼容性 (Compatibility)

| 平台 | 搜索爬取 | 指定帖子 | 创作者主页 |
|------|---------|---------|-----------|
| 小红书 (XHS) | ✅ | ❌ | ✅ |
| 抖音 (DY) | 待实现 | 待实现 | 待实现 |
| 快手 (KS) | 待实现 | 待实现 | 待实现 |
| B站 (Bili) | 待实现 | 待实现 | 待实现 |
| 微博 (WB) | 待实现 | 待实现 | 待实现 |
| 贴吧 (Tieba) | 待实现 | 待实现 | 待实现 |
| 知乎 (Zhihu) | 待实现 | 待实现 | 待实现 |

> 注: 当前仅实现了小红书平台的断点续传功能,其他平台可参考实现。

## 扩展到其他平台 (Extending to Other Platforms)

### 实现步骤

1. **导入CheckpointManager**
```python
from tools.checkpoint import CheckpointManager
```

2. **初始化管理器**
```python
def __init__(self):
    # ... 其他初始化代码 ...
    self.checkpoint_manager = CheckpointManager(config.CHECKPOINT_FILE_PATH) \
        if config.ENABLE_CHECKPOINT_RESUME else None
```

3. **加载checkpoint**
```python
checkpoint = None
if self.checkpoint_manager:
    checkpoint = self.checkpoint_manager.load_checkpoint(
        platform="your_platform",
        crawler_type="search",
        keyword=keyword
    )
    if checkpoint:
        start_page = checkpoint.get("last_page", start_page)
```

4. **保存checkpoint**
```python
if self.checkpoint_manager and last_item_id:
    self.checkpoint_manager.save_checkpoint(
        platform="your_platform",
        crawler_type="search",
        keyword=keyword,
        last_page=page + 1,
        last_item_id=last_item_id
    )
```

5. **清除checkpoint**
```python
if self.checkpoint_manager:
    self.checkpoint_manager.clear_checkpoint(
        platform="your_platform",
        crawler_type="search",
        keyword=keyword
    )
```

详细实现可参考 `media_platform/xhs/core.py`。

## 反馈和贡献 (Feedback and Contribution)

如有问题或建议,欢迎:
- 提交 Issue: https://github.com/NanmiCoder/MediaCrawler/issues
- 提交 PR: https://github.com/NanmiCoder/MediaCrawler/pulls
- 加入讨论群组

## 更新日志 (Changelog)

### v1.0.0 (2025-01-20)
- ✅ 首次发布断点续传功能
- ✅ 支持小红书搜索和创作者模式
- ✅ 完整的测试覆盖
- ✅ 中英文文档
