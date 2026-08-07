# 文峰桌面宠物 (WenFeng Desktop Pet)

基于 **Codex Pet Standard** 格式的轻量级桌面宠物，以文峰（闭嘴手势）为角色形象。

## 效果预览

| 状态 | 描述 |
|------|------|
| **idle** | 静止站立，带呼吸微动动画 |
| **shush** | 鼠标悬停/双击时触发闭嘴手势（食指放嘴边 + 眨眼） |

## 快速启动

```bash
cd wenfeng-desktop-pet
python3 start.py
```

浏览器会自动打开 `http://localhost:8765`。

## 交互方式

| 操作 | 效果 |
|------|------|
| 鼠标悬停 | 切换到 shush 状态（闭嘴手势 + 晃动） |
| 鼠标离开 | 回到 idle 状态 |
| 单击 | 随机显示气泡对话 |
| 双击 | 触发 shush 动作 + 对话 |
| 拖拽 | 移动位置 |
| 右键 | 菜单（关于/说话/手势/退出） |

## 项目结构

```
wenfeng-desktop-pet/
├── index.html          # 主页面
├── style.css           # 样式表（动画/气泡/菜单）
├── pet-engine.js       # 核心引擎（状态机/事件系统）
├── app.js              # 应用入口（初始化/回调注册）
├── pet.json            # 宠物配置（Codex Pet Standard 格式）
├── start.py            # 启动脚本
└── assets/
    ├── idle.png        # idle 状态图片
    └── shush.png       # shush 状态图片
```

## 扩展更多动效

在 `pet.json` 的 `states` 中添加新状态，然后在 `assets/` 中添加对应图片：

```json
{
  "states": {
    "idle": { "row": 0, "frames": 4, "interval": 500, "loop": true },
    "shush": { "row": 1, "frames": 4, "interval": 300, "loop": true },
    "wave":  { "row": 2, "frames": 6, "interval": 200, "loop": false }
  }
}
```

在 `app.js` 的 assets 映射中添加：
```js
const assets = {
  idle: './assets/idle.png',
  shush: './assets/shush.png',
  wave: './assets/wave.png',   // 新增
};
```

## 技术栈

- **纯前端**: HTML5 + CSS3 + Vanilla JS（零依赖）
- **动画系统**: CSS keyframes + JS 状态机
- **格式规范**: Codex Pet Standard (pet.json + spritesheet)
- **设计风格**: Chibi 卡通 Q 版，蓝色西装 + 黑框眼镜

## 参考

- [Codex Pet Standard](https://blog.csdn.net/weixin_29708043/article/details/162023487) - pet.json 格式规范
- [Ice-teapop/desktop-pet](https://github.com/Ice-teapop/desktop-pet) - Tauri 透明桌宠参考
- [ClaudeCodePet](https://github.com/WangJunqing-coder/ClaudeCodePet) - Codex Pet 格式实现参考
