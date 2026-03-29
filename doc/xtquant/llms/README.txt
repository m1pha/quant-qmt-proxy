

通过本目录可快速导航本项目 llms 文档内容。

HTTP 访问（替换 `{HOST}` 为实际域名或 IP）：
- http://{HOST}/llms/llms.txt
- http://{HOST}/llms/xtdata.txt
- http://{HOST}/llms/xttrader.txt
- http://{HOST}/llms/xttools.txt
- http://{HOST}/llms/xtquant_example.txt

## 文件说明

- `llms.txt`: 概览与快速上手指南，包含 xtdata + xttrader 核心接口。
- `xtdata.txt`: xtdata 行情模块详解，含 get/download/subscribe 说明与示例。
- `xttrader.txt`: xttrader 交易模块详解，含下单、撤单、query、回调示例。
- `xttools.txt`: xttools 辅助模块说明，含 export/query 功能示例。
- `xtquant_example.txt`: 官方完整示例汇总（来源：https://dict.thinktrader.net/nativeApi/code_examples.html?id=M1Ku17）。

## 快速启动

```bash
cd c:\Users\marti\AppData\Local\Programs\Python\Python312\Lib\site-packages\xtquant\doc
python -m http.server 8000
```

然后浏览： `http://{HOST}/llms/README.txt`

### 规范说明

- 文档采用 `llmstxt` 简洁风格。
- 代码块使用 ```python。
- 标题层级清晰（# / ## / ###）。
