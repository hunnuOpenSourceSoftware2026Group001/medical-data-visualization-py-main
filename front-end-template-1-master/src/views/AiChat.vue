<template>
  <div class="ai-chat-modern">
    <!-- 左侧对话列表 -->
    <div class="sidebar-conversations" :class="{ hidden: !sidebarVisible }">
      <div class="sidebar-header">
        <h3>对话历史</h3>
        <button class="new-chat-btn" :disabled="isGenerating" @click="createNewChat">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 5v14M5 12h14" stroke-width="2" stroke-linecap="round"/>
          </svg>
          {{ isGenerating ? '回复中…' : '新建对话' }}
        </button>
      </div>

      <div class="conversations-list">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          :class="['conversation-item', { active: currentConversationId === conv.id }]"
          @click="switchConversation(conv.id)"
        >
          <div class="conv-info">
            <div v-if="editingId === conv.id" class="conv-edit">
              <input
                v-model="editingTitle"
                class="edit-input"
                ref="editInput"
                @keyup.enter="saveTitle(conv.id)"
                @keyup.esc="cancelEdit"
                @blur="saveTitle(conv.id)"
              />
            </div>
            <div v-else class="conv-title">{{ conv.title }}</div>
            <div class="conv-time">{{ formatDate(conv.updatedAt) }}</div>
          </div>

          <div class="conv-actions">
            <button class="action-btn" title="重命名" @click.stop="startEdit(conv)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke-width="2"/>
                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke-width="2"/>
              </svg>
            </button>
            <button class="action-btn delete" title="删除" @click.stop="deleteConversation(conv.id)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14z" stroke-width="2"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="conversations.length === 0" class="no-conversations">
          暂无对话记录
        </div>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="main-chat-area">
      <div class="chat-header">
        <button class="sidebar-toggle" @click="toggleSidebar">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M3 12h18M3 6h18M3 18h18" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
        <div class="header-info">
          <h2>{{ currentConversation ? currentConversation.title : 'AI医疗助手' }}</h2>
          <span class="header-subtitle">基于 DeepSeek 的智能医疗咨询参考</span>
        </div>
        <div class="header-actions">
          <span :class="['connection-status', connectionState]">
            <span class="status-dot"></span>
            {{ connectionLabel }}
          </span>
          <button
            v-if="connectionState === 'disconnected'"
            class="reconnect-btn"
            @click="reconnect"
          >
            重连
          </button>
        </div>
      </div>

      <div
        v-if="connectionState !== 'connected'"
        :class="['connection-banner', connectionState]"
      >
        <span>{{ connectionBannerText }}</span>
        <button
          class="banner-btn"
          :disabled="connectionState === 'connecting' || connectionState === 'reconnecting'"
          @click="reconnect"
        >
          {{ connectionState === 'disconnected' ? '立即重连' : '连接中…' }}
        </button>
      </div>

      <div class="chat-content" ref="chatContent">
        <!-- 欢迎界面 -->
        <div v-if="!currentMessages.length && !isLoading" class="welcome-screen">
          <div class="welcome-icon">
            <img src="../assets/doctor-avatar.svg" alt="AI助手" @error="handleImageError">
          </div>
          <h3>您好，我是 AI 医疗助手</h3>
          <p>我可以提供健康科普、症状分析和就医建议，但不能替代医生面诊</p>

          <div class="quick-prompts">
            <h4>快速开始</h4>
            <div class="prompt-grid">
              <div class="prompt-card" @click="quickStart('最近感冒了，日常应该注意什么？')">
                <span class="prompt-icon">🤧</span>
                <span>感冒护理</span>
              </div>
              <div class="prompt-card" @click="quickStart('高血压患者日常饮食有哪些注意事项？')">
                <span class="prompt-icon">🩺</span>
                <span>高血压饮食</span>
              </div>
              <div class="prompt-card" @click="quickStart('如何看懂体检报告中的常见指标？')">
                <span class="prompt-icon">📋</span>
                <span>体检报告解读</span>
              </div>
              <div class="prompt-card" @click="quickStart('儿童发烧时家庭护理要注意什么？')">
                <span class="prompt-icon">👶</span>
                <span>儿童发烧</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-else class="messages-container" ref="messagesContainer">
          <div v-for="(message, index) in currentMessages" :key="index" class="message-wrapper">
            <div :class="['message-row', message.role]">
              <div class="message-avatar">
                <img
                  v-if="message.role === 'assistant'"
                  src="../assets/doctor-avatar.svg"
                  alt="助手"
                  @error="handleImageError"
                >
                <div v-else class="user-icon">用</div>
              </div>
              <div class="message-body">
                <div class="message-header">
                  <span class="message-author">
                    {{ message.role === 'assistant' ? 'AI医疗助手' : '您' }}
                    <span v-if="message.safety" class="safety-tag">安全提示</span>
                  </span>
                  <span class="message-time">{{ message.time }}</span>
                </div>
                <div
                  :class="['message-content', { 'safety-message': message.safety }]"
                  v-html="formatMessage(message.content)"
                ></div>
                <div v-if="message.streaming" class="stream-status">
                  <span class="stream-caret"></span>
                  正在生成，可点击“停止”
                </div>
                <div v-else-if="message.stopped" class="stream-status stopped">
                  已停止生成
                </div>
              </div>
            </div>
          </div>

          <!-- 等待首包 -->
          <div v-if="isLoading" class="message-wrapper">
            <div class="message-row assistant">
              <div class="message-avatar">
                <img src="../assets/doctor-avatar.svg" alt="助手" @error="handleImageError">
              </div>
              <div class="message-body">
                <div class="message-header">
                  <span class="message-author">AI医疗助手</span>
                </div>
                <div class="typing-animation">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div v-if="lastError" class="chat-error-banner">
          <span>{{ lastError }}</span>
          <button class="error-close" @click="lastError = ''">×</button>
        </div>

        <div class="input-container">
          <textarea
            v-model="inputMessage"
            @keydown.enter.prevent="handleEnterKey"
            @compositionstart="isComposing = true"
            @compositionend="isComposing = false"
            placeholder="输入您的问题，例如：高血压患者日常要注意什么？"
            class="chat-input"
            :disabled="isGenerating"
            :maxlength="maxInputLength"
            rows="1"
            ref="chatInput"
          ></textarea>

          <button
            v-if="isGenerating"
            class="send-btn stop-btn"
            :disabled="isStopping"
            title="停止生成"
            @click="stopGeneration"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="6" width="12" height="12" rx="2"></rect>
            </svg>
            {{ isStopping ? '停止中' : '停止' }}
          </button>
          <button
            v-else
            class="send-btn"
            :disabled="!canSend"
            title="发送"
            @click="sendMessage"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <div class="input-meta">
          <span>Shift + Enter 换行 | Enter 发送</span>
          <span>{{ inputMessage.length }} / {{ maxInputLength }}</span>
        </div>
        <div class="medical-disclaimer">
          <strong>医疗免责声明：</strong>
          本助手内容由 AI 生成，仅供健康科普和就医参考，不能替代执业医师的诊断、处方和治疗。出现胸痛、呼吸困难、意识障碍等急症，请立即拨打 120。
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import io from "socket.io-client";
import { marked } from "marked";

const STORAGE_KEY = "ai_chat_conversations";
const CURRENT_ID_KEY = "ai_chat_current_id";
const MAX_CONVERSATIONS = 30;
const MAX_MESSAGES_PER_CONVERSATION = 200;
const MAX_INPUT_LENGTH = 2000;
const MAX_HISTORY_MESSAGES = 20;
const RETENTION_DAYS = 30;

export default {
  name: "AiChat",
  data() {
    return {
      conversations: [],
      currentConversationId: null,
      inputMessage: "",
      isLoading: false,
      isStreaming: false,
      isStopping: false,
      socket: null,
      connectionState: "connecting",
      reconnectAttempt: 0,
      editingId: null,
      editingTitle: "",
      sidebarVisible: true,
      activeRequestId: null,
      activeConversationId: null,
      responseTimer: null,
      stopFallbackTimer: null,
      saveTimer: null,
      scrollFrame: null,
      lastError: "",
      isComposing: false,
      manualClose: false,
      maxInputLength: MAX_INPUT_LENGTH,
    };
  },

  computed: {
    currentConversation() {
      return this.findConversation(this.currentConversationId);
    },
    currentMessages() {
      return this.currentConversation ? this.currentConversation.messages : [];
    },
    isGenerating() {
      return this.isLoading || this.isStreaming;
    },
    canSend() {
      return (
        !!this.inputMessage.trim() &&
        !this.isGenerating &&
        this.connectionState === "connected"
      );
    },
    connectionLabel() {
      const labels = {
        connected: "已连接",
        connecting: "连接中",
        reconnecting: "重连中",
        disconnected: "未连接",
      };
      return labels[this.connectionState] || "未连接";
    },
    connectionBannerText() {
      if (this.connectionState === "connecting") {
        return "正在连接 AI 服务…";
      }
      if (this.connectionState === "reconnecting") {
        return `AI 服务连接中断，正在进行第 ${this.reconnectAttempt} 次重连…`;
      }
      return "AI 服务未连接，请检查 websocket_chat.py 是否启动在 5001 端口。";
    },
  },

  mounted() {
    this.loadConversations();
    if (!this.conversations.length) {
      this.createNewChat(true);
    }
    this.connectWebSocket();
    window.addEventListener("online", this.handleOnline);
    window.addEventListener("offline", this.handleOffline);
    if (this.currentMessages.length) {
      this.$nextTick(this.scrollToBottom);
    }
  },

  beforeDestroy() {
    this.manualClose = true;
    window.removeEventListener("online", this.handleOnline);
    window.removeEventListener("offline", this.handleOffline);
    this.clearResponseTimer();
    this.clearStopFallbackTimer();
    if (this.saveTimer) {
      clearTimeout(this.saveTimer);
      this.saveTimer = null;
      this.saveConversations();
    }
    if (this.scrollFrame) {
      cancelAnimationFrame(this.scrollFrame);
      this.scrollFrame = null;
    }
    if (this.socket) {
      this.socket.removeAllListeners();
      this.socket.disconnect();
      this.socket = null;
    }
  },

  methods: {
    // ==================== 连接管理 ====================
    connectWebSocket() {
      if (this.socket) {
        this.socket.removeAllListeners();
        this.socket.disconnect();
      }

      this.connectionState = "connecting";
      this.reconnectAttempt = 0;
      const socketUrl = `${window.location.protocol}//${window.location.hostname}:5001`;

      this.socket = io(`${socketUrl}/ws/chat`, {
        path: "/socket.io/",
        transports: ["websocket", "polling"],
        reconnection: true,
        reconnectionAttempts: 8,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        timeout: 10000,
        autoConnect: true,
      });

      this.socket.on("connect", () => {
        const wasReconnecting =
          this.connectionState === "reconnecting" ||
          this.connectionState === "disconnected";
        this.connectionState = "connected";
        this.reconnectAttempt = 0;
        this.lastError = "";
        if (wasReconnecting) {
          this.$message?.success("AI 服务已重新连接");
        }
      });

      this.socket.on("connected", (data) => {
        if (data && data.api_configured === false) {
          this.lastError = "服务端未配置 DeepSeek API Key，暂时无法对话。";
        }
      });

      this.socket.on("disconnect", (reason) => {
        this.connectionState = "disconnected";
        if (this.isGenerating) {
          this.failGeneration("连接已断开，本次回复未完成。");
        }
        if (reason === "io server disconnect" && !this.manualClose) {
          this.socket.connect();
        }
      });

      if (this.socket.io) {
        this.socket.io.on("reconnect_attempt", (attempt) => {
          this.connectionState = "reconnecting";
          this.reconnectAttempt = attempt;
        });

        this.socket.io.on("reconnect_failed", () => {
          this.connectionState = "disconnected";
          this.lastError = "多次重连失败，请确认 AI 服务已启动后点击“重连”。";
        });
      }

      this.socket.on("connect_error", (error) => {
        const wasConnecting = this.connectionState === "connecting";
        this.connectionState = "disconnected";
        if (wasConnecting) {
          this.lastError = `连接 AI 服务失败：${error.message || "网络异常"}`;
        }
      });

      this.socket.on("response_start", this.handleResponseStart);
      this.socket.on("response_chunk", this.handleResponseChunk);
      this.socket.on("response_end", this.handleResponseEnd);
      this.socket.on("response_stopped", this.handleResponseStopped);
      this.socket.on("stop_ack", this.handleStopAck);
      this.socket.on("response_error", this.handleResponseError);
    },

    reconnect() {
      if (!this.socket) {
        this.connectWebSocket();
        return;
      }
      if (this.socket.connected) {
        this.connectionState = "connected";
        return;
      }
      this.connectionState = "connecting";
      this.lastError = "";
      this.socket.connect();
    },

    handleOnline() {
      if (this.connectionState !== "connected") {
        this.reconnect();
      }
    },

    handleOffline() {
      this.connectionState = "disconnected";
      if (this.isGenerating) {
        this.failGeneration("网络已断开，本次回复未完成。");
      }
    },

    // ==================== 发送与流式接收 ====================
    sendMessage() {
      const content = this.inputMessage.trim();
      if (!content || this.isGenerating) return;
      if (content.length > MAX_INPUT_LENGTH) {
        this.lastError = `问题太长了，请控制在 ${MAX_INPUT_LENGTH} 字以内。`;
        return;
      }
      if (this.connectionState !== "connected") {
        this.lastError = "AI 服务未连接，请稍后重试。";
        return;
      }

      let conversation = this.currentConversation;
      if (!conversation) {
        conversation = this.createNewChat(true);
      }
      if (!conversation) return;

      const history = conversation.messages
        .filter((msg) => msg.role === "user" || msg.role === "assistant")
        .slice(-MAX_HISTORY_MESSAGES)
        .map((msg) => ({ role: msg.role, content: msg.content }))
        .filter((msg) => msg.content);

      this.activeConversationId = conversation.id;
      this.activeRequestId = null;
      this.lastError = "";
      this.isLoading = true;
      this.isStreaming = false;
      this.isStopping = false;

      this.addMessage("user", content, conversation);
      this.inputMessage = "";
      this.socket.emit(
        "message",
        JSON.stringify({
          content,
          history,
          conversation_id: conversation.id,
        })
      );

      this.setResponseTimer(30000, "等待 AI 响应超时，请重试。");
      this.scrollToBottom();
    },

    handleResponseStart(data) {
      this.activeRequestId = data.id;
      this.isLoading = false;
      this.isStreaming = true;
      this.isStopping = false;

      const conversation = this.findConversation(this.activeConversationId);
      if (!conversation) return;

      let message = this.findMessage(data.id, conversation);
      if (!message) {
        message = {
          role: "assistant",
          content: "",
          time: this.getCurrentTime(),
          requestId: data.id,
          safety: !!data.safety,
          streaming: true,
          stopped: false,
        };
        conversation.messages.push(message);
        conversation.updatedAt = new Date().toISOString();
      }

      this.setResponseTimer(60000, "AI 回复超时，已自动停止。");
      this.scheduleSave();
      this.throttleScroll();
    },

    handleResponseChunk(data) {
      if (!data || data.id !== this.activeRequestId) return;
      const conversation = this.findConversation(this.activeConversationId);
      if (!conversation) return;
      const message = this.findMessage(data.id, conversation);
      if (!message) return;

      message.content += data.delta || "";
      this.setResponseTimer(60000, "AI 回复超时，已自动停止。");
      this.scheduleSave();
      this.throttleScroll();
    },

    handleResponseEnd(data) {
      if (data.id && this.activeRequestId && data.id !== this.activeRequestId) {
        return;
      }
      const conversation = this.findConversation(this.activeConversationId);
      const message = this.findMessage(data.id, conversation);
      if (message) {
        message.content = data.content || message.content;
        message.streaming = false;
        message.stopped = false;
        message.safety = !!data.safety;
      }
      this.finishGeneration();
      this.saveConversations();
      this.scrollToBottom();
    },

    handleResponseStopped(data) {
      const conversation = this.findConversation(this.activeConversationId);
      const message = this.findMessage(data.id, conversation);
      if (message) {
        message.content = data.content || message.content || "（已停止生成）";
        message.streaming = false;
        message.stopped = true;
      }
      this.finishGeneration();
      this.saveConversations();
      this.$message?.info("已停止生成");
      this.scrollToBottom();
    },

    handleStopAck(data) {
      if (data && data.id === null && this.isStopping) {
        this.finishLocalStop();
      }
    },

    handleResponseError(data) {
      const message = {
        code: data.code || "api_error",
        text: data.message || "AI 服务异常，请稍后重试。",
      };
      const conversation = this.findConversation(this.activeConversationId);
      const current = this.findMessage(data.id, conversation);

      if (current && !current.content) {
        conversation.messages = conversation.messages.filter(
          (item) => item !== current
        );
      } else if (current) {
        current.streaming = false;
        current.stopped = true;
      }

      this.finishGeneration();
      this.lastError = message.text;
      this.saveConversations();
    },

    stopGeneration() {
      if (!this.isGenerating || this.isStopping) return;
      this.isStopping = true;
      this.clearResponseTimer();

      if (this.socket && this.socket.connected) {
        this.socket.emit("stop_generation", { id: this.activeRequestId });
      }

      this.clearStopFallbackTimer();
      this.stopFallbackTimer = setTimeout(() => {
        if (this.isGenerating) {
          this.finishLocalStop();
        }
      }, 4000);
    },

    finishLocalStop() {
      const conversation = this.findConversation(this.activeConversationId);
      const message = this.findMessage(this.activeRequestId, conversation);
      if (message) {
        message.streaming = false;
        message.stopped = true;
        if (!message.content) {
          message.content = "（已停止生成）";
        }
      }
      this.finishGeneration();
      this.saveConversations();
    },

    failGeneration(reason) {
      const conversation = this.findConversation(this.activeConversationId);
      const message = this.findMessage(this.activeRequestId, conversation);
      if (message) {
        message.streaming = false;
        if (!message.content) {
          message.content = "（连接中断，未收到完整回复）";
        }
      }
      this.finishGeneration();
      this.lastError = reason;
      this.saveConversations();
    },

    finishGeneration() {
      this.clearResponseTimer();
      this.clearStopFallbackTimer();
      this.isLoading = false;
      this.isStreaming = false;
      this.isStopping = false;
      this.activeRequestId = null;
    },

    setResponseTimer(ms, message) {
      this.clearResponseTimer();
      this.responseTimer = setTimeout(() => {
        if (!this.isGenerating) return;
        if (this.socket && this.socket.connected) {
          this.socket.emit("stop_generation", { id: this.activeRequestId });
        }
        this.failGeneration(message);
      }, ms);
    },

    clearResponseTimer() {
      if (this.responseTimer) {
        clearTimeout(this.responseTimer);
        this.responseTimer = null;
      }
    },

    clearStopFallbackTimer() {
      if (this.stopFallbackTimer) {
        clearTimeout(this.stopFallbackTimer);
        this.stopFallbackTimer = null;
      }
    },

    // ==================== 对话管理 ====================
    generateId() {
      return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    },

    createNewChat(silent = false) {
      if (this.isGenerating) {
        if (!silent) {
          this.$message?.warning("请先停止当前回复，再新建对话。");
        }
        return null;
      }

      // 已有一个空白对话时直接复用，避免侧边栏堆出一串“新对话”
      const emptyConversation = this.conversations.find(
        (conv) => conv.messages.length === 0
      );
      if (emptyConversation) {
        this.currentConversationId = emptyConversation.id;
        this.saveConversations();
        this.$nextTick(() => {
          if (this.$refs.chatInput) {
            this.$refs.chatInput.focus();
          }
        });
        return emptyConversation;
      }

      const newConversation = {
        id: this.generateId(),
        title: "新对话",
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      this.conversations.unshift(newConversation);
      this.conversations = this.conversations.slice(0, MAX_CONVERSATIONS);
      this.currentConversationId = newConversation.id;
      this.saveConversations();

      this.$nextTick(() => {
        if (this.$refs.chatInput) {
          this.$refs.chatInput.focus();
        }
        if (newConversation.messages.length) {
          this.scrollToBottom();
        }
      });
      return newConversation;
    },

    switchConversation(id) {
      if (id === this.currentConversationId) return;
      if (this.isGenerating) {
        this.$message?.warning("请先停止当前回复，再切换对话。");
        return;
      }
      this.currentConversationId = id;
      this.lastError = "";
      if (this.currentMessages.length) {
        this.$nextTick(this.scrollToBottom);
      }
    },

    deleteConversation(id) {
      if (this.isGenerating && id === this.activeConversationId) {
        this.$message?.warning("请先停止当前回复，再删除对话。");
        return;
      }
      if (!confirm("确定要删除这个对话吗？")) return;

      const index = this.conversations.findIndex((conv) => conv.id === id);
      if (index === -1) return;

      this.conversations.splice(index, 1);
      if (this.currentConversationId === id) {
        if (this.conversations.length > 0) {
          this.currentConversationId = this.conversations[0].id;
        } else {
          this.createNewChat(true);
        }
      }
      this.saveConversations();
    },

    startEdit(conversation) {
      this.editingId = conversation.id;
      this.editingTitle = conversation.title;
      this.$nextTick(() => {
        const input = Array.isArray(this.$refs.editInput)
          ? this.$refs.editInput[0]
          : this.$refs.editInput;
        if (input) {
          input.focus();
          input.select();
        }
      });
    },

    saveTitle(id) {
      const conversation = this.findConversation(id);
      if (conversation && this.editingTitle.trim()) {
        conversation.title = this.editingTitle.trim().slice(0, 40);
        conversation.updatedAt = new Date().toISOString();
        this.saveConversations();
      }
      this.cancelEdit();
    },

    cancelEdit() {
      this.editingId = null;
      this.editingTitle = "";
    },

    toggleSidebar() {
      this.sidebarVisible = !this.sidebarVisible;
    },

    addMessage(role, content, conversation = null, extra = {}) {
      const target = conversation || this.currentConversation;
      if (!target) return null;

      const message = {
        role,
        content,
        time: this.getCurrentTime(),
        ...extra,
      };
      target.messages.push(message);
      target.updatedAt = new Date().toISOString();

      if (
        role === "user" &&
        target.messages.filter((item) => item.role === "user").length === 1
      ) {
        const title = content.replace(/\s+/g, " ").slice(0, 30);
        target.title = title + (content.length > 30 ? "…" : "");
      }

      this.saveConversations();
      this.$nextTick(this.scrollToBottom);
      return message;
    },

    quickStart(prompt) {
      if (this.isGenerating) return;
      this.inputMessage = prompt;
      this.sendMessage();
    },

    handleEnterKey(event) {
      if (this.isComposing) return;
      if (!event.shiftKey) {
        this.sendMessage();
      } else {
        const start = event.target.selectionStart;
        const end = event.target.selectionEnd;
        const value = event.target.value;
        this.inputMessage =
          value.substring(0, start) + "\n" + value.substring(end);
        this.$nextTick(() => {
          event.target.selectionStart = event.target.selectionEnd = start + 1;
        });
      }
    },

    // ==================== 持久化与工具方法 ====================
    saveConversations() {
      try {
        const payload = this.conversations
          .slice(0, MAX_CONVERSATIONS)
          .map((conv) => ({
            id: conv.id,
            title: conv.title,
            createdAt: conv.createdAt,
            updatedAt: conv.updatedAt,
            messages: conv.messages
              .filter((msg) => msg.role === "user" || msg.role === "assistant")
              .slice(-MAX_MESSAGES_PER_CONVERSATION)
              .map((msg) => ({
                role: msg.role,
                content: msg.content,
                time: msg.time,
                safety: !!msg.safety,
                stopped: !!msg.stopped,
              })),
          }));

        localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
        localStorage.setItem(CURRENT_ID_KEY, this.currentConversationId || "");
      } catch (error) {
        console.error("保存对话失败:", error);
        this.lastError = "本地对话记录保存失败，可能是浏览器存储空间不足。";
      }
    },

    scheduleSave() {
      if (this.saveTimer) return;
      this.saveTimer = setTimeout(() => {
        this.saveTimer = null;
        this.saveConversations();
      }, 500);
    },

    loadConversations() {
      try {
        const saved = localStorage.getItem(STORAGE_KEY);
        const currentId = localStorage.getItem(CURRENT_ID_KEY);

        if (!saved) {
          this.conversations = [];
          return;
        }

        const parsed = JSON.parse(saved);
        if (!Array.isArray(parsed)) {
          throw new Error("对话数据格式不正确");
        }

        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - RETENTION_DAYS);

        this.conversations = parsed
          .filter((conv) => conv && conv.id && Array.isArray(conv.messages))
          .filter((conv) => {
            const updated = new Date(conv.updatedAt || conv.createdAt || 0);
            return !Number.isNaN(updated.getTime()) && updated >= cutoff;
          })
          .slice(0, MAX_CONVERSATIONS)
          .map((conv) => ({
            id: conv.id,
            title: conv.title || "新对话",
            createdAt: conv.createdAt || new Date().toISOString(),
            updatedAt: conv.updatedAt || conv.createdAt || new Date().toISOString(),
            messages: conv.messages
              .filter(
                (msg) =>
                  msg &&
                  (msg.role === "user" || msg.role === "assistant") &&
                  typeof msg.content === "string"
              )
              .slice(-MAX_MESSAGES_PER_CONVERSATION)
              .map((msg) => ({
                role: msg.role,
                content: msg.content,
                time: msg.time || "",
                safety: !!msg.safety,
                stopped: !!msg.stopped,
                streaming: false,
              })),
          }));

        if (this.conversations.length === 0) {
          return;
        }

        // 清理历史遗留的多个空白对话，只保留一个
        const nonEmpty = this.conversations.filter(
          (conv) => conv.messages.length > 0
        );
        this.conversations = nonEmpty.length
          ? nonEmpty
          : this.conversations.slice(0, 1);

        if (currentId && this.conversations.some((conv) => conv.id === currentId)) {
          this.currentConversationId = currentId;
        } else {
          this.currentConversationId = this.conversations[0].id;
        }
      } catch (error) {
        console.error("加载对话失败:", error);
        this.conversations = [];
        this.currentConversationId = null;
        this.lastError = "本地对话记录读取失败，已新建对话。";
      }
    },

    findConversation(id) {
      return this.conversations.find((conv) => conv.id === id) || null;
    },

    findMessage(requestId, conversation = null) {
      if (!requestId) return null;
      const target = conversation || this.currentConversation;
      if (!target) return null;
      return target.messages.find((msg) => msg.requestId === requestId) || null;
    },

    formatMessage(content) {
      try {
        marked.setOptions({
          breaks: true,
          gfm: true,
          headerIds: false,
          mangle: false,
        });

        // 先转义原始 HTML，避免模型/用户输入中的脚本被 v-html 执行
        const escaped = String(content || "")
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;");

        let html = marked.parse(escaped);
        html = html.replace(/<a /g, '<a target="_blank" rel="noopener noreferrer" ');
        html = html.replace(
          /href="(?!https?:|mailto:|#)[^"]*"/gi,
          'href="#"'
        );
        return html;
      } catch (error) {
        console.error("Markdown解析失败:", error);
        return String(content || "").replace(/\n/g, "<br>");
      }
    },

    getCurrentTime() {
      const now = new Date();
      return `${now.getHours().toString().padStart(2, "0")}:${now
        .getMinutes()
        .toString()
        .padStart(2, "0")}`;
    },

    formatDate(dateStr) {
      const date = new Date(dateStr);
      if (Number.isNaN(date.getTime())) return "";

      const now = new Date();
      const startOfToday = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate()
      );
      const startOfDate = new Date(
        date.getFullYear(),
        date.getMonth(),
        date.getDate()
      );
      const diffDays = Math.round(
        (startOfToday - startOfDate) / (1000 * 60 * 60 * 24)
      );

      if (diffDays === 0) {
        return `今天 ${date.getHours().toString().padStart(2, "0")}:${date
          .getMinutes()
          .toString()
          .padStart(2, "0")}`;
      }
      if (diffDays === 1) return "昨天";
      if (diffDays < 7) return `${diffDays}天前`;
      return `${date.getMonth() + 1}/${date.getDate()}`;
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container =
          this.$refs.chatContent || this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },

    throttleScroll() {
      if (this.scrollFrame) return;
      this.scrollFrame = requestAnimationFrame(() => {
        this.scrollFrame = null;
        this.scrollToBottom();
      });
    },

    handleImageError(event) {
      event.target.src =
        "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSI0MCIgY3k9IjQwIiByPSI0MCIgZmlsbD0iIzYzNjdmMSIvPjxwYXRoIGQ9Ik00MCAyNUM0NC45NzA2IDI1IDQ5IDI5LjAyOTQgNDkgMzRDNDkgMzguOTcwNiA0NC45NzA2IDQzIDQwIDQzQzM1LjAyOTQgNDMgMzEgMzguOTcwNiAzMSAzNEMzMSAyOS4wMjk0IDM1LjAyOTQgMjUgNDAgMjVaIiBmaWxsPSJ3aGl0ZSIvPjxwYXRoIGQ9Ik0yNSA1NUMyNSA0OS40NzcyIDI5LjQ3NzIgNDUgMzUgNDVINDVDNTAuNTIyOCA0NSA1NSA0OS40NzcyIDU1IDU1VjYwSDI1VjU1WiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=";
    },
  },
};
</script>

<style scoped>
@import "./AiChatModern.css";
</style>
