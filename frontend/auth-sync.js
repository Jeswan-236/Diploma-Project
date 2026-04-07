const SKILLSTALKER_API_BASE_URL = 'http://127.0.0.1:8000/api';
const SKILLSTALKER_TOKEN_KEY = 'ss_token';

function parseJsonStorage(value) {
    if (!value) return null;
    try {
        return JSON.parse(value);
    } catch (e) {
        return null;
    }
}

function getLocalProgressData() {
    return {
        aiStudySchedule: parseJsonStorage(localStorage.getItem('aiStudySchedule')) || null,
        streakDays: parseJsonStorage(localStorage.getItem('streakDays')) || null,
        calendarTopics: parseJsonStorage(localStorage.getItem('calendarTopics')) || null,
    };
}

function saveLocalProgressData(profileData) {
    if (!profileData || typeof profileData !== 'object') {
        return;
    }
    if (profileData.aiStudySchedule !== undefined && profileData.aiStudySchedule !== null) {
        localStorage.setItem('aiStudySchedule', JSON.stringify(profileData.aiStudySchedule));
    }
    if (profileData.streakDays !== undefined && profileData.streakDays !== null) {
        localStorage.setItem('streakDays', JSON.stringify(profileData.streakDays));
    }
    if (profileData.calendarTopics !== undefined && profileData.calendarTopics !== null) {
        localStorage.setItem('calendarTopics', JSON.stringify(profileData.calendarTopics));
    }
}

function redirectToPortal() {
    window.location.href = 'portal.html';
}

async function verifyAuthTokenOrRedirect() {
    const token = localStorage.getItem(SKILLSTALKER_TOKEN_KEY);
    if (!token) {
        redirectToPortal();
        return false;
    }

    try {
        const response = await fetch(`${SKILLSTALKER_API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Token validation failed');
        }

        await response.json();
        return true;
    } catch (error) {
        localStorage.removeItem(SKILLSTALKER_TOKEN_KEY);
        localStorage.removeItem('ss_active_user');
        redirectToPortal();
        return false;
    }
}

async function loadUserProgressFromServer() {
    const token = localStorage.getItem(SKILLSTALKER_TOKEN_KEY);
    if (!token) {
        return false;
    }

    try {
        const response = await fetch(`${SKILLSTALKER_API_BASE_URL}/user/progress`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            return false;
        }

        const result = await response.json();
        if (result?.profile_data) {
            saveLocalProgressData(result.profile_data);
        }
        return true;
    } catch (error) {
        console.warn('Could not load user progress:', error);
        return false;
    }
}

async function syncDataWithServer() {
    const token = localStorage.getItem(SKILLSTALKER_TOKEN_KEY);
    if (!token) {
        return false;
    }

    const payload = {
        profile_data: getLocalProgressData()
    };

    try {
        const response = await fetch(`${SKILLSTALKER_API_BASE_URL}/user/progress`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorBody = await response.text();
            console.warn('Failed to sync user progress:', response.status, errorBody);
            return false;
        }

        return true;
    } catch (error) {
        console.warn('Sync request failed:', error);
        return false;
    }
}

window.verifyAuthTokenOrRedirect = verifyAuthTokenOrRedirect;
window.syncDataWithServer = syncDataWithServer;
window.loadUserProgressFromServer = loadUserProgressFromServer;
window.initSkillStalkerSync = async function () {
    const valid = await verifyAuthTokenOrRedirect();
    if (!valid) {
        return;
    }
    await loadUserProgressFromServer();
};

(async function () {
    await initSkillStalkerSync();
})();
