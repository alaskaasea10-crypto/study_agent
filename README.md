# 学伴 Study Agent

面向大学生的主动服务型学习 AI Agent 系统。

## Streamlit Cloud 部署

在 Streamlit Cloud 中选择本仓库后，将入口文件设置为：

```text
app.py
```

依赖由 `requirements.txt` 安装。项目不依赖本地绝对路径，数据默认写入仓库内的 `data/memory.json`。

## 本地运行

```bash
streamlit run app.py
```

也可以运行命令行演示：

```bash
python main.py demo
```
