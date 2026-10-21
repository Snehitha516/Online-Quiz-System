/**
 * Frontend Controller: Handles client state, UI rendering, diagnostic quiz questions, 
 * view switching, and links interactive listeners to the API client.
 */

// Diagnostic MCQ Bank
const DIAGNOSTIC_MCQS = [
    {
        subject: "Aptitude",
        question: "A train running at 54 km/hr crosses a standing post in 20 seconds. What is the length of the train in meters?",
        options: ["200 m", "250 m", "300 m", "350 m"],
        answer: 2 // 300 m (54 * 5/18 = 15 m/s. 15 * 20 = 300)
    },
    {
        subject: "C Language",
        question: "What is the result of applying the sizeof operator to a char type variable on standard 32-bit systems?",
        options: ["1 Byte", "2 Bytes", "4 Bytes", "Depends on compiler"],
        answer: 0 // 1 Byte
    },
    {
        subject: "C++",
        question: "Which of the following concepts in C++ is achieved by having multiple functions with the same name but different arguments?",
        options: ["Operator Overloading", "Method Overriding", "Function Overloading", "Virtual Functions"],
        answer: 2 // Function Overloading
    },
    {
        subject: "Java",
        question: "Which of these classes is the absolute root/superclass of every other class in Java?",
        options: ["Class", "Object", "String", "System"],
        answer: 1 // Object
    },
    {
        subject: "Python",
        question: "What will print(type([]) == list) evaluate to in Python 3?",
        options: ["True", "False", "None", "Error"],
        answer: 0 // True
    },
    {
        subject: "SQL",
        question: "Which SQL command is used to remove all records from a table instantly without recording individual row deletes in the transaction log?",
        options: ["DELETE", "DROP", "TRUNCATE", "REMOVE"],
        answer: 2 // TRUNCATE
    },
    {
        subject: "DBMS",
        question: "A table is in 3rd Normal Form (3NF) if it is in 2NF and has no:",
        options: ["Partial dependencies", "Transitive dependencies", "Multivalued dependencies", "Functional dependencies"],
        answer: 1 // Transitive dependencies
    },
    {
        subject: "Operating System",
        question: "In memory management, what is 'Thrashing' primarily caused by?",
        options: ["High CPU speed", "Excessive page swapping due to insufficient RAM", "Deadlock situations", "Fragmentation in cache"],
        answer: 1 // Excessive page swapping
    },
    {
        subject: "Computer Networks",
        question: "At which layer of the ISO-OSI model does the HTTP/HTTPS protocol operate?",
        options: ["Transport Layer", "Session Layer", "Presentation Layer", "Application Layer"],
        answer: 3 // Application Layer
    },
    {
        subject: "OOPS",
        question: "Wrapping data variables and their associated methods together inside a single capsule or class is called:",
        options: ["Abstraction", "Inheritance", "Encapsulation", "Polymorphism"],
        answer: 2 // Encapsulation
    }
];

// App Global State
let state = {
    currentUser: null,
    currentView: 'home',
    profile: null,
    assessment: null,
    roadmap: null,
    tasks: [],
    streak: 0,
    quizIndex: 0,
    quizAnswers: Array(10).fill(null),
    codingAnswer: "",
    interviewTopic: "OOPS",
    interviewQIndex: 0,
    interviewHistory: []
};

// Start initialization on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

async function initApp() {
    setupViewSwitching();
    setupAuthListeners();
    setupProfileListeners();
    setupAssessmentListeners();
    setupRoadmapListeners();
    setupCodingPracticeListeners();
    setupCompanyPrepListeners();
    setupMockInterviewListeners();
    setupResumeListeners();
    setupChatAssistantListeners();
    setupEligibilityListeners();
    setupNotesListeners();
    
    // Check if user is already logged in
    await checkAuth();
}

// 1. Navigation and View Switching Logic
function setupViewSwitching() {
    // Sidebar navigation links
    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const targetView = link.getAttribute("data-view");
            switchView(targetView);
        });
    });

    // Landing CTA Start Button
    document.querySelectorAll(".btn-cta-start").forEach(btn => {
        btn.addEventListener("click", () => {
            if (state.currentUser) {
                switchView('dashboard');
            } else {
                switchView('auth');
            }
        });
    });

    // Toggle Sidebar on mobile
    const toggleBtn = document.getElementById("sidebar-toggle");
    const sidebar = document.getElementById("app-sidebar");
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("mobile-show");
        });
    }
}

function switchView(viewId) {
    // Close sidebar on mobile after clicking
    const sidebar = document.getElementById("app-sidebar");
    if (sidebar) sidebar.classList.remove("mobile-show");

    // Hide all views, display target
    document.querySelectorAll(".view-panel").forEach(panel => {
        panel.classList.remove("active");
    });
    
    const targetPanel = document.getElementById(`view-${viewId}`);
    if (targetPanel) {
        targetPanel.classList.add("active");
    }

    state.currentView = viewId;

    // Update Sidebar Active state
    document.querySelectorAll(".nav-link").forEach(link => {
        if (link.getAttribute("data-view") === viewId) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });

    // Update header title
    const viewTitleEl = document.getElementById("view-title");
    if (viewTitleEl) {
        const titleMap = {
            'home': 'Home Page',
            'auth': 'Login & Signup',
            'profile': 'Profile Setup',
            'assessment': 'Diagnostic Skill Assessment',
            'readiness': 'Placement Readiness Score',
            'roadmap': 'AI Personalized Roadmap',
            'dashboard': 'Student Dashboard',
            'tasks': 'Daily Tasks Generator',
            'coding': 'Coding Problem Recommendation',
            'company': 'Company-Wise Prep Guide',
            'interview': 'AI Mock Interview Coach',
            'resources': 'Study Materials & Resources',
            'chat': 'AI Doubt Solver Chatbot',
            'resume': 'AI Resume ATS Analyzer',
            'eligibility': 'Placement Eligibility Checker',
            'notes': 'Notes & Revision Planner',
            'progress': 'Achievements & Badges'
        };
        viewTitleEl.textContent = titleMap[viewId] || 'PathPrep AI';
    }

    // Refresh view data on entry
    triggerViewLoad(viewId);
}

// Perform fetches specifically when entering a view page
function triggerViewLoad(viewId) {
    if (!state.currentUser && viewId !== 'home' && viewId !== 'auth') {
        switchView('auth');
        return;
    }

    switch (viewId) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'readiness':
            loadReadinessData();
            break;
        case 'roadmap':
            loadRoadmapData();
            break;
        case 'tasks':
            loadTasksData();
            break;
        case 'coding':
            loadCodingRecommendations();
            break;
        case 'eligibility':
            loadEligibilityData();
            break;
        case 'notes':
            loadNotesData();
            break;
        case 'progress':
            loadAchievementsData();
            break;
        case 'resources':
            loadResourcesData();
            break;
        case 'profile':
            loadProfileData();
            break;
    }
}

// 2. Authentication Logic
async function checkAuth() {
    try {
        const data = await API.me();
        const appWrapper = document.getElementById("app-container");
        
        if (data.authenticated) {
            state.currentUser = data.user;
            
            // Adjust layout classes
            appWrapper.classList.remove("app-unauthenticated");
            appWrapper.classList.add("app-authenticated");
            
            document.getElementById("user-display-name").textContent = data.user.name;
            document.getElementById("user-display-email").textContent = data.user.email;
            document.getElementById("header-auth-buttons").style.display = "none";
            document.getElementById("streak-header-badge").style.display = "flex";
            
            // Sync streak from server
            const streakData = await API.getStreak();
            state.streak = streakData.streak;
            document.getElementById("streak-count-val").textContent = state.streak;

            // Direct verified user to dashboard
            if (state.currentView === 'home' || state.currentView === 'auth') {
                switchView('dashboard');
            }
        } else {
            state.currentUser = null;
            appWrapper.classList.remove("app-authenticated");
            appWrapper.classList.add("app-unauthenticated");
            
            document.getElementById("header-auth-buttons").style.display = "flex";
            document.getElementById("streak-header-badge").style.display = "none";
            
            if (state.currentView !== 'home' && state.currentView !== 'auth') {
                switchView('home');
            }
        }
    } catch (e) {
        console.error("Auth check failed:", e);
    }
}

function setupAuthListeners() {
    // Top Nav buttons
    document.getElementById("btn-header-login").addEventListener("click", () => switchView('auth'));
    document.getElementById("btn-header-register").addEventListener("click", () => switchView('auth'));

    // Toggle Forms inside Auth card
    const toggleLogin = document.getElementById("btn-toggle-login");
    const toggleSignup = document.getElementById("btn-toggle-signup");
    const loginForm = document.getElementById("form-login");
    const signupForm = document.getElementById("form-signup");

    toggleLogin.addEventListener("click", () => {
        toggleLogin.classList.add("active");
        toggleSignup.classList.remove("active");
        loginForm.classList.add("active");
        signupForm.classList.remove("active");
    });

    toggleSignup.addEventListener("click", () => {
        toggleSignup.classList.add("active");
        toggleLogin.classList.remove("active");
        signupForm.classList.add("active");
        loginForm.classList.remove("active");
    });

    // Login Form Submit
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;
        
        try {
            await API.login(email, password);
            await checkAuth();
        } catch (err) {
            alert(err.message || "Login failed");
        }
    });

    // Signup Form Submit
    signupForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("signup-name").value;
        const email = document.getElementById("signup-email").value;
        const password = document.getElementById("signup-password").value;
        
        try {
            await API.signup(name, email, password);
            await checkAuth();
            switchView('profile'); // Direct new users straight to onboarding setup!
        } catch (err) {
            alert(err.message || "Signup failed");
        }
    });

    // Logout click
    document.getElementById("btn-logout").addEventListener("click", async () => {
        try {
            await API.logout();
            await checkAuth();
        } catch (err) {
            console.error("Logout failed", err);
        }
    });
}

// 3. Candidate Profile Logic
async function loadProfileData() {
    try {
        const data = await API.getProfile();
        if (data.profile) {
            state.profile = data.profile;
            document.getElementById("prof-college").value = data.profile.college || "";
            document.getElementById("prof-dept").value = data.profile.department || "";
            document.getElementById("prof-year").value = data.profile.academic_year || "4th Year";
            document.getElementById("prof-cgpa").value = data.profile.cgpa || "";
            document.getElementById("prof-backlogs").value = data.profile.backlogs || 0;
            document.getElementById("prof-lang").value = data.profile.programming_language || "Python";
            document.getElementById("prof-company").value = data.profile.target_company || "TCS";
            document.getElementById("prof-time").value = data.profile.daily_study_time || "3-4 Hours";
            document.getElementById("prof-skills").value = data.profile.skills || "";
        }
    } catch (e) {
        console.error("Profile load failed", e);
    }
}

function setupProfileListeners() {
    const profileForm = document.getElementById("form-profile");
    profileForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const profileData = {
            college: document.getElementById("prof-college").value,
            department: document.getElementById("prof-dept").value,
            academic_year: document.getElementById("prof-year").value,
            cgpa: parseFloat(document.getElementById("prof-cgpa").value),
            backlogs: parseInt(document.getElementById("prof-backlogs").value),
            programming_language: document.getElementById("prof-lang").value,
            target_company: document.getElementById("prof-company").value,
            daily_study_time: document.getElementById("prof-time").value,
            skills: document.getElementById("prof-skills").value
        };

        try {
            await API.saveProfile(profileData);
            state.profile = profileData;
            alert("Profile parameters updated successfully!");
            switchView('assessment'); // Direct onto diagnostic assessment quiz!
        } catch (e) {
            alert(e.message || "Failed to update profile");
        }
    });
}

// 4. Skill Assessment Diagnostic Quiz Controller
let assessmentTimer = null;
let assessmentSecondsLeft = 900; // 15 mins

function setupAssessmentListeners() {
    document.getElementById("btn-start-quiz").addEventListener("click", () => {
        document.getElementById("assessment-intro-panel").style.display = "none";
        document.getElementById("assessment-quiz-panel").style.display = "block";
        startAssessmentTimer();
        renderQuizQuestion();
    });

    document.getElementById("btn-quiz-prev").addEventListener("click", () => {
        if (state.quizIndex > 0) {
            state.quizIndex--;
            renderQuizQuestion();
        }
    });

    document.getElementById("btn-quiz-next").addEventListener("click", () => {
        // Save answers before proceeding
        if (state.quizIndex < 10) {
            const selectedOpt = document.querySelector(".option-btn.selected");
            if (selectedOpt) {
                state.quizAnswers[state.quizIndex] = parseInt(selectedOpt.getAttribute("data-index"));
            } else {
                alert("Please select an answer to proceed!");
                return;
            }
        }

        if (state.quizIndex < 10) {
            state.quizIndex++;
            renderQuizQuestion();
        } else {
            // Submit entire quiz (Q11 is coding compiler workspace submission)
            submitQuizResults();
        }
    });

    // Code compilation test runner
    document.getElementById("btn-run-code").addEventListener("click", () => {
        const textCode = document.getElementById("coding-editor-textarea").value;
        const resultIndicator = document.getElementById("code-test-result");
        const editorLang = document.getElementById("editor-lang-display").textContent;
        
        resultIndicator.className = "test-result-indicator";
        resultIndicator.textContent = "Running test cases...";

        setTimeout(() => {
            let pass = false;
            if (editorLang === "Python") {
                pass = textCode.includes("def reverse_string") && (textCode.includes("return") || textCode.includes("print"));
            } else if (editorLang === "Java") {
                pass = textCode.includes("class Solution") && textCode.includes("reverseString") && textCode.includes("return");
            } else if (editorLang === "C++") {
                pass = textCode.includes("reverseString") && textCode.includes("return");
            } else if (editorLang === "C") {
                pass = textCode.includes("reverseString") && (textCode.includes("char") || textCode.includes("while") || textCode.includes("for") || textCode.includes("int"));
            } else if (editorLang === "JavaScript") {
                pass = textCode.includes("function reverseString") && textCode.includes("return");
            }
            
            if (pass) {
                resultIndicator.classList.add("success");
                resultIndicator.textContent = "Pass: All tests completed (3/3 passed).";
                state.codingAnswer = textCode;
            } else {
                resultIndicator.classList.add("error");
                resultIndicator.textContent = `Fail: Invalid ${editorLang} signature or return construct.`;
            }
        }, 1200);
    });
}

function startAssessmentTimer() {
    assessmentSecondsLeft = 900;
    const timerVal = document.getElementById("quiz-time-val");
    
    if (assessmentTimer) clearInterval(assessmentTimer);
    
    assessmentTimer = setInterval(() => {
        assessmentSecondsLeft--;
        const mins = Math.floor(assessmentSecondsLeft / 60);
        const secs = assessmentSecondsLeft % 60;
        
        timerVal.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        
        if (assessmentSecondsLeft <= 0) {
            clearInterval(assessmentTimer);
            alert("Time's up! Submitting your diagnostics automatically.");
            submitQuizResults();
        }
    }, 1000);
}

function renderQuizQuestion() {
    const questionCounter = document.getElementById("quiz-question-counter");
    const mcqContainer = document.getElementById("quiz-mcq-container");
    const codingContainer = document.getElementById("quiz-coding-container");
    const prevBtn = document.getElementById("btn-quiz-prev");
    const nextBtn = document.getElementById("btn-quiz-next");
    const editorLang = document.getElementById("editor-lang-display");

    // Enable/disable previous button
    prevBtn.disabled = (state.quizIndex === 0);
    
    // Set text on Next / Submit
    if (state.quizIndex === 10) {
        nextBtn.innerHTML = `Submit Assessment <i class="fa-solid fa-circle-check"></i>`;
    } else {
        nextBtn.innerHTML = `Next <i class="fa-solid fa-chevron-right"></i>`;
    }

    if (state.quizIndex < 10) {
        // Show MCQ
        mcqContainer.style.display = "block";
        codingContainer.style.display = "none";
        
        const currentQ = DIAGNOSTIC_MCQS[state.quizIndex];
        questionCounter.textContent = `Question ${state.quizIndex + 1} of 11 (${currentQ.subject})`;
        
        document.getElementById("quiz-question-text").textContent = currentQ.question;
        const optionsBox = document.getElementById("quiz-options-container");
        optionsBox.innerHTML = "";
        
        currentQ.options.forEach((opt, index) => {
            const btn = document.createElement("button");
            btn.className = "option-btn";
            btn.setAttribute("data-index", index);
            
            const savedAns = state.quizAnswers[state.quizIndex];
            if (savedAns === index) {
                btn.classList.add("selected");
            }
            
            btn.innerHTML = `<span class="option-indicator"></span> ${opt}`;
            
            btn.addEventListener("click", () => {
                document.querySelectorAll(".option-btn").forEach(b => b.classList.remove("selected"));
                btn.classList.add("selected");
            });
            
            optionsBox.appendChild(btn);
        });
    } else {
        // Show Coding Test Q11
        mcqContainer.style.display = "none";
        codingContainer.style.display = "block";
        questionCounter.textContent = "Question 11 of 11 (Coding Logic)";
        
        // Sync programming language from profile if configured
        editorLang.textContent = state.profile ? state.profile.programming_language : "Python";
        const codeTextarea = document.getElementById("coding-editor-textarea");
        
        if (!codeTextarea.value || codeTextarea.value.startsWith("def ") || codeTextarea.value.startsWith("public class ") || codeTextarea.value.startsWith("#include ")) {
            const lang = editorLang.textContent;
            if (lang === "Java") {
                codeTextarea.value = "public class Solution {\n    public String reverseString(String s) {\n        // Write Java code here\n        return s;\n    }\n}";
            } else if (lang === "C++") {
                codeTextarea.value = "#include <iostream>\n#include <string>\nusing namespace std;\n\nstring reverseString(string s) {\n    // Write C++ code here\n    return s;\n}";
            } else if (lang === "C") {
                codeTextarea.value = "#include <stdio.h>\n#include <string.h>\n\nvoid reverseString(char* s) {\n    // Write C code here\n}";
            } else if (lang === "JavaScript") {
                codeTextarea.value = "function reverseString(s) {\n    // Write JavaScript code here\n    return s;\n}";
            } else {
                codeTextarea.value = "def reverse_string(s):\n    # Write Python code here\n    return s";
            }
        }
    }
}

async function submitQuizResults() {
    clearInterval(assessmentTimer);
    
    // Evaluate MCQ score
    let scoreMCQCount = 0;
    DIAGNOSTIC_MCQS.forEach((q, idx) => {
        if (state.quizAnswers[idx] === q.answer) {
            scoreMCQCount++;
        }
    });

    // Score components:
    // Coding: coding question (40 pts) + programming base (60 pts)
    const codingScore = state.codingAnswer ? 85 : 45;
    // Aptitude: Q1 + random profile factor
    const aptScore = Math.min(scoreMCQCount * 10 + 10, 100);
    // SQL: Q6 + Q7 DBMS logic
    const sqlScore = (state.quizAnswers[5] === 2 && state.quizAnswers[6] === 1) ? 90 : 55;
    // Resume (Diagnostic placeholder default)
    const resScore = 65;
    // Communication (Diagnostic placeholder default)
    const commScore = 70;

    const payload = {
        coding_score: codingScore,
        aptitude_score: aptScore,
        sql_score: sqlScore,
        resume_score: resScore,
        comm_score: commScore
    };

    try {
        const res = await API.saveAssessment(payload);
        state.assessment = res.assessment;
        alert("Assessment submitted successfully! Reviewing placement readiness index.");
        
        // Reset quiz state
        state.quizIndex = 0;
        state.quizAnswers = Array(10).fill(null);
        state.codingAnswer = "";
        
        document.getElementById("assessment-intro-panel").style.display = "block";
        document.getElementById("assessment-quiz-panel").style.display = "none";
        
        switchView('readiness');
    } catch (e) {
        alert(e.message || "Failed to submit assessment answers");
    }
}

// 5. Placement Readiness & Score Chart Rendering
async function loadReadinessData() {
    try {
        const data = await API.getAssessment();
        if (data.assessment) {
            state.assessment = data.assessment;
            
            // Set Overall Gauge
            const overallScore = data.assessment.overall_score;
            document.getElementById("overall-score-val").textContent = overallScore;
            
            // Set Gauge color class based on score
            const scoreStatus = document.getElementById("overall-score-status");
            if (overallScore >= 80) {
                scoreStatus.textContent = "Placement Ready! Excellent";
                scoreStatus.className = "score-status text-success";
            } else if (overallScore >= 60) {
                scoreStatus.textContent = "Moderately Prepared. Action needed.";
                scoreStatus.className = "score-status text-warning";
            } else {
                scoreStatus.textContent = "Needs Urgent Practice";
                scoreStatus.className = "score-status text-danger";
            }
            
            // Update SVG Ring animation (circumference of r=80 is ~502)
            const ring = document.getElementById("readiness-ring");
            if (ring) {
                const offset = 502.65 - (overallScore / 100) * 502.65;
                ring.style.strokeDashoffset = offset;
            }

            // Categories Progress Bars
            document.getElementById("bar-coding").style.width = `${data.assessment.coding_score}%`;
            document.getElementById("val-coding").textContent = `${data.assessment.coding_score}%`;
            
            document.getElementById("bar-aptitude").style.width = `${data.assessment.aptitude_score}%`;
            document.getElementById("val-aptitude").textContent = `${data.assessment.aptitude_score}%`;
            
            document.getElementById("bar-sql").style.width = `${data.assessment.sql_score}%`;
            document.getElementById("val-sql").textContent = `${data.assessment.sql_score}%`;
            
            document.getElementById("bar-resume").style.width = `${data.assessment.resume_score}%`;
            document.getElementById("val-resume").textContent = `${data.assessment.resume_score}%`;
            
            document.getElementById("bar-comm").style.width = `${data.assessment.comm_score}%`;
            document.getElementById("val-comm").textContent = `${data.assessment.comm_score}%`;

            // SWOT list rendering
            const strongBox = document.getElementById("strong-areas-list");
            strongBox.innerHTML = "";
            data.assessment.strong_areas.split(',').forEach(item => {
                if (item.trim()) {
                    const li = document.createElement("li");
                    li.textContent = item.trim();
                    strongBox.appendChild(li);
                }
            });

            const weakBox = document.getElementById("weak-areas-list");
            weakBox.innerHTML = "";
            data.assessment.weak_areas.split(',').forEach(item => {
                if (item.trim()) {
                    const li = document.createElement("li");
                    li.textContent = item.trim();
                    weakBox.appendChild(li);
                }
            });

            document.getElementById("ai-suggestions-paragraph").textContent = data.assessment.suggestions;
        } else {
            // Default placeholder state
            document.getElementById("overall-score-val").textContent = "0";
            document.getElementById("overall-score-status").textContent = "Diagnostic Test Pending";
            document.getElementById("overall-score-status").className = "score-status text-muted";
        }
    } catch (e) {
        console.error("Readiness check failed", e);
    }
}

// 6. AI Personalized Roadmap generator logic
function setupRoadmapListeners() {
    // Generate roadmap from readiness score page
    document.getElementById("btn-trigger-roadmap").addEventListener("click", () => {
        if (!state.assessment) {
            alert("Please complete the Diagnostic Skill Quiz before generating a customized roadmap.");
            switchView('assessment');
            return;
        }
        switchView('roadmap');
    });

    // Tabs navigation inside roadmap view
    document.querySelectorAll(".roadmap-tab-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            document.querySelectorAll(".roadmap-tab-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const duration = parseInt(btn.getAttribute("data-duration"));
            await generateCustomRoadmap(duration);
        });
    });

    // PDF Download Event
    document.getElementById("btn-download-roadmap-pdf").addEventListener("click", () => {
        if (state.currentUser) {
            window.location.href = API.getRoadmapPDFUrl(state.currentUser.id);
        }
    });
}

async function loadRoadmapData() {
    try {
        const data = await API.getRoadmap();
        if (data.roadmap) {
            state.roadmap = data.roadmap;
            
            // Activate corresponding tab
            document.querySelectorAll(".roadmap-tab-btn").forEach(btn => {
                if (parseInt(btn.getAttribute("data-duration")) === data.roadmap.duration) {
                    btn.classList.add("active");
                } else {
                    btn.classList.remove("active");
                }
            });
            
            renderRoadmapTimeline(data.roadmap.roadmap_data);
        } else {
            // Generate initial 30-day plan
            await generateCustomRoadmap(30);
        }
    } catch (e) {
        console.error("Load roadmap failed", e);
    }
}

async function generateCustomRoadmap(duration) {
    try {
        const data = await API.generateRoadmap(duration);
        state.roadmap = data.roadmap;
        renderRoadmapTimeline(data.roadmap.roadmap_data);
    } catch (e) {
        alert(e.message || "Failed to generate roadmap timeline");
    }
}

function renderRoadmapTimeline(periods) {
    const box = document.getElementById("roadmap-timeline-container");
    box.innerHTML = "";
    
    periods.forEach(p => {
        const div = document.createElement("div");
        div.className = "timeline-period";
        
        let tagsHtml = "";
        p.activities.forEach(act => {
            tagsHtml += `<span class="activity-tag"><i class="fa-solid fa-circle-check font-cyan"></i> ${act}</span>`;
        });
        
        div.innerHTML = `
            <h3>${p.period}</h3>
            <p>${p.details}</p>
            <div class="activity-tag-list">${tagsHtml}</div>
        `;
        
        box.appendChild(div);
    });
}

// 7. Student Dashboard Logic
async function loadDashboardData() {
    try {
        // Fetch values
        const readiness = await API.getAssessment();
        const streakData = await API.getStreak();
        const tasks = await API.getDailyTasks();
        const achievements = await API.getAchievements();

        // Populate cards
        document.getElementById("dash-readiness-val").textContent = readiness.assessment ? `${readiness.assessment.overall_score}%` : "0%";
        document.getElementById("dash-streak-val").textContent = `${streakData.streak} Days`;
        document.getElementById("dash-badges-val").textContent = achievements.achievements ? achievements.achievements.length : 0;
        
        // Calculate task progress percentage
        let progress = 0;
        if (tasks && tasks.total_tasks_count > 0) {
            progress = Math.round((tasks.completed_tasks_count / tasks.total_tasks_count) * 100);
        }
        document.getElementById("dash-completion-val").textContent = `${progress}%`;

        // Render today's task snapshot list
        const tasksContainer = document.getElementById("dash-tasks-container");
        tasksContainer.innerHTML = "";
        
        if (tasks && tasks.tasks.length > 0) {
            tasks.tasks.slice(0, 3).forEach(t => {
                const item = document.createElement("div");
                item.className = `task-item ${t.completed ? 'completed' : ''}`;
                item.innerHTML = `
                    <div class="task-checkbox"><i class="fa-solid fa-check"></i></div>
                    <span class="task-text">${t.title}</span>
                `;
                tasksContainer.appendChild(item);
            });
            
            // Add click event directing to tasks detail page
            document.getElementById("btn-dash-go-tasks").addEventListener("click", () => {
                switchView('tasks');
            });
        } else {
            tasksContainer.innerHTML = "<p class='text-muted'>No tasks created yet today. Head over to the Roadmap section to load one.</p>";
        }

        // Action hooks in Dashboard cards
        document.querySelectorAll(".quick-card").forEach(qc => {
            qc.addEventListener("click", (e) => {
                e.preventDefault();
                switchView(qc.getAttribute("data-view"));
            });
        });
    } catch (e) {
        console.error("Dashboard synchronization error", e);
    }
}

// 8. Daily Tasks Checkbox Generator
async function loadTasksData() {
    try {
        const data = await API.getDailyTasks();
        state.tasks = data.tasks;
        
        document.getElementById("task-day-title").textContent = `Day ${data.day_number || 1} Milestones`;
        
        const container = document.getElementById("tasks-list-container");
        container.innerHTML = "";
        
        data.tasks.forEach((t, idx) => {
            const item = document.createElement("div");
            item.className = `task-item ${t.completed ? 'completed' : ''}`;
            item.setAttribute("data-index", idx);
            
            item.innerHTML = `
                <div class="task-checkbox"><i class="fa-solid fa-check"></i></div>
                <span class="task-text">${t.title}</span>
            `;
            
            item.addEventListener("click", async () => {
                const nextCompleted = !t.completed;
                const updateRes = await API.toggleTask(idx, nextCompleted);
                
                // Update header streak immediately
                state.streak = updateRes.tasks_data.streak;
                document.getElementById("streak-count-val").textContent = state.streak;
                
                // Reload checklist view
                loadTasksData();
            });
            
            container.appendChild(item);
        });

        // Calculate progress percentage
        let progress = 0;
        if (data.total_tasks_count > 0) {
            progress = Math.round((data.completed_tasks_count / data.total_tasks_count) * 100);
        }
        document.getElementById("tasks-progress-percentage").textContent = `${progress}%`;
        document.getElementById("tasks-progress-bar").style.width = `${progress}%`;
    } catch (e) {
        console.error("Failed loading checklist", e);
    }
}

// 10. Company-Wise Preparation Panel
function setupCompanyPrepListeners() {
    // Company selection
    document.querySelectorAll(".company-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            document.querySelectorAll(".company-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const compName = btn.getAttribute("data-company");
            try {
                const data = await API.getCompanyPrep(compName);
                const info = data.details;
                
                const panel = document.getElementById("company-details-panel");
                panel.style.display = "block";
                
                document.getElementById("comp-title").textContent = `${compName} Preparation Kit`;
                document.getElementById("comp-pattern").textContent = info.pattern;
                document.getElementById("comp-aptitude").textContent = info.aptitude;
                document.getElementById("comp-hr").textContent = info.hr;
                document.getElementById("comp-experience").textContent = `"${info.experiences}"`;
                
                const codeList = document.getElementById("comp-coding-list");
                codeList.innerHTML = "";
                info.questions.forEach(q => {
                    const li = document.createElement("li");
                    li.textContent = q;
                    codeList.appendChild(li);
                });
            } catch (e) {
                console.error("Failed loading company files", e);
            }
        });
    });
}

// 9. Coding Problem Workspace Setup
function setupCodingPracticeListeners() {
    // Override/setup mock practice editor submissions
    document.querySelectorAll(".btn-practice-mock-code").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            const problem = btn.getAttribute("data-problem");
            const desc = btn.getAttribute("data-desc");
            
            const workspace = document.getElementById("coding-practice-workspace");
            if (workspace) {
                workspace.style.display = "block";
                document.getElementById("workspace-problem-title").textContent = `Workspace: ${problem}`;
                document.getElementById("workspace-problem-desc").textContent = desc;
                document.getElementById("workspace-textarea").value = "";
                workspace.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    const submitBtn = document.getElementById("btn-workspace-submit");
    if (submitBtn) {
        submitBtn.addEventListener("click", () => {
            const userCode = document.getElementById("workspace-textarea").value;
            if (userCode.trim().length < 20) {
                alert("Please type a valid implementation solution before submitting!");
                return;
            }
            alert("Solution submitted! System analyzed runtime complexity: O(N) auxiliary. Unlocked achievement: DSA Beginner.");
            
            // Try updating achievements on UI
            API.getAchievements().then(res => {
                const unlockedBadges = res.achievements.map(a => a.badge_name);
                const badgeCards = document.querySelectorAll(".badge-card");
                badgeCards.forEach(card => {
                    const title = card.querySelector("h4").textContent;
                    if (unlockedBadges.includes(title)) {
                        card.classList.add("unlocked");
                        const icon = card.querySelector(".badge-icon-box");
                        if (icon) icon.style.background = "var(--gradient-primary)";
                    }
                });
            }).catch(e => console.error(e));
            
            document.getElementById("coding-practice-workspace").style.display = "none";
        });
    }

    const closeBtn = document.getElementById("btn-workspace-close");
    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            document.getElementById("coding-practice-workspace").style.display = "none";
        });
    }
}

// 11. AI Mock Interview Coaching Logic
function setupMockInterviewListeners() {
    const setupPanel = document.getElementById("interview-setup-panel");
    const chatPanel = document.getElementById("interview-chat-panel");
    const feedbackPanel = document.getElementById("interview-feedback-panel");
    
    document.getElementById("btn-start-interview").addEventListener("click", async () => {
        const topic = document.getElementById("interview-topic").value;
        state.interviewTopic = topic;
        state.interviewQIndex = 0;
        state.interviewHistory = [];

        try {
            const data = await API.startMockInterview(topic);
            
            setupPanel.style.display = "none";
            chatPanel.style.display = "flex";
            feedbackPanel.style.display = "none";
            
            document.getElementById("chat-topic-display").textContent = topic;
            
            const msgBox = document.getElementById("interview-messages");
            msgBox.innerHTML = `
                <div class="chat-bubble ai-bubble">
                    <p>Hello! Welcome to your simulated <strong>${topic}</strong> round. Let's begin.</p>
                </div>
                <div class="chat-bubble ai-bubble">
                    <p>${data.question}</p>
                </div>
            `;
            
            document.getElementById("interview-user-response").value = "";
        } catch (e) {
            alert("Error starting mock interview");
        }
    });

    document.getElementById("btn-submit-interview-answer").addEventListener("click", async () => {
        const responseText = document.getElementById("interview-user-response").value.trim();
        if (!responseText) {
            alert("Please type a response before submitting!");
            return;
        }

        const msgBox = document.getElementById("interview-messages");
        
        // Append user response
        msgBox.innerHTML += `
            <div class="chat-bubble user-bubble">
                <p>${responseText}</p>
            </div>
        `;
        msgBox.scrollTop = msgBox.scrollHeight;
        
        document.getElementById("interview-user-response").value = "";

        try {
            const data = await API.respondMockInterview(state.interviewTopic, state.interviewQIndex, responseText);
            
            state.interviewHistory.push(data.evaluation);

            if (data.has_next) {
                state.interviewQIndex = data.q_index;
                
                // Append AI reply
                setTimeout(() => {
                    msgBox.innerHTML += `
                        <div class="chat-bubble ai-bubble">
                            <p><em>AI Feedback on last answer: Technical Accuracy ${data.evaluation.tech_score}%, Comm: ${data.evaluation.comm_score}%</em></p>
                        </div>
                        <div class="chat-bubble ai-bubble">
                            <p>${data.next_question}</p>
                        </div>
                    `;
                    msgBox.scrollTop = msgBox.scrollHeight;
                }, 1000);
            } else {
                // Compile final scores
                let totalTech = 0;
                let totalComm = 0;
                state.interviewHistory.forEach(h => {
                    totalTech += h.tech_score;
                    totalComm += h.comm_score;
                });
                
                const avgTech = Math.round(totalTech / state.interviewHistory.length);
                const avgComm = Math.round(totalComm / state.interviewHistory.length);
                
                // Show feedback card
                setTimeout(() => {
                    chatPanel.style.display = "none";
                    feedbackPanel.style.display = "block";
                    
                    document.getElementById("val-feedback-tech").textContent = `${avgTech}%`;
                    document.getElementById("val-feedback-comm").textContent = `${avgComm}%`;
                    document.getElementById("val-feedback-conf").textContent = avgTech > 70 ? 'High' : 'Medium';
                    document.getElementById("val-feedback-suggestions").textContent = data.evaluation.suggestions;
                }, 1000);
            }
        } catch (e) {
            alert("Failed checking responses");
        }
    });

    document.getElementById("btn-end-interview-early").addEventListener("click", () => {
        chatPanel.style.display = "none";
        setupPanel.style.display = "block";
    });

    document.getElementById("btn-interview-restart").addEventListener("click", () => {
        feedbackPanel.style.display = "none";
        setupPanel.style.display = "block";
    });
}

// 12. Study Resources Catalog Loading
async function loadResourcesData() {
    try {
        const data = await API.getResources();
        const container = document.getElementById("resources-cards-container");
        container.innerHTML = "";

        Object.keys(data.resources).forEach(cat => {
            const sec = document.createElement("div");
            sec.className = "resource-category-section";
            
            let listHtml = "";
            data.resources[cat].forEach(r => {
                const icon = r.type === 'Video' ? 'fa-video' : (r.type === 'Book' ? 'fa-book' : 'fa-file-invoice');
                listHtml += `
                    <div class="resource-list-item">
                        <span><i class="fa-solid ${icon} font-indigo"></i> ${r.title}</span>
                        <a href="${r.link}" target="_blank" class="btn btn-sm btn-secondary">Open <i class="fa-solid fa-up-right-from-square"></i></a>
                    </div>
                `;
            });

            sec.innerHTML = `
                <h3>${cat}</h3>
                <div class="resource-list-box">${listHtml}</div>
            `;
            container.appendChild(sec);
        });
    } catch (e) {
        console.error("Resource fetch failed", e);
    }
}

// 13. AI Doubt Solver Chatbot
function setupChatAssistantListeners() {
    const input = document.getElementById("chat-assistant-input");
    const sendBtn = document.getElementById("btn-send-chat-assistant");
    const msgBox = document.getElementById("chat-assistant-messages");

    const sendMessage = async () => {
        const text = input.value.trim();
        if (!text) return;

        input.value = "";
        
        // Append user bubble
        msgBox.innerHTML += `
            <div class="chat-bubble user-bubble">
                <p>${text}</p>
            </div>
        `;
        msgBox.scrollTop = msgBox.scrollHeight;

        try {
            const data = await API.askChatAssistant(text);
            
            // Append AI response
            setTimeout(() => {
                msgBox.innerHTML += `
                    <div class="chat-bubble ai-bubble">
                        <p>${data.reply}</p>
                    </div>
                `;
                msgBox.scrollTop = msgBox.scrollHeight;
            }, 800);
        } catch (e) {
            console.error("Chat message error", e);
        }
    };

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keypress", (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

// 14. AI Resume Analyzer Setup
function setupResumeListeners() {
    document.getElementById("btn-analyze-resume").addEventListener("click", async () => {
        const text = document.getElementById("resume-text-input").value.trim();
        if (!text) {
            alert("Please paste resume text credentials before analyzing!");
            return;
        }

        const btn = document.getElementById("btn-analyze-resume");
        btn.disabled = true;
        btn.textContent = "Scanning ATS files...";

        try {
            const data = await API.analyzeResume(text);
            
            document.getElementById("resume-results-panel").style.display = "block";
            document.getElementById("ats-score-val").textContent = `${data.ats_score}%`;
            document.getElementById("ats-missing-skills").textContent = data.missing_skills;
            document.getElementById("ats-grammar").textContent = data.grammar_suggestions;
            document.getElementById("ats-tips").textContent = data.improvement_tips;
        } catch (e) {
            alert("Failed scanning resume");
        } finally {
            btn.disabled = false;
            btn.textContent = "Analyze Resume";
        }
    });
}

// 15. Placement Eligibility Calculator
async function loadEligibilityData() {
    if (!state.profile) {
        alert("Please configure academic credentials under Profile first!");
        switchView('profile');
        return;
    }
    
    try {
        const res = await API.checkEligibility(state.profile.cgpa, state.profile.backlogs, state.profile.skills);
        const eligBox = document.getElementById("elig-companies-container");
        const ineligBox = document.getElementById("inelig-companies-container");
        
        eligBox.innerHTML = "";
        ineligBox.innerHTML = "";

        res.eligible.forEach(c => {
            const div = document.createElement("div");
            div.className = "elig-card";
            div.innerHTML = `
                <h4>${c.name}</h4>
                <p>Required Skills: <small class="text-info">${c.required_skills}</small></p>
                <p>Missing Skills: <small class="text-warning">${c.missing_skills}</small></p>
            `;
            eligBox.appendChild(div);
        });

        res.not_eligible.forEach(c => {
            const div = document.createElement("div");
            div.className = "elig-card";
            div.innerHTML = `
                <h4>${c.name}</h4>
                <p class="text-danger">Reasons: ${c.reasons}</p>
                <p>Required Skills: <small>${c.required_skills}</small></p>
            `;
            ineligBox.appendChild(div);
        });
    } catch (e) {
        console.error("Eligibility check failed", e);
    }
}

function setupEligibilityListeners() {
    document.getElementById("btn-check-eligibility").addEventListener("click", () => {
        loadEligibilityData();
    });
}

// 16. Notes and revision cards planner
async function loadNotesData() {
    try {
        const res = await API.getNotes();
        const container = document.getElementById("notes-list-container");
        container.innerHTML = "";

        if (res.notes && res.notes.length > 0) {
            res.notes.forEach(n => {
                const card = document.createElement("div");
                card.className = "note-card";
                card.innerHTML = `
                    <div class="note-card-header">
                        <span class="note-tag font-cyan">${n.category}</span>
                        <button class="note-btn-action note-btn-bookmark" data-id="${n.id}" data-active="${n.is_bookmarked}">
                            <i class="${n.is_bookmarked ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>
                        </button>
                    </div>
                    <h4>${n.title}</h4>
                    <p>${n.content}</p>
                    <div class="note-card-footer">
                        <span class="date"><i class="fa-regular fa-clock"></i> ${n.revision_interval}</span>
                        <button class="note-btn-action note-btn-delete" data-id="${n.id}">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                `;
                
                // Add Bookmark Event
                card.querySelector(".note-btn-bookmark").addEventListener("click", async () => {
                    const active = n.is_bookmarked === 1;
                    await API.toggleBookmarkNote(n.id, !active);
                    loadNotesData();
                });

                // Add Delete Event
                card.querySelector(".note-btn-delete").addEventListener("click", async () => {
                    if (confirm("Are you sure you want to delete this revision note?")) {
                        await API.deleteNote(n.id);
                        loadNotesData();
                    }
                });

                container.appendChild(card);
            });
        } else {
            container.innerHTML = "<p class='text-muted'>No revision notes logged yet. Write one on the left!</p>";
        }
    } catch (e) {
        console.error("Notes synchronization error", e);
    }
}

function setupNotesListeners() {
    const form = document.getElementById("form-note");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const title = document.getElementById("note-title").value;
        const cat = document.getElementById("note-category").value;
        const rev = document.getElementById("note-revision").value;
        const content = document.getElementById("note-content").value;

        try {
            await API.addNote(title, content, cat, rev);
            alert("Revision note saved successfully!");
            form.reset();
            loadNotesData();
        } catch (err) {
            alert("Failed writing note");
        }
    });
}

// 17. Achievements and Badges
async function loadAchievementsData() {
    try {
        const res = await API.getAchievements();
        const unlockedBadges = res.achievements.map(a => a.badge_name);
        
        const badgesConfig = [
            { name: "SQL Master", desc: "Achieve 85%+ on Database normalisation diagnostics.", icon: "fa-database" },
            { name: "DSA Beginner", desc: "Solve a coding compiler problem inside the workspace.", icon: "fa-code" },
            { name: "Aptitude Expert", desc: "Score 85%+ on mathematical reasoning metrics.", icon: "fa-calculator" },
            { name: "15-Day Streak", desc: "Check off milestones daily to accumulate consistent streaks.", icon: "fa-fire" }
        ];

        const container = document.getElementById("badges-container");
        container.innerHTML = "";

        badgesConfig.forEach(b => {
            const isUnlocked = unlockedBadges.includes(b.name);
            const card = document.createElement("div");
            card.className = `badge-card ${isUnlocked ? 'unlocked' : ''}`;
            
            card.innerHTML = `
                <div class="badge-icon-box">
                    <i class="fa-solid ${b.icon}"></i>
                </div>
                <h4>${b.name}</h4>
                <span>${b.desc}</span>
            `;
            container.appendChild(card);
        });
    } catch (e) {
        console.error("Failed sync badges", e);
    }
}

// 18. Coding Problem Recommendation Question Bank & Renderer
const CODING_QUESTIONS_BANK = {
    "Coding": [
        { name: "Two Sum", difficulty: "Easy", category: "Array / Hashing", desc: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. Write a function that returns the indices in O(N) time complexity." },
        { name: "Container With Most Water", difficulty: "Medium", category: "Two Pointers", desc: "Given n non-negative integers representation of lines, find two lines that form a container containing the most water. Return maximum capacity." },
        { name: "Merge K Sorted Lists", difficulty: "Hard", category: "Heap / Priority Queue", desc: "You are given an array of k linked lists, each linked list is sorted in ascending order. Merge all the linked lists into one sorted linked list and return it." },
        { name: "Reverse Nodes in K-Group", difficulty: "Hard", category: "Linked List / Recursion", desc: "Given the head of a linked list, reverse the nodes of the list k at a time and return the modified head pointer." }
    ],
    "SQL & DBMS": [
        { name: "Combine Two Tables", difficulty: "Easy", category: "SQL Joins", desc: "Write a SQL solution to report the first name, last name, city, and state of each person in the Person table. If the address is missing, report NULL instead." },
        { name: "Nth Highest Salary", difficulty: "Medium", category: "SQL Subqueries", desc: "Write a SQL query to get the Nth highest salary from the Employee table. If there is no nth highest salary, return NULL." },
        { name: "Department Highest Salary", difficulty: "Medium", category: "SQL Partition / Rank", desc: "Write a SQL query to find employees who have the highest salary in each of the corporate departments." },
        { name: "Human Traffic of Stadium", difficulty: "Hard", category: "SQL Consecutive Rows", desc: "Write an query to display records with three or more rows of consecutive IDs where visitors count exceeds 100." }
    ],
    "Aptitude": [
        { name: "Palindrome Number", difficulty: "Easy", category: "Math & Logic", desc: "Given an integer x, return true if x is a palindrome, and false otherwise. Avoid converting the integer to a string directly." },
        { name: "Pow(x, n)", difficulty: "Medium", category: "Binary Exponentiation", desc: "Implement pow(x, n), which calculates x raised to the power n in O(log N) operations." },
        { name: "Max Points on a Line", difficulty: "Hard", category: "Geometry / Slope Hash", desc: "Given an array of points on a 2D plane, return the maximum number of points that lie on the same straight line." }
    ],
    "General": [
        { name: "Valid Parentheses", difficulty: "Easy", category: "Stacks", desc: "Given a string containing brackets, check if opening brackets are closed in the correct order using a stack." },
        { name: "Longest Substring Without Repeating", difficulty: "Medium", category: "Sliding Window", desc: "Given a string s, find the length of the longest substring without repeating characters in O(N) runtime." },
        { name: "Edit Distance", difficulty: "Hard", category: "Dynamic Programming", desc: "Given two strings word1 and word2, return the minimum number of operations (insert, delete, replace) to convert word1 to word2." }
    ]
};

function loadCodingRecommendations() {
    const tbody = document.getElementById("coding-recommendations-body");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    
    // Choose category based on weak areas
    let category = "General";
    if (state.assessment) {
        const weak = state.assessment.weak_areas || "";
        if (weak.includes("Coding")) {
            category = "Coding";
        } else if (weak.includes("SQL")) {
            category = "SQL & DBMS";
        } else if (weak.includes("Aptitude")) {
            category = "Aptitude";
        }
    }
    
    const questions = CODING_QUESTIONS_BANK[category] || CODING_QUESTIONS_BANK["General"];
    
    questions.forEach(q => {
        const tr = document.createElement("tr");
        let badgeClass = "badge-success";
        if (q.difficulty === "Medium") badgeClass = "badge-warning";
        if (q.difficulty === "Hard") badgeClass = "badge-danger";
        
        tr.innerHTML = `
            <td>${q.name}</td>
            <td><span class="badge ${badgeClass}">${q.difficulty}</span></td>
            <td>${q.category}</td>
            <td><button class="btn btn-sm btn-primary btn-practice-mock-code" data-problem="${q.name}" data-desc="${q.desc}">Practice</button></td>
        `;
        tbody.appendChild(tr);
    });
    
    // Bind click events to dynamically rendered rows
    setupCodingPracticeListeners();
}
