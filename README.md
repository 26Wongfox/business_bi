# 金域医学 HTML 看板 Demo

本项目当前以 **HTML 可视化 Demo** 为核心交付，聚焦管理层展示与移动端分享。

## 主要产物

- 医疗风格看板页面：`/Users/a1-6/Downloads/super_man/output/demo_dashboard.html`
- 单文件离线分享版：`/Users/a1-6/Downloads/super_man/output/demo_dashboard_embedded.html`
- 看板数据：`/Users/a1-6/Downloads/super_man/output/demo_data.json`
- 汇报稿：`/Users/a1-6/Downloads/super_man/output/汇报稿_医疗风格.md`
- 项目总结文档：`/Users/a1-6/Downloads/super_man/docs/html看板项目汇总.md`

## 快速使用

1. 本地查看（建议）

```bash
cd /Users/a1-6/Downloads/super_man/output
python3 -m http.server 8000
```

浏览器访问：

- `http://localhost:8000/demo_dashboard.html`

2. 直接分享

将 `demo_dashboard_embedded.html` 发送给他人，可在手机浏览器离线打开。

## 更新数据

```bash
python3 /Users/a1-6/Downloads/super_man/scripts/build_demo_json.py
```

执行后刷新页面即可看到新数据。
