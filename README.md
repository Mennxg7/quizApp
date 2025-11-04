# Streamlit 刷题应用（自动生成）

包含从你的 Excel 文件 `/mnt/data/竞赛题库.xlsx` 导入并生成的题库 (questions.json) 以及一个 Streamlit 应用。

## 文件列表
- app.py         (Streamlit 应用)
- questions.json (题库，已从 Excel 中解析)
- requirements.txt

## 本地运行
1. 创建虚拟环境并激活：
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 在项目目录运行：
   ```bash
   streamlit run app.py
   ```
4. 打开浏览器访问命令行给出的本地地址（通常 http://127.0.0.1:8501）

## 在线分享（推荐）
你可以把本文件夹上传到 GitHub，然后连接到 [Streamlit Cloud](https://streamlit.io/cloud) 或 Hugging Face Spaces，部署后会有一个公开链接，别人点击即可访问。

---
解析信息：
- 原始 Excel 读入行数: 1000
- 生成题目数量: 1000
- 导出文件位置: /mnt/data/streamlit_quiz_app
