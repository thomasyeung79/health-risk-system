# WellNest AI - 个人健康管理平台

> 一个基于 Streamlit 构建的中英双语个人健康管理平台，整合身体检测、情绪重整、历史追踪与 AI 综合报告。

[![Streamlit App](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B?logo=streamlit)](https://github.com/thomasyeung79/health-risk-system)

## 功能模块

| 模块 | 功能 |
|------|------|
| 🏠 首页 | 登录/注册、语言切换、模块导航 |
| 🩺 健康检测 | 评估 BMI、饮水、睡眠、运动、饮食、屏幕时间、习惯与心理健康 |
| 🧠 情绪重整 | 记录情绪、压力、能量状态，获得结构化情绪引导 |
| 📈 历史记录 | 查看健康与情绪记录的长期变化，支持数据导出 |
| 📋 综合报告 | 生成身体健康与情绪状态的 AI 综合报告（支持 OpenAI / Ollama） |

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/thomasyeung79/health-risk-system.git
cd health-risk-system

# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run web_v1.py
```

## 技术栈

- **前端/框架**: [Streamlit](https://streamlit.io/) 1.38+
- **AI 集成**: OpenAI API / Ollama 本地 AI
- **数据存储**: JSON + CSV
- **可视化**: Matplotlib + Streamlit Charts
- **双语言**: 中文 / English

## 主要特性

- ✅ 8 项健康信号检测与综合评分
- ✅ AI 驱动情绪分析与呼吸引导
- ✅ 历史趋势可视化（健康评分、压力、能量）
- ✅ 健康雷达图
- ✅ 双语界面（中文 / English）
- ✅ 深色模式
- ✅ 数据导出（CSV / JSON）
- ✅ 本地 AI 支持（Ollama）
- ✅ Docker 部署

## 环境变量

```bash
# OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# Ollama 本地 AI（可选）
export OLLAMA_BASE_URL=http://localhost:11434/v1
```

## Docker 部署

```bash
docker build -t wellnest-ai .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-your-key-here wellnest-ai
```

## 许可证

MIT
