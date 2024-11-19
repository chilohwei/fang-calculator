# 智能房贷计算器 (Smart Mortgage Calculator)

一个基于 Streamlit 的智能房贷计算器，帮助您轻松计算和比较不同还款方式。

## 功能特点

- 支持等额本息和等额本金两种还款方式
- 可视化还款计划，直观展示每月还款情况
- 智能推荐最优贷款方案
- 支持自定义首付比例
- 包含各类税费计算

## 快速开始

### 使用 Docker（推荐）

我们提供了支持多架构的 Docker 镜像，可以在不同平台上运行：

```bash
# AMD64 架构
docker run -d -p 8501:8501 chiloh/fang-calculator:latest

# ARM64 架构（如 Apple Silicon Mac）
docker run -d -p 8501:8501 chiloh/fang-calculator:latest-arm64
```

访问 http://localhost:8501 即可使用计算器。

### 本地运行

1. 克隆仓库：
```bash
git clone https://github.com/chilohwei/fang-calculator.git
cd fang-calculator
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
streamlit run main.py
```

## 环境要求

- Python 3.9+
- 依赖包见 requirements.txt

## Docker 部署说明

本项目提供了优化的 Docker 镜像，具有以下特点：

- 多阶段构建，优化镜像大小
- 支持 AMD64 和 ARM64 架构
- 内置健康检查
- 使用非 root 用户运行，提高安全性

### 自行构建镜像

如果您想自己构建 Docker 镜像：

```bash
# AMD64 架构
docker buildx build --platform linux/amd64 -t your-tag:latest .

# ARM64 架构
docker buildx build --platform linux/arm64 -t your-tag:latest-arm64 .
```

## 使用说明

1. 输入房屋总价
2. 选择首付比例（20%-80%）
3. 选择贷款年限（最高30年）
4. 输入年利率
5. 选择还款方式
6. 查看计算结果和还款计划

## 数据分析

本项目集成了 Umami 分析，用于收集匿名使用数据，帮助我们改进产品。我们承诺：
- 不收集个人敏感信息
- 仅收集匿名使用数据
- 用户可以选择退出跟踪

如个人开发，请删除 `main.py`中的 Umami 分析代码。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系开发者。

## 项目预览

![image](https://github.com/user-attachments/assets/f0d8f665-9754-4183-bcb6-51f588cd68f0)
![image](https://github.com/user-attachments/assets/1fb4cc43-48f4-41a9-bb0c-3afb5d3a1cda)