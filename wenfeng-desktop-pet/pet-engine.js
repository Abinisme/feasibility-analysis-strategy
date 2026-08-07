/**
 * ============================================
 * 文峰桌面宠物 - 核心引擎 (PetEngine)
 * ============================================
 * 
 * 基于 Codex Pet Standard 格式的轻量级状态机驱动动画引擎
 * 支持：
 *   - 多状态精灵图动画播放
 *   - 鼠标交互（悬停/点击/拖拽）
 *   - 透明窗口 + 置顶
 *   - 可扩展的状态机架构
 * 
 * @author feasibility-analysis-strategy
 * @version 1.0.0
 */

class PetEngine {
  /**
   * @param {Object} options
   * @param {string} options.containerId - 容器元素 ID
   * @param {string} options.imageId - 图片元素 ID
   * @param {string} options.bubbleId - 气泡元素 ID
   * @param {Object} options.config - pet.json 配置对象
   * @param {Object} options.assets - 资源映射 { stateName: imageUrl }
   */
  constructor(options) {
    this.container = document.getElementById(options.containerId);
    this.imageEl = document.getElementById(options.imageId);
    this.bubbleEl = document.getElementById(options.bubbleId);
    this.config = options.config;
    this.assets = options.assets || {};

    // 状态机
    this.currentState = 'idle';
    this.previousState = null;
    this.frameIndex = 0;
    this.animationTimer = null;
    this.isAnimating = false;

    // 交互状态
    this.isHovering = false;
    this.isDragging = false;
    this.dragOffset = { x: 0, y: 0 };
    this.position = { x: null, y: null };

    // 气泡计时器
    this.bubbleTimer = null;

    // 事件回调注册表
    this.callbacks = {
      onStateChange: [],
      onHover: [],
      onHoverEnd: [],
      onClick: [],
      onDoubleClick: [],
      onDragStart: [],
      onDragEnd: [],
    };

    // 初始化
    this._init();
  }

  /* ========== 初始化 ========== */

  _init() {
    this._setPosition();
    this._loadState('idle');
    this._bindEvents();
    this.container.classList.add('interactive');
    
    console.log(`[PetEngine] ${this.config.displayName} v${this.config.version} 已启动`);
  }

  _setPosition() {
    // 默认位置：屏幕右下角
    const screenW = window.innerWidth;
    const screenH = window.innerHeight;
    const petW = this.config.size.width;
    const petH = this.config.size.height;

    this.position.x = screenW - petW - 40;
    this.position.y = screenH - petH - 60;

    this._updatePosition();
  }

  _updatePosition() {
    if (this.position.x !== null && this.position.y !== null) {
      this.container.style.left = `${this.position.x}px`;
      this.container.style.top = `${this.position.y}px`;
    }
  }

  /* ========== 状态机核心 ========== */

  /**
   * 加载并播放指定状态的动画
   * @param {string} stateName - 状态名称（如 'idle', 'shush'）
   */
  _loadState(stateName) {
    const state = this.config.states[stateName];
    if (!state) {
      console.warn(`[PetEngine] 未知状态: ${stateName}`);
      return;
    }

    // 状态切换
    this.previousState = this.currentState;
    this.currentState = stateName;
    this.frameIndex = 0;

    // 更新图片源
    const assetUrl = this.assets[stateName];
    if (assetUrl) {
      this.imageEl.src = assetUrl;
      
      // 更新 CSS 状态类
      this.imageEl.className = 'pet-image';
      if (stateName !== 'idle') {
        this.imageEl.classList.add(`state-${stateName}`);
      }
    }

    // 触发回调
    this._emit('onStateChange', {
      from: this.previousState,
      to: stateName,
      state: state
    });

    // 启动帧动画（如果有多个帧）
    if (state.frames > 1) {
      this._startAnimation(state);
    }
  }

  _startAnimation(state) {
    this._stopAnimation();
    this.isAnimating = true;

    const playFrame = () => {
      if (!this.isAnimating || this.currentState !== (state || this.config.states[this.currentState]).name) return;
      
      // 帧递增
      const currentStateConfig = this.config.states[this.currentState];
      this.frameIndex = (this.frameIndex + 1) % currentStateConfig.frames;

      // 如果不循环且播放完最后一帧，停止
      if (!currentStateConfig.loop && this.frameIndex === 0) {
        this._stopAnimation();
        return;
      }

      this.animationTimer = setTimeout(playFrame, currentStateConfig.interval);
    };

    this.animationTimer = setTimeout(playFrame, state.interval);
  }

  _stopAnimation() {
    if (this.animationTimer) {
      clearTimeout(this.animationTimer);
      this.animationTimer = null;
    }
    this.isAnimating = false;
  }

  /**
   * 切换到指定状态
   * @param {string} stateName
   */
  setState(stateName) {
    if (stateName === this.currentState) return;
    this._loadState(stateName);
  }

  /** 回到 idle 状态 */
  idle() {
    this.setState('idle');
  }

  /* ========== 事件绑定 ========== */

  _bindEvents() {
    // 鼠标进入
    this.container.addEventListener('mouseenter', (e) => {
      this.isHovering = true;
      this._emit('onHover', e);
      
      // 根据 interactions 配置切换状态
      const hoverState = this.config.interactions?.hover;
      if (hoverState) {
        this.setState(hoverState);
      }
    });

    // 鼠标离开
    this.container.addEventListener('mouseleave', (e) => {
      this.isHovering = false;
      this._emit('onHoverEnd', e);
      
      const hoverEndState = this.config.interactions?.hoverEnd;
      if (hoverEndState) {
        this.setState(hoverEndState);
      }
    });

    // 点击
    this.container.addEventListener('click', (e) => {
      this._emit('onClick', e);
    });

    // 双击
    this.container.addEventListener('dblclick', (e) => {
      this._emit('onDoubleClick', e);
    });

    // 拖拽开始
    this.container.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return; // 只响应左键
      
      this.isDragging = true;
      this.container.classList.add('dragging');
      
      this.dragOffset.x = e.clientX - this.position.x;
      this.dragOffset.y = e.clientY - this.position.y;
      
      this._emit('onDragStart', e);

      // 拖拽时切换到指定状态
      const dragState = this.config.interactions?.dragStart;
      if (dragState) {
        this.setState(dragState);
      }

      e.preventDefault();
    });

    // 拖拽移动
    document.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;

      this.position.x = e.clientX - this.dragOffset.x;
      this.position.y = e.clientY - this.dragOffset.y;

      // 边界约束
      const maxX = window.innerWidth - this.config.size.width;
      const maxY = window.innerHeight - this.config.size.height;
      this.position.x = Math.max(0, Math.min(this.position.x, maxX));
      this.position.y = Math.max(0, Math.min(this.position.y, maxY));

      this._updatePosition();
    });

    // 拖拽结束
    document.addEventListener('mouseup', (e) => {
      if (!this.isDragging) return;
      
      this.isDragging = false;
      this.container.classList.remove('dragging');
      
      this._emit('onDragEnd', e);

      // 拖拽结束恢复状态
      const dragEndState = this.config.interactions?.dragEnd;
      if (dragEndState) {
        this.setState(dragEndState);
      }
    });

    // 右键菜单
    this.container.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      this._showContextMenu(e.clientX, e.clientY);
    });

    // 点击其他地方关闭菜单
    document.addEventListener('click', (e) => {
      if (this.contextMenuEl && !this.contextMenuEl.contains(e.target)) {
        this._hideContextMenu();
      }
    });
  }

  /* ========== 对话气泡 ========== */

  /**
   * 显示对话气泡
   * @param {string} text - 气泡文字
   * @param {number} duration - 显示时长(ms)，0 表示不自动消失
   */
  showBubble(text, duration = 3000) {
    if (!this.bubbleEl) return;
    
    this.bubbleEl.textContent = text;
    this.bubbleEl.classList.remove('hidden');
    this.bubbleEl.classList.add('visible');

    if (duration > 0) {
      if (this.bubbleTimer) clearTimeout(this.bubbleTimer);
      this.bubbleTimer = setTimeout(() => this.hideBubble(), duration);
    }
  }

  hideBubble() {
    if (!this.bubbleEl) return;
    this.bubbleEl.classList.remove('visible');
    this.bubbleEl.classList.add('hidden');
  }

  /* ========== 右键菜单 ========== */

  _showContextMenu(x, y) {
    if (!this.contextMenuEl) {
      this.contextMenuEl = this._createContextMenu();
    }
    
    this.contextMenuEl.style.left = `${x}px`;
    this.contextMenuEl.style.top = `${y}px`;
    this.contextMenuEl.classList.add('visible');
  }

  _hideContextMenu() {
    if (this.contextMenuEl) {
      this.contextMenuEl.classList.remove('visible');
    }
  }

  _createContextMenu() {
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.innerHTML = `
      <div class="context-menu-item" data-action="about">关于文峰</div>
      <div class="context-menu-divider"></div>
      <div class="context-menu-item" data-action="say">说句话</div>
      <div class="context-menu-item" data-action="shush">闭嘴手势</div>
      <div class="context-menu-divider"></div>
      <div class="context-menu-item" data-action="top">取消置顶</div>
      <div class="context-menu-item" data-action="exit">退出</div>
    `;

    menu.addEventListener('click', (e) => {
      const item = e.target.closest('.context-menu-item');
      if (item) {
        const action = item.dataset.action;
        this._handleContextAction(action);
        this._hideContextMenu();
      }
    });

    document.body.appendChild(menu);
    return menu;
  }

  _handleContextAction(action) {
    switch (action) {
      case 'about':
        this.showBubble(`${this.config.displayName} v${this.config.version}\n${this.config.description}`, 4000);
        break;
      case 'say':
        const phrases = [
          '嘘...',
          '安静点！',
          '我在思考...',
          '别说话，看盘！',
          '🤫',
          '保持专注',
          'Deep Work 模式开启',
        ];
        this.showBubble(phrases[Math.floor(Math.random() * phrases.length)], 2500);
        break;
      case 'shush':
        this.setState('shush');
        setTimeout(() => this.idle(), 3000);
        break;
      case 'top':
        // 切换置顶（需要 Electron/Tauri API）
        this.showBubble('置顶功能需在桌面客户端中使用', 2000);
        break;
      case 'exit':
        this.showBubble('再见！👋', 1000);
        setTimeout(() => {
          window.close?.() || alert('请直接关闭此页面/窗口');
        }, 1200);
        break;
    }
  }

  /* ========== 事件系统 ========== */

  /**
   * 注册事件监听
   * @param {string} event - 事件名
   * @param {Function} callback - 回调函数
   */
  on(event, callback) {
    if (this.callbacks[event]) {
      this.callbacks[event].push(callback);
    } else {
      console.warn(`[PetEngine] 未知事件类型: ${event}`);
    }
    return this; // 支持链式调用
  }

  _emit(event, data) {
    (this.callbacks[event] || []).forEach(cb => cb(data));
  }

  /* ========== 工具方法 ========== */

  /** 获取当前状态 */
  getState() {
    return this.currentState;
  }

  /** 获取配置 */
  getConfig() {
    return this.config;
  }

  /** 销毁实例 */
  destroy() {
    this._stopAnimation();
    if (this.bubbleTimer) clearTimeout(this.bubbleTimer);
    this.container?.remove();
    this.contextMenuEl?.remove();
    console.log('[PetEngine] 已销毁');
  }
}

// 导出（支持模块和全局两种方式）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PetEngine;
}
