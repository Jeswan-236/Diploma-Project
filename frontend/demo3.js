// ===== AI STUDY PLANNER =====
(function() {
    const generateBtn = document.getElementById('generateSchedule');
    const scheduleDisplay = document.getElementById('scheduleDisplay');
    const scheduleList = document.getElementById('scheduleList');
    const saveBtn = document.getElementById('saveSchedule');
    const clearBtn = document.getElementById('clearSchedule');

    // All available topics organized by subject
    const allTopics = {
        'HTML': [
            { topic: 'tags & structure', difficulty: 'easy' },
            { topic: 'forms & tables', difficulty: 'easy' },
            { topic: 'semantic HTML', difficulty: 'medium' },
            { topic: 'canvas', difficulty: 'hard' },
            { topic: 'SVG', difficulty: 'hard' }
        ],
        'CSS': [
            { topic: 'selectors & colors', difficulty: 'easy' },
            { topic: 'box model', difficulty: 'easy' },
            { topic: 'flexbox', difficulty: 'medium' },
            { topic: 'grid layout', difficulty: 'medium' },
            { topic: 'animations', difficulty: 'hard' },
            { topic: 'variables', difficulty: 'medium' }
        ],
        'JS': [
            { topic: 'variables & data', difficulty: 'easy' },
            { topic: 'functions', difficulty: 'easy' },
            { topic: 'arrays & loops', difficulty: 'easy' },
            { topic: 'DOM intro', difficulty: 'medium' },
            { topic: 'events', difficulty: 'mediuinm' },
            { topic: 'async JS', difficulty: 'hard' },
            { topic: 'fetch API', difficulty: 'hard' },
            { topic: 'classes', difficulty: 'medium' },
            { topic: 'design patterns', difficulty: 'hard' }
        ],
        'DB': [
            { topic: 'SQL basics', difficulty: 'easy' },
            { topic: 'CRUD ops', difficulty: 'medium' },
            { topic: 'joins', difficulty: 'hard' },
            { topic: 'indexes', difficulty: 'hard' }
        ],
        'Python': [
            { topic: 'Python basics', difficulty: 'easy' },
            { topic: 'variables & data', difficulty: 'easy' },
            { topic: 'functions', difficulty: 'medium' },
            { topic: 'lists & loops', difficulty: 'medium' },
            { topic: 'OOP', difficulty: 'hard' }
        ],
        'Java': [
            { topic: 'Java basics', difficulty: 'easy' },
            { topic: 'variables & data', difficulty: 'easy' },
            { topic: 'methods', difficulty: 'medium' },
            { topic: 'OOP concepts', difficulty: 'hard' }
        ]
    };

    const iconMap = {
        'HTML': '<i class="fab fa-html5"></i>',
        'CSS': '<i class="fab fa-css3-alt"></i>',
        'JS': '<i class="fab fa-js"></i>',
        'DB': '<i class="fas fa-database"></i>',
        'Python': '<i class="fab fa-python"></i>',
        'Java': '<i class="fab fa-java"></i>'
    };

    const timeSlots = {
        'morning': '6:00 AM - 12:00 PM',
        'afternoon': '12:00 PM - 6:00 PM',
        'evening': '6:00 PM - 10:00 PM'
    };

    let generatedSchedule = [];

    function getSelectedSubjects() {
        const subjects = [];
        if (document.getElementById('subjectHTML') && document.getElementById('subjectHTML').checked) subjects.push('HTML');
        if (document.getElementById('subjectCSS') && document.getElementById('subjectCSS').checked) subjects.push('CSS');
        if (document.getElementById('subjectJS') && document.getElementById('subjectJS').checked) subjects.push('JS');
        if (document.getElementById('subjectDB') && document.getElementById('subjectDB').checked) subjects.push('DB');
        if (document.getElementById('subjectPython') && document.getElementById('subjectPython').checked) subjects.push('Python');
        if (document.getElementById('subjectJava') && document.getElementById('subjectJava').checked) subjects.push('Java');
        return subjects;
    }

    function getPreferredDays() {
        const days = [];
        if (document.getElementById('weekdays') && document.getElementById('weekdays').checked) days.push('weekday');
        if (document.getElementById('weekends') && document.getElementById('weekends').checked) days.push('weekend');
        return days;
    }

    function getTimeSlot() {
        const selected = document.querySelector('input[name="timeSlot"]:checked');
        return selected ? selected.value : 'morning';
    }

    function getDayName(dayIndex) {
        // JS `getDay()` returns 0..6 with 0 === Sunday — map accordingly
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        return days[dayIndex] || '';
    }

    function generateAISchedule() {
        const subjects = getSelectedSubjects();
        const preferredDays = getPreferredDays();
        const timeSlot = getTimeSlot();

        if (subjects.length === 0) {
            alert('Please select at least one subject!');
            return;
        }

        if (preferredDays.length === 0) {
            alert('Please select at least one day type!');
            return;
        }

        // Build available topics list
        let availableTopics = [];
        subjects.forEach(subject => {
            if (allTopics[subject]) {
                allTopics[subject].forEach(t => {
                    availableTopics.push({ subject, ...t });
                });
            }
        });

        // Sort by difficulty (easy first for momentum)
        availableTopics.sort((a, b) => {
            const difficultyOrder = { easy: 1, medium: 2, hard: 3 };
            return difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
        });

        // Generate schedule for 30 days
        generatedSchedule = [];
        let topicIndex = 0;
        const startDate = new Date('2026-01-01');

        for (let day = 0; day < 30; day++) {
            const currentDate = new Date(startDate);
            currentDate.setDate(currentDate.getDate() + day);
            const dayOfWeek = currentDate.getDay();
            const isWeekend = (dayOfWeek === 0 || dayOfWeek === 6);

            // Check if this day type is allowed
            const dayType = isWeekend ? 'weekend' : 'weekday';
            if (!preferredDays.includes(dayType)) {
                continue;
            }

            // Get a topic if available
            if (topicIndex < availableTopics.length) {
                const topic = availableTopics[topicIndex];
                generatedSchedule.push({
                    day: day + 1,
                    date: currentDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                    dayName: getDayName(dayOfWeek),
                    subject: topic.subject,
                    topic: topic.topic,
                    difficulty: topic.difficulty,
                    timeSlot: timeSlots[timeSlot]
                });
                topicIndex++;
            } else {
                // Review day if no more topics
                generatedSchedule.push({
                    day: day + 1,
                    date: currentDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                    dayName: getDayName(dayOfWeek),
                    subject: 'Review',
                    topic: 'Practice & Review',
                    difficulty: 'review',
                    timeSlot: timeSlots[timeSlot]
                });
            }
        }

        displaySchedule();
    }

    function displaySchedule() {
        if (!scheduleList) return;
        
        scheduleList.innerHTML = '';
        
        if (generatedSchedule.length === 0) {
            scheduleList.innerHTML = '<p style="text-align: center; color: #bdc9ff;">No study days match your preferences. Try adjusting your settings.</p>';
            if (scheduleDisplay) scheduleDisplay.style.display = 'block';
            return;
        }

        generatedSchedule.forEach(item => {
            const div = document.createElement('div');
            div.className = 'schedule-item';
            
            let subjectIcon = iconMap[item.subject] || '<i class="fas fa-book"></i>';
            let difficultyColor = item.difficulty === 'easy' ? '#7cf596' : 
                                 item.difficulty === 'medium' ? '#ffd58c' : 
                                 item.difficulty === 'hard' ? '#ff7b7b' : '#bdc9ff';
            
            div.innerHTML = `
                <div class="schedule-day">
                    <span class="day-num">${item.day}</span>
                    <div class="day-info">
                        <div>${item.dayName}</div>
                        <div class="date">${item.date}</div>
                    </div>
                </div>
                <div class="schedule-subject">
                    <div class="subject-name">${subjectIcon} ${item.subject}</div>
                    <div class="topic-name" style="color: ${difficultyColor}">${item.topic}</div>
                    <div class="time-slot"><i class="fas fa-clock"></i> ${item.timeSlot}</div>
                </div>
            `;
            scheduleList.appendChild(div);
        });

        if (scheduleDisplay) scheduleDisplay.style.display = 'block';
    }

    function saveSchedule() {
        if (generatedSchedule.length === 0) {
            alert('No schedule to save! Generate one first.');
            return;
        }
        localStorage.setItem('aiStudySchedule', JSON.stringify(generatedSchedule));
        alert('Schedule saved successfully!');
        if (typeof syncDataWithServer === 'function') {
            syncDataWithServer().catch(() => {});
        }
    }

    function clearSchedule() {
        generatedSchedule = [];
        if (scheduleDisplay) scheduleDisplay.style.display = 'none';
        localStorage.removeItem('aiStudySchedule');
        if (typeof syncDataWithServer === 'function') {
            syncDataWithServer().catch(() => {});
        }
    }

    function loadSavedSchedule() {
        const saved = localStorage.getItem('aiStudySchedule');
        if (saved) {
            try {
                generatedSchedule = JSON.parse(saved);
                displaySchedule();
            } catch (e) {
                console.log('Could not load saved schedule');
            }
        }
    }

    if (generateBtn) {
        generateBtn.addEventListener('click', generateAISchedule);
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', saveSchedule);
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', clearSchedule);
    }

    // Load saved schedule on page load
    loadSavedSchedule();

    // Feature modal handlers (exposed globally for inline onclick in HTML)
    window.openFeatureModal = function(feature) {
        const overlay = document.getElementById('featureModal');
        const content = document.getElementById('featureModalContent');
        const title = document.getElementById('featureModalTitle');
        const icon = document.getElementById('featureModalIcon');

        if (!overlay || !content || !title || !icon) return;
        title.textContent = feature ? (feature[0].toUpperCase() + feature.slice(1)) : 'Feature';

        const featureIcons = {
            meditation: '<i class="fas fa-spa"></i>',
            exam: '<i class="fas fa-clipboard-check"></i>',
            coding: '<i class="fas fa-code"></i>',
            practice: '<i class="fas fa-laptop-code"></i>'
        };

        icon.innerHTML = featureIcons[feature] || '<i class="fas fa-book"></i>';

        // Special content for meditation: curated YouTube video class links
        if (feature === 'meditation') {
            const videos = [
                { title: '5-Minute Guided Meditation', query: 'guided+meditation+5+minutes' },
                { title: '10-Minute Mindfulness Practice', query: '10+minute+mindfulness+meditation' },
                { title: 'Guided Sleep Meditation', query: 'guided+sleep+meditation' },
                { title: 'Breathing Exercise for Focus', query: 'breathing+exercise+meditation' }
            ];

            content.innerHTML = `
                <div style="padding:0.6rem;color:#bdc9ff;">
                    <p>Curated meditation class videos from YouTube. Click a card to open the YouTube search for that session.</p>
                </div>
                <div class="video-card-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0.6rem;padding:0.6rem;">
                    ${videos.map(v => `
                        <a class="med-card" href="https://www.youtube.com/results?search_query=${v.query}" target="_blank" rel="noopener" style="display:block;background:#0f1330;padding:0.8rem;border-radius:8px;color:#e6ecff;text-decoration:none;box-shadow:0 6px 18px rgba(0,0,0,0.4)">
                            <div style="font-weight:700;margin-bottom:0.4rem">${v.title}</div>
                            <div style="font-size:0.9rem;color:#9fb0ff">Open on YouTube</div>
                        </a>
                    `).join('')}
                </div>
            `;
        } else {
            content.innerHTML = `<p style="color:#bdc9ff; padding: 1rem;">Quick resources for <strong>${title.textContent}</strong> will appear here.</p>`;
        }

        // Coding resources: HTML, CSS, JavaScript, Python
        if (feature === 'coding') {
            const codingVideos = [
                { title: 'HTML Crash Course', query: 'html+crash+course' },
                { title: 'CSS Flexbox & Grid', query: 'css+flexbox+grid+tutorial' },
                { title: 'JavaScript DOM & Basics', query: 'javascript+dom+tutorial' },
                { title: 'Python for Beginners', query: 'python+for+beginners+tutorial' }
            ];

            content.innerHTML = `
                <div style="padding:0.6rem;color:#bdc9ff;">
                    <p>Curated coding video classes. Click a card to open YouTube search results for that topic.</p>
                </div>
                <div class="video-card-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0.6rem;padding:0.6rem;">
                    ${codingVideos.map(v => `
                        <a class="med-card" href="https://www.youtube.com/results?search_query=${v.query}" target="_blank" rel="noopener" style="display:block;background:#0f1330;padding:0.8rem;border-radius:8px;color:#e6ecff;text-decoration:none;box-shadow:0 6px 18px rgba(0,0,0,0.4)">
                            <div style="font-weight:700;margin-bottom:0.4rem">${v.title}</div>
                            <div style="font-size:0.9rem;color:#9fb0ff">Open on YouTube</div>
                        </a>
                    `).join('')}
                </div>
            `;
            overlay.classList.add('active');
            return;
        }
        overlay.classList.add('active');
    };

    window.closeFeatureModal = function() {
        const overlay = document.getElementById('featureModal');
        if (overlay) overlay.classList.remove('active');
    };
})();


// ===== 30-DAY STREAK GRID =====
(function() {
    const grid = document.getElementById('daysGrid');
    const topics = [
        { lang: 'HTML', topic: 'tags & structure', status: 'completed' },
        { lang: 'HTML', topic: 'forms & tables', status: 'completed' },
        { lang: 'CSS', topic: 'selectors & colors', status: 'completed' },
        { lang: 'CSS', topic: 'box model', status: 'completed' },
        { lang: 'CSS', topic: 'flexbox', status: 'completed' },
        { lang: 'JS', topic: 'variables & data', status: 'completed' },
        { lang: 'JS', topic: 'functions', status: 'completed' },
        { lang: 'JS', topic: 'arrays & loops', status: 'completed' },
        { lang: 'JS', topic: 'DOM intro', status: 'completed' },
        { lang: 'JS', topic: 'events', status: 'completed' },
        { lang: 'DB', topic: 'SQL basics', status: 'in-progress' },
        { lang: 'DB', topic: 'CRUD ops', status: 'in-progress' },
        { lang: 'Python', topic: 'Python basics', status: 'locked' },
        { lang: 'Python', topic: 'variables & data', status: 'locked' },
        { lang: 'DB', topic: 'MongoDB intro', status: 'locked' },
        { lang: 'HTML', topic: 'semantic HTML', status: 'completed' },
        { lang: 'CSS', topic: 'grid layout', status: 'completed' },
        { lang: 'JS', topic: 'async JS', status: 'in-progress' },
        { lang: 'JS', topic: 'fetch API', status: 'locked' },
        { lang: 'Java', topic: 'Java basics', status: 'locked' },
        { lang: 'DB', topic: 'joins', status: 'locked' },
        { lang: 'HTML', topic: 'canvas', status: 'locked' },
        { lang: 'CSS', topic: 'animations', status: 'locked' },
        { lang: 'JS', topic: 'classes', status: 'locked' },
        { lang: 'Python', topic: 'functions', status: 'locked' },
        { lang: 'DB', topic: 'indexes', status: 'locked' },
        { lang: 'HTML', topic: 'SVG', status: 'locked' },
        { lang: 'CSS', topic: 'variables', status: 'locked' },
        { lang: 'JS', topic: 'design patterns', status: 'locked' },
        { lang: 'Project', topic: 'fullstack mini', status: 'locked' }
    ];
    
    const iconMap = { 
        'HTML': '<i class="fab fa-html5"></i>', 
        'CSS': '<i class="fab fa-css3-alt"></i>', 
        'JS': '<i class="fab fa-js"></i>', 
        'DB': '<i class="fas fa-database"></i>', 
        'Python': '<i class="fab fa-python"></i>',
        'Java': '<i class="fab fa-java"></i>',
        'Project': '<i class="fas fa-code-branch"></i>' 
    };

    // Load streak overrides from localStorage (keys: 1..n -> status)
    const savedStreak = (function(){ try { return JSON.parse(localStorage.getItem('streakDays')||'{}'); } catch(e){ return {}; } })();

if (grid) {
        topics.forEach((item, index) => {
            const dayNum = index + 1;
            const status = savedStreak[dayNum] || 'locked';
            const day = document.createElement('div');
            day.className = `day-circle ${status}`;
            day.setAttribute('data-tooltip', `${item.lang}: ${item.topic}`);
            day.setAttribute('data-day-num', String(dayNum));
            day.innerHTML = `${dayNum}<span>${item.lang}</span>`;
            grid.appendChild(day);
        });
        updateStreakCounter();
    }

// Expose helper to mark the next incomplete streak day as completed
window.completeNextStreakDay = function() {
        try {
            const stored = JSON.parse(localStorage.getItem('streakDays') || '{}');
            for (let i = 1; i <= topics.length; i++) {
                if (stored[i] !== 'completed' && topics[i-1]) {
                    stored[i] = 'completed';
                    localStorage.setItem('streakDays', JSON.stringify(stored));
                    updateStreakCounter();
                    if (typeof syncDataWithServer === 'function') {
                        syncDataWithServer().catch(() => {});
                    }
                    return i;
                }
            }
        } catch (e) {
            console.error('Could not update streak', e);
        }
        return null;
    };

// Helper functions
    function updateStreakCounter() {
        const counter = document.getElementById('streakCounter');
        if (!counter) return;
        try {
            const saved = JSON.parse(localStorage.getItem('streakDays') || '{}');
            let streak = 0;
            for (let i = 1; i <= 30; i++) {
                if (saved[i] === 'completed') {
                    streak++;
                } else {
                    break;
                }
            }
            counter.textContent = streak;
        } catch (e) {
            console.error('Could not update streak counter', e);
            counter.textContent = '0';
        }
    }

    function showStreakToast(msg, isSuccess = false) {
        let toast = document.getElementById('streakToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'streakToast';
            toast.className = 'toast-popup';
            document.body.appendChild(toast);
        }
        toast.innerHTML = `<i class="fas ${isSuccess ? 'fa-check-circle' : 'fa-exclamation-triangle'}"></i> ${msg}`;
        if (isSuccess) toast.classList.add('success');
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show', 'success');
        }, 3000);
    }

    function resetAndRepopulateGrid() {
        const grid = document.getElementById('daysGrid');
        if (!grid) return;
        grid.innerHTML = '';
        topics.forEach((item, index) => {
            const dayNum = index + 1;
            const day = document.createElement('div');
            day.className = 'day-circle locked';
            day.setAttribute('data-tooltip', `${item.lang}: ${item.topic}`);
            day.setAttribute('data-day-num', String(dayNum));
            day.innerHTML = `${dayNum}<span>${item.lang}</span>`;
            grid.appendChild(day);
        });
        updateStreakCounter();
    }

    // Reset streak button handler
    const resetStreakBtn = document.getElementById('resetStreak');
    if (resetStreakBtn) {
        resetStreakBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to reset your streak progress? This will clear all progress and set streak to 0.')) {
                localStorage.removeItem('streakDays');
                resetAndRepopulateGrid();
                showStreakToast('Streak reset successfully! Start fresh 🔥', true);
            } else {
                showStreakToast('Reset cancelled.', false);
            }
        });
    }
})();


// ===== 2026 CALENDAR WITH EDITABLE TOPICS =====
(function() {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const grid = document.getElementById('year2026Grid');
    const monthLabel = document.getElementById('currentMonthName');
    const aiSuggestBtn = document.getElementById('aiSuggestBtn');
    
    // Modal elements
    const modal = document.getElementById('topicModal');
    const modalTitle = document.getElementById('modalTitle');
    const topicForm = document.getElementById('topicForm');
    const selectedDayInput = document.getElementById('selectedDay');
    const selectedMonthInput = document.getElementById('selectedMonth');
    const subjectSelect = document.getElementById('topicSubject');
    const topicNameInput = document.getElementById('topicName');
    const timeSelect = document.getElementById('topicTime');
    const cancelBtn = document.getElementById('cancelBtn');
    const deleteBtn = document.getElementById('deleteBtn');

    let currentMonthIndex = 0;
    let isAnimating = false;
    let calendarTopics = {}; // Key: "month-day", Value: {subject, topic, time}

    // Load saved topics
    function loadCalendarTopics() {
        const saved = localStorage.getItem('calendarTopics');
        if (saved) {
            try {
                calendarTopics = JSON.parse(saved);
            } catch (e) {
                calendarTopics = {};
            }
        }
    }

    // Save topics to localStorage
    function saveCalendarTopics() {
        localStorage.setItem('calendarTopics', JSON.stringify(calendarTopics));
        if (typeof syncDataWithServer === 'function') {
            syncDataWithServer().catch(() => {});
        }
    }

    // Get topic for a specific day
    function getDayTopic(month, day) {
        const key = `${month}-${day}`;
        return calendarTopics[key] || null;
    }

    // Set topic for a specific day
    function setDayTopic(month, day, subject, topic, time) {
        const key = `${month}-${day}`;
        if (subject && topic) {
            calendarTopics[key] = { subject, topic, time };
        } else {
            delete calendarTopics[key];
        }
        saveCalendarTopics();
    }

    // Open modal for editing a day
    function openDayModal(month, day) {
        if (!modal) return;
        
        const topic = getDayTopic(month, day);
        
        selectedMonthInput.value = month;
        selectedDayInput.value = day;
        modalTitle.textContent = `${monthNames[month]} ${day}, 2026`;
        
        if (topic) {
            subjectSelect.value = topic.subject;
            topicNameInput.value = topic.topic;
            timeSelect.value = topic.time;
            deleteBtn.style.display = 'block';
        } else {
            subjectSelect.value = '';
            topicNameInput.value = '';
            timeSelect.value = 'morning';
            deleteBtn.style.display = 'none';
        }
        
        modal.classList.add('active');
    }

    // Close modal
    function closeModal() {
        if (modal) {
            modal.classList.remove('active');
        }
    }

    // Save topic from modal
    function saveTopic(e) {
        e.preventDefault();
        
        const month = parseInt(selectedMonthInput.value);
        const day = parseInt(selectedDayInput.value);
        const subject = subjectSelect.value;
        const topic = topicNameInput.value.trim();
        const time = timeSelect.value;
        
        if (!subject || !topic) {
            alert('Please select a subject and enter a topic!');
            return;
        }
        
        setDayTopic(month, day, subject, topic, time);
        closeModal();
        populateCalendar(currentMonthIndex);
    }

    // Delete topic
    function deleteTopic() {
        const month = parseInt(selectedMonthInput.value);
        const day = parseInt(selectedDayInput.value);
        
        setDayTopic(month, day, null, null, null);
        closeModal();
        populateCalendar(currentMonthIndex);
    }

    // AI Suggest Schedule
    function aiSuggestSchedule() {
        const confirmAI = confirm('This will populate your calendar with AI-suggested topics. Existing topics will be kept. Continue?');
        if (!confirmAI) return;

        // Get all topics
        const allTopicsList = [
            { subject: 'HTML', topic: 'tags & structure' },
            { subject: 'HTML', topic: 'forms & tables' },
            { subject: 'HTML', topic: 'semantic HTML' },
            { subject: 'CSS', topic: 'selectors & colors' },
            { subject: 'CSS', topic: 'box model' },
            { subject: 'CSS', topic: 'flexbox' },
            { subject: 'CSS', topic: 'grid layout' },
            { subject: 'JS', topic: 'variables & data' },
            { subject: 'JS', topic: 'functions' },
            { subject: 'JS', topic: 'arrays & loops' },
            { subject: 'JS', topic: 'DOM intro' },
            { subject: 'JS', topic: 'events' },
            { subject: 'JS', topic: 'async JS' },
            { subject: 'DB', topic: 'SQL basics' },
            { subject: 'DB', topic: 'CRUD ops' },
            { subject: 'Python', topic: 'Python basics' },
            { subject: 'Python', topic: 'functions' },
            { subject: 'Java', topic: 'Java basics' }
        ];

        // Fill weekdays with topics
        const times = ['morning', 'afternoon', 'evening'];
        let topicIndex = 0;

        for (let month = 0; month < 12; month++) {
            const daysInMonth = new Date(2026, month + 1, 0).getDate();
            
            for (let day = 1; day <= daysInMonth; day++) {
                const date = new Date(2026, month, day);
                const dayOfWeek = date.getDay();
                
                // Skip weekends
                if (dayOfWeek === 0 || dayOfWeek === 6) continue;
                
                // Skip if already has topic
                if (getDayTopic(month, day)) continue;
                
                // Add topic if available
                if (topicIndex < allTopicsList.length) {
                    const t = allTopicsList[topicIndex];
                    const time = times[Math.floor(Math.random() * times.length)];
                    setDayTopic(month, day, t.subject, t.topic, time);
                    topicIndex++;
                }
            }
        }

        populateCalendar(currentMonthIndex);
        alert('AI has suggested topics for your calendar! Click on any day to edit.');
    }

    if (!grid) return;

    function populateCalendar(monthIndex) {
        grid.innerHTML = '';
        
        // Add month marker
        const marker = document.createElement('div');
        marker.className = 'month-marker';
        marker.innerHTML = `<i class="fas fa-calendar-alt"></i> ${monthNames[monthIndex]} 2026`;
        grid.appendChild(marker);
        
        // Get first day of month
        const firstDay = new Date(2026, monthIndex, 1).getDay();
        const daysInMonth = new Date(2026, monthIndex + 1, 0).getDate();
        
        // Adjust for Monday start
        const adjustedFirstDay = firstDay === 0 ? 6 : firstDay - 1;
        
        // Empty cells before first day
        for (let i = 0; i < adjustedFirstDay; i++) {
            const empty = document.createElement('div');
            empty.className = 'day-cell';
            empty.style.opacity = '0.3';
            grid.appendChild(empty);
        }
        
        // Days
        for (let d = 1; d <= daysInMonth; d++) {
            const cell = document.createElement('div');
            cell.className = 'day-cell';
            
            const dayOfWeek = new Date(2026, monthIndex, d).getDay();
            if (dayOfWeek === 0 || dayOfWeek === 6) {
                cell.classList.add('weekend');
            }
            
            // Check if has topic
            const topic = getDayTopic(monthIndex, d);
            if (topic) {
                cell.classList.add('has-topic');
                cell.innerHTML = `
                    ${d}
                    <span class="topic-badge">
                        <span class="day-subject">${topic.subject}</span>
                    </span>
                `;
            } else {
                cell.innerText = d;
            }
            
            // Add click handler
            cell.addEventListener('click', () => openDayModal(monthIndex, d));
            
            grid.appendChild(cell);
        }
    }

    function renderMonth(monthIndex, direction) {
        if (isAnimating) return;
        
        if (direction) {
            isAnimating = true;
            const oldGrid = grid.cloneNode(true);
            grid.parentNode.appendChild(oldGrid);
            oldGrid.classList.add(direction === 'left' ? 'slide-left' : 'slide-right');
            
            populateCalendar(monthIndex);
            
            setTimeout(() => {
                oldGrid.remove();
                if (monthLabel) monthLabel.innerText = `${monthNames[monthIndex]} 2026`;
                setTimeout(() => {
                    grid.classList.remove('slide-left');
                    isAnimating = false;
                }, 50);
            }, 400);
        } else {
            populateCalendar(monthIndex);
            if (monthLabel) monthLabel.innerText = `${monthNames[monthIndex]} 2026`;
            isAnimating = false;
        }
    }

    // Initialize
    loadCalendarTopics();
    renderMonth(0);

    // Navigation buttons
    const prevBtn = document.getElementById('prevMonth');
    const nextBtn = document.getElementById('nextMonth');

    if (prevBtn) {
        prevBtn.onclick = () => {
            if (isAnimating) return;
            currentMonthIndex = (currentMonthIndex - 1 + 12) % 12;
            renderMonth(currentMonthIndex, 'right');
        };
    }

    if (nextBtn) {
        nextBtn.onclick = () => {
            if (isAnimating) return;
            currentMonthIndex = (currentMonthIndex + 1) % 12;
            renderMonth(currentMonthIndex, 'left');
        };
    }

    // AI Suggest button
    if (aiSuggestBtn) {
        aiSuggestBtn.addEventListener('click', aiSuggestSchedule);
    }

    // Modal event listeners
    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeModal);
    }
    
    if (deleteBtn) {
        deleteBtn.addEventListener('click', deleteTopic);
    }
    
    if (topicForm) {
        topicForm.addEventListener('submit', saveTopic);
    }
    
    // Close modal on overlay click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
})();


// ===== STUDENT PORTAL LOGIC =====
(function() {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMsg');
    
    function showToast(msg, isSuccess = false) {
        if (!toast || !toastMsg) return;
        toastMsg.innerText = msg;
        toast.style.background = isSuccess ? '#2f9e5a' : '#d94f4f';
        toast.classList.add('show');
        setTimeout(() => { toast.classList.remove('show'); }, 2500);
    }

    const loginBtn = document.getElementById('loginBtn');
    const usernameInp = document.getElementById('username');
    const passwordInp = document.getElementById('password');

    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            const user = usernameInp ? usernameInp.value.trim() : '';
            const pass = passwordInp ? passwordInp.value.trim() : '';
            
            if (user === 'student' && pass === '2026') {
                showToast('✓ login successful (demo)', true);
                const card = document.querySelector('.portal-card');
                if (card) {
                    card.style.boxShadow = '0 0 50px #5fe07e';
                    setTimeout(() => card.style.boxShadow = '', 1000);
                }
            } else {
                showToast('✗ incorrect username or password');
                const card = document.querySelector('.portal-card');
                if (card) {
                    card.classList.add('shake');
                    setTimeout(() => card.classList.remove('shake'), 500);
                }
            }
        });
    }

    // Social login buttons
    const googleLogin = document.getElementById('googleLogin');
    if (googleLogin) {
        googleLogin.addEventListener('click', () => {
            showToast('⚡ continue with Google (demo)', false);
        });
    }
    
    const phoneLogin = document.getElementById('phoneLogin');
    if (phoneLogin) {
        phoneLogin.addEventListener('click', () => {
            showToast('📱 phone login demo', false);
        });
    }
})();