/**
 * ============================================
 * 文峰桌面宠物 - 应用入口
 * ============================================
 */

(async function init() {
  // 1. 加载 pet.json 配置
  const configResponse = await fetch('./pet.json');
  const config = await configResponse.json();

  // 2. 定义资源映射（状态名 -> 图片路径）
  const assets = {
    idle: './assets/idle.png',
    shush: './assets/shush.png',
  };

  // 3. 初始化引擎
  const wenfeng = new PetEngine({
    containerId: 'pet-container',
    imageId: 'pet-image',
    bubbleId: 'speech-bubble',
    config: config,
    assets: assets,
  });

  // 4. 注册交互回调
  wenfeng
    .on('onStateChange', (data) => {
      console.log(`[状态切换] ${data.from} → ${data.to}`);
    })
    .on('onHover', () => {
      // 悬停时可以额外处理
    })
    .on('onClick', () => {
      // 随机说句话
      const phrases = [
        '嗯？',
        '有事？',
        '🤫',
        '...',
        '看盘呢，别闹',
        'Deep Work 中',
      ];
      if (Math.random() > 0.6) {
        wenfeng.showBubble(phrases[Math.floor(Math.random() * phrases.length)], 2000);
      }
    })
    .on('onDoubleClick', () => {
      wenfeng.showBubble('双击干嘛！别戳我 😤', 2000);
      // 双击时做 shush 动作
      wenfeng.setState('shush');
      setTimeout(() => wenfeng.idle(), 2500);
    });

  // 5. 随机 idle 行为 - 偶尔自动 shush
  setInterval(() => {
    if (wenfeng.getState() === 'idle' && !wenfeng.isHovering && Math.random() > 0.85) {
      wenfeng.setState('shush');
      setTimeout(() => wenfeng.idle(), 2000 + Math.random() * 2000);
    }
  }, 8000);

  // 6. 全局暴露（调试用）
  window.wenfeng = wenfeng;

  console.log('[文峰桌面宠物] 初始化完成 ✅');
  console.log('[提示] 可通过 window.wenfeng 访问实例');
})();
