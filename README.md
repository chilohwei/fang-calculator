# 智能房贷计算器

## Docker 部署

1. 创建`docker-compose.yml`文件
```yml
services:
  app:
    image: chiloh/fang-calculator:latest
    ports:
      - "8501:8501"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

2. 执行`docker-compose up -d`

## 项目预览

![image](https://github.com/user-attachments/assets/f0d8f665-9754-4183-bcb6-51f588cd68f0)
![image](https://github.com/user-attachments/assets/1fb4cc43-48f4-41a9-bb0c-3afb5d3a1cda)