// 공고 관련 JavaScript 함수들

// 공고 지원하기
async function applyJob(jobId) {
    if (!showConfirm('이 공고에 지원하시겠습니까?')) {
        return;
    }
    
    try {
        const response = await apiRequest(`/jobs/${jobId}/apply`, {
            method: 'POST'
        });
        
        if (response.success) {
            showAlert('지원이 완료되었습니다!');
        } else {
            showAlert(response.message || '지원 중 오류가 발생했습니다.');
        }
    } catch (error) {
        showAlert('지원 중 오류가 발생했습니다.');
    }
}

// 찜하기/찜 해제
async function toggleBookmark(jobId, button) {
    try {
        const response = await apiRequest(`/jobs/${jobId}/bookmark`, {
            method: 'POST'
        });
        
        if (response.success) {
            if (response.is_bookmarked) {
                button.classList.add('bookmarked');
                button.textContent = '♥';
            } else {
                button.classList.remove('bookmarked');
                button.textContent = '♡';
                
                // 찜 목록 페이지에서는 카드 제거
                if (window.location.pathname.includes('bookmark')) {
                    removeBookmarkCard(button);
                }
            }
        } else {
            showAlert(response.message || '오류가 발생했습니다.');
        }
    } catch (error) {
        showAlert('오류가 발생했습니다.');
    }
}

// 찜 목록에서 카드 제거
function removeBookmarkCard(button) {
    const jobCard = button.closest('.job-card');
    if (jobCard) {
        jobCard.style.transition = 'opacity 0.3s, transform 0.3s';
        jobCard.style.opacity = '0';
        jobCard.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            jobCard.remove();
            
            // 찜 목록이 비어있으면 빈 상태 표시
            const jobList = document.querySelector('.job-list');
            const remainingCards = jobList.querySelectorAll('.job-card');
            if (remainingCards.length === 0) {
                showEmptyBookmarkState(jobList);
            }
        }, 300);
    }
}

// 빈 찜 목록 상태 표시
function showEmptyBookmarkState(container) {
    container.innerHTML = `
        <div class="empty-state">
            <h3>찜한 공고가 없습니다</h3>
            <p>마음에 드는 공고를 찜해보세요!<br>나중에 쉽게 찾아볼 수 있습니다.</p>
            <a href="/jobs" class="btn-primary">공고 둘러보기</a>
        </div>
    `;
}

// 공고 상세 페이지로 이동
function goToJobDetail(jobId) {
    navigateTo(`/jobs/${jobId}`);
}

// 공고 수정 페이지로 이동
function editJob(jobId) {
    navigateTo(`/jobs/${jobId}/edit`);
}

// 공고 삭제
async function deleteJob(jobId) {
    if (!showConfirm('정말로 이 공고를 삭제하시겠습니까?')) {
        return;
    }
    
    try {
        const response = await apiRequest(`/jobs/${jobId}`, {
            method: 'DELETE'
        });
        
        if (response.success) {
            showAlert('공고가 삭제되었습니다.');
            navigateTo('/jobs');
        } else {
            showAlert(response.message || '삭제 중 오류가 발생했습니다.');
        }
    } catch (error) {
        showAlert('삭제 중 오류가 발생했습니다.');
    }
}