// 채팅 관련 JavaScript 함수들

// 채팅방으로 이동
function goToChatRoom(roomId) {
  navigateTo(`/chat/${roomId}`);
}

// 채팅 목록으로 이동
function goToChatList() {
  navigateTo("/chat");
}

// 메시지 전송
async function sendMessage(roomId) {
  const messageInput = document.getElementById("messageInput");
  const message = messageInput.value.trim();

  if (!message) {
    return;
  }

  const sendBtn = document.getElementById("sendBtn");
  const originalText = sendBtn.innerHTML;

  try {
    showLoading(sendBtn);

    const response = await apiRequest(`/chat/${roomId}/send`, {
      method: "POST",
      body: JSON.stringify({
        message: message,
        message_type: "text",
      }),
    });

    if (response.success) {
      // 메시지 입력창 초기화
      messageInput.value = "";

      // 새 메시지를 채팅창에 추가
      addMessageToChat(response.message_data, true);

      // 채팅창 스크롤을 맨 아래로
      scrollToBottom();
    } else {
      showAlert(response.message || "메시지 전송에 실패했습니다.");
    }
  } catch (error) {
    showAlert("메시지 전송 중 오류가 발생했습니다.");
  } finally {
    hideLoading(sendBtn, originalText);
    messageInput.focus();
  }
}

// 채팅창에 메시지 추가
function addMessageToChat(messageData, isOwn = false) {
  const messagesContainer = document.getElementById("chatMessages");
  if (!messagesContainer) return;

  // 이미 동일 ID의 메시지가 존재하면 중복 추가 방지
  if (messageData && typeof messageData.id !== "undefined") {
    const exists = messagesContainer.querySelector(
      `[data-message-id="${messageData.id}"]`
    );
    if (exists) {
      return;
    }
  }

  const messageElement = createMessageElement(messageData, isOwn);
  messagesContainer.appendChild(messageElement);
}

// 메시지 요소 생성
function createMessageElement(messageData, isOwn = false) {
  const messageDiv = document.createElement("div");
  const isSystem = messageData.message_type === "system";
  messageDiv.className = `message ${isOwn ? "own" : ""} ${
    isSystem ? "system" : ""
  }`;

  // 중복 판별을 위한 메시지 ID 저장
  if (typeof messageData.id !== "undefined") {
    messageDiv.dataset.messageId = String(messageData.id);
  }

  const avatarDiv = document.createElement("div");
  avatarDiv.className = "message-avatar";
  const senderName = messageData.sender_name || "?";
  if (!isSystem) {
    avatarDiv.textContent = senderName.charAt(0);
  }

  const contentDiv = document.createElement("div");
  contentDiv.className = "message-content";

  const bubbleDiv = document.createElement("div");
  bubbleDiv.className = "message-bubble";
  bubbleDiv.textContent = messageData.message;

  const timeDiv = document.createElement("div");
  timeDiv.className = "message-time";
  timeDiv.textContent = formatMessageTime(messageData.created_at);

  contentDiv.appendChild(bubbleDiv);
  contentDiv.appendChild(timeDiv);

  if (!isSystem) {
    messageDiv.appendChild(avatarDiv);
  }
  messageDiv.appendChild(contentDiv);

  return messageDiv;
}

// 메시지 시간 포맷팅
function formatMessageTime(timeString) {
  const date = new Date(timeString);
  const now = new Date();

  // 오늘 날짜인지 확인
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString("ko-KR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } else {
    return date.toLocaleDateString("ko-KR", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }
}

// 채팅창 스크롤을 맨 아래로
function scrollToBottom() {
  const messagesContainer = document.getElementById("chatMessages");
  if (messagesContainer) {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
}

// Enter 키로 메시지 전송
function handleMessageKeyPress(event, roomId) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage(roomId);
  }
}

// 채팅방 나가기
async function leaveChatRoom(roomId) {
  if (!showConfirm("정말로 이 채팅방을 나가시겠습니까?")) {
    return;
  }

  try {
    const response = await apiRequest(`/chat/${roomId}/leave`, {
      method: "POST",
    });

    showAlert("채팅방을 나갔습니다.");
    goToChatList();
  } catch (error) {
    showAlert("채팅방 나가기 중 오류가 발생했습니다.");
  }
}

// 페이지 로드 시 초기화
document.addEventListener("DOMContentLoaded", function () {
  // 채팅창이 있으면 스크롤을 맨 아래로
  scrollToBottom();

  // 메시지 입력창에 포커스
  const messageInput = document.getElementById("messageInput");
  if (messageInput) {
    messageInput.focus();
  }
});

// 실시간 메시지 업데이트 (폴링 방식)
let messagePollingInterval;

function startMessagePolling(roomId) {
  // 기존 폴링 중지
  if (messagePollingInterval) {
    clearInterval(messagePollingInterval);
  }

  // 5초마다 새 메시지 확인
  messagePollingInterval = setInterval(async () => {
    try {
      const response = await apiRequest(
        `/chat/${roomId}/messages?page=1&per_page=10`
      );
      if (response.success) {
        updateChatMessages(response.messages);
      }
    } catch (error) {
      console.error("메시지 폴링 오류:", error);
    }
  }, 5000);
}

function stopMessagePolling() {
  if (messagePollingInterval) {
    clearInterval(messagePollingInterval);
    messagePollingInterval = null;
  }
}

// 채팅 메시지 업데이트
function updateChatMessages(newMessages) {
  const messagesContainer = document.getElementById("chatMessages");
  if (!messagesContainer) return;

  const existingMessages = messagesContainer.querySelectorAll(".message");
  const existingMessageIds = Array.from(existingMessages)
    .map((msg) => parseInt(msg.dataset.messageId))
    .filter((id) => !isNaN(id));

  newMessages.forEach((messageData) => {
    if (!existingMessageIds.includes(messageData.id)) {
      const isOwn = messageData.sender_id === getCurrentUserId();
      addMessageToChat(messageData, isOwn);
    }
  });

  scrollToBottom();
}

// 현재 사용자 ID 가져오기 (전역 변수나 데이터 속성에서)
function getCurrentUserId() {
  return window.currentUserId || parseInt(document.body.dataset.userId) || 0;
}
