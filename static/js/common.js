// 공통 JavaScript 함수들

// 알림 표시 함수
function showAlert(message, type = "info") {
  alert(message);
}

// 확인 대화상자
function showConfirm(message) {
  return confirm(message);
}

// 로딩 상태 표시
function showLoading(element) {
  if (element) {
    element.disabled = true;
    element.textContent = "처리중...";
  }
}

// 로딩 상태 해제
function hideLoading(element, originalText) {
  if (element) {
    element.disabled = false;
    // 원래 콘텐츠가 HTML(SVG 포함)일 수 있으므로 innerHTML로 복원
    element.innerHTML = originalText;
  }
}

// API 요청 공통 함수
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
}

// 페이지 이동 함수
function navigateTo(url) {
  window.location.href = url;
}

// 뒤로가기
function goBack() {
  window.history.back();
}
