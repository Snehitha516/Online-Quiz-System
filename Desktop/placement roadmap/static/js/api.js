/**
 * API Wrapper: Handles all HTTP communication with the Flask backend.
 */
const API = {
    // Helper to perform fetch requests
    async request(url, options = {}) {
        options.headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };
        
        try {
            const response = await fetch(url, options);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Something went wrong');
            }
            return data;
        } catch (error) {
            console.error(`API Error [${url}]:`, error);
            throw error;
        }
    },

    // --- Authentication ---
    async me() {
        return this.request('/api/me');
    },

    async signup(name, email, password) {
        return this.request('/api/signup', {
            method: 'POST',
            body: JSON.stringify({ name, email, password })
        });
    },

    async login(email, password) {
        return this.request('/api/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },

    async logout() {
        return this.request('/api/logout', { method: 'POST' });
    },

    // --- Candidate Profile ---
    async getProfile() {
        return this.request('/api/profile');
    },

    async saveProfile(profileData) {
        return this.request('/api/profile', {
            method: 'POST',
            body: JSON.stringify(profileData)
        });
    },

    // --- Assessment ---
    async getAssessment() {
        return this.request('/api/assessment');
    },

    async saveAssessment(scores) {
        return this.request('/api/assessment', {
            method: 'POST',
            body: JSON.stringify(scores)
        });
    },

    // --- Roadmap ---
    async getRoadmap() {
        return this.request('/api/roadmap');
    },

    async generateRoadmap(duration) {
        return this.request('/api/roadmap', {
            method: 'POST',
            body: JSON.stringify({ duration })
        });
    },

    getRoadmapPDFUrl(userId) {
        return `/api/roadmap/download?user_id=${userId}`;
    },

    // --- Daily Tasks ---
    async getDailyTasks() {
        return this.request('/api/tasks');
    },

    async toggleTask(taskIndex, completed) {
        return this.request('/api/tasks', {
            method: 'PATCH',
            body: JSON.stringify({ task_index: taskIndex, completed })
        });
    },

    async getStreak() {
        return this.request('/api/streak');
    },

    // --- Notes & Revision Planner ---
    async getNotes() {
        return this.request('/api/notes');
    },

    async addNote(title, content, category, revisionInterval) {
        return this.request('/api/notes', {
            method: 'POST',
            body: JSON.stringify({ title, content, category, revision_interval: revisionInterval })
        });
    },

    async deleteNote(noteId) {
        return this.request(`/api/notes?note_id=${noteId}`, {
            method: 'DELETE'
        });
    },

    async toggleBookmarkNote(noteId, isBookmarked) {
        return this.request('/api/notes', {
            method: 'PATCH',
            body: JSON.stringify({ note_id: noteId, is_bookmarked: isBookmarked })
        });
    },

    // --- Achievements ---
    async getAchievements() {
        return this.request('/api/achievements');
    },

    // --- Resources ---
    async getResources() {
        return this.request('/api/resources');
    },

    // --- Company Prep ---
    async getCompanyPrep(companyName) {
        return this.request(`/api/company-prep/${companyName}`);
    },

    // --- Company Eligibility ---
    async checkEligibility(cgpa, backlogs, skills) {
        return this.request('/api/company-eligibility', {
            method: 'POST',
            body: JSON.stringify({ cgpa, backlogs, skills })
        });
    },

    // --- AI Resume Analyzer ---
    async analyzeResume(resumeText) {
        return this.request('/api/resume-analyzer', {
            method: 'POST',
            body: JSON.stringify({ resume_text: resumeText })
        });
    },

    // --- AI Chat Assistant ---
    async askChatAssistant(message) {
        return this.request('/api/chat-assistant', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
    },

    // --- AI Mock Interview ---
    async startMockInterview(topic) {
        return this.request('/api/mock-interview', {
            method: 'POST',
            body: JSON.stringify({ stage: 'start', topic })
        });
    },

    async respondMockInterview(topic, qIndex, responseText) {
        return this.request('/api/mock-interview', {
            method: 'POST',
            body: JSON.stringify({
                stage: 'respond',
                topic,
                q_index: qIndex,
                response: responseText
            })
        });
    }
};
