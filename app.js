/* ==========================================================================
   STUDYTRACK FRONTEND APPLICATION LOGIC
   Uses async/await, Event Delegation, document.createElement DOM creation,
   and error banner handling.
   ========================================================================== */

const API_BASE = ''; // Relative path for single-process FastAPI static mounting

// DOM Element References
const rosterList = document.getElementById('roster-list');
const studentForm = document.getElementById('student-form');
const errorBanner = document.getElementById('error-banner');
const refreshRosterBtn = document.getElementById('refresh-roster-btn');

// Algorithms DOM References
const sortAgeBtn = document.getElementById('sort-age-btn');
const sortNameBtn = document.getElementById('sort-name-btn');
const sortResultsBox = document.getElementById('sort-results');
const binarySearchForm = document.getElementById('binary-search-form');
const searchNameInput = document.getElementById('search-name-input');
const binarySearchResultsBox = document.getElementById('binary-search-results');
const reportForm = document.getElementById('report-form');
const reportMinAgeInput = document.getElementById('report-min-age');
const reportResultsBox = document.getElementById('report-results');

// AI Assistant DOM References
const noteInput = document.getElementById('note-input');
const summarizeBtn = document.getElementById('summarize-btn');
const summaryOutputBox = document.getElementById('summary-output');
const summaryTopicEl = document.getElementById('summary-topic');
const summaryDifficultyEl = document.getElementById('summary-difficulty');
const summaryPointsEl = document.getElementById('summary-points');
const aiSearchQueryInput = document.getElementById('ai-search-query');
const searchNotesBtn = document.getElementById('search-notes-btn');
const searchResultsBox = document.getElementById('search-results');

// Course Management DOM References
const courseForm = document.getElementById('course-form');
const courseStudentIdInput = document.getElementById('course-student-id');
const courseNameInput = document.getElementById('course-name');
const courseCreditsInput = document.getElementById('course-credits');
const coursesListEl = document.getElementById('courses-list');
const refreshCoursesBtn = document.getElementById('refresh-courses-btn');

// ==========================================
// ERROR HANDLING BANNER HELPERS
// ==========================================
function showError(message) {
  if (errorBanner) {
    errorBanner.textContent = `Error: ${message}`;
    errorBanner.classList.remove('hidden');
  }
}

function clearError() {
  if (errorBanner) {
    errorBanner.textContent = '';
    errorBanner.classList.add('hidden');
  }
}

// ==========================================
// DYNAMIC DOM CARD CREATION (document.createElement)
// ==========================================
function createStudentCardElement(student) {
  const card = document.createElement('div');
  card.className = 'student-card';
  card.setAttribute('data-id', student.id);

  // Name
  const nameEl = document.createElement('h4');
  nameEl.className = 'student-name';
  nameEl.textContent = student.name;

  // Email
  const emailEl = document.createElement('p');
  emailEl.className = 'student-email';
  emailEl.textContent = student.email;

  // Age Container & Pre-filled Number Input
  const ageRow = document.createElement('div');
  ageRow.className = 'student-age-row';

  const ageLabel = document.createElement('span');
  ageLabel.className = 'student-age-label';
  ageLabel.textContent = 'Age:';

  const ageDisplay = document.createElement('span');
  ageDisplay.className = 'age-display';
  ageDisplay.textContent = student.age;

  const ageInput = document.createElement('input');
  ageInput.type = 'number';
  ageInput.className = 'age-input';
  ageInput.value = student.age;
  ageInput.min = '1';

  ageRow.appendChild(ageLabel);
  ageRow.appendChild(ageDisplay);
  ageRow.appendChild(ageInput);

  // Actions Bar with Save Age & Delete Buttons
  const actionsRow = document.createElement('div');
  actionsRow.className = 'card-actions';

  const saveAgeBtn = document.createElement('button');
  saveAgeBtn.className = 'btn secondary-btn small-btn save-age-btn';
  saveAgeBtn.setAttribute('data-id', student.id);
  saveAgeBtn.textContent = 'Save Age';

  const deleteBtn = document.createElement('button');
  deleteBtn.className = 'btn danger-btn small-btn delete-btn';
  deleteBtn.setAttribute('data-id', student.id);
  deleteBtn.textContent = 'Delete';

  const courseBadge = document.createElement('span');
  courseBadge.className = 'course-count-badge';
  courseBadge.textContent = 'Courses: ...';
  fetchCourseCount(student.id, courseBadge);

  actionsRow.appendChild(saveAgeBtn);
  actionsRow.appendChild(deleteBtn);
  actionsRow.appendChild(courseBadge);

  // Assemble Student Card
  card.appendChild(nameEl);
  card.appendChild(emailEl);
  card.appendChild(ageRow);
  card.appendChild(actionsRow);

  return card;
}

// Fetch aggregate course count for a student
async function fetchCourseCount(studentId, badgeElement) {
  try {
    const res = await fetch(`${API_BASE}/students/${studentId}/course-count`);
    if (res.ok) {
      const data = await res.json();
      badgeElement.textContent = `Courses: ${data.course_count}`;
    }
  } catch (err) {
    console.error('Course count fetch failed', err);
  }
}

// ==========================================
// INITIAL ROSTER FETCH (GET /students/)
// ==========================================
async function fetchStudentRoster() {
  clearError();
  try {
    const response = await fetch(`${API_BASE}/students/`);
    if (!response.ok) {
      throw new Error(`Failed to load student roster (Status ${response.status})`);
    }
    const students = await response.json();
    
    // Clear list safely without rebuilding innerHTML for dynamic appends
    rosterList.replaceChildren();

    students.forEach(student => {
      const card = createStudentCardElement(student);
      rosterList.appendChild(card);
    });
  } catch (err) {
    showError(err.message || 'Unable to connect to backend server');
  }
}

// ==========================================
// EVENT DELEGATION ON #roster-list
// Attach ONE listener to #roster-list for Save Age and Delete
// ==========================================
rosterList.addEventListener('click', async (event) => {
  const target = event.target;

  // SAVE AGE BUTTON CLICK
  if (target.classList.contains('save-age-btn')) {
    clearError();
    const studentId = target.getAttribute('data-id');
    const card = target.closest('.student-card');
    const ageInput = card.querySelector('.age-input');
    const ageDisplay = card.querySelector('.age-display');
    const newAge = parseInt(ageInput.value, 10);

    if (isNaN(newAge) || newAge <= 0) {
      showError('Age must be a positive integer greater than 0');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/students/${studentId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age: newAge })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to update age (Status ${response.status})`);
      }

      const updatedStudent = await response.json();
      // On success: update displayed age in that card
      ageDisplay.textContent = updatedStudent.age;
      ageInput.value = updatedStudent.age;
    } catch (err) {
      showError(err.message);
    }
  }

  // DELETE BUTTON CLICK
  if (target.classList.contains('delete-btn')) {
    clearError();
    const studentId = target.getAttribute('data-id');
    const card = target.closest('.student-card');

    try {
      const response = await fetch(`${API_BASE}/students/${studentId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to delete student (Status ${response.status})`);
      }

      // On success: remove that card from the DOM
      card.remove();
    } catch (err) {
      showError(err.message);
    }
  }
});

// ==========================================
// ADD STUDENT FORM SUBMIT (POST /students/)
// ==========================================
studentForm.addEventListener('submit', async (event) => {
  event.preventDefault(); // Prevent full page reload
  clearError();

  const nameInput = document.getElementById('student-name');
  const emailInput = document.getElementById('student-email');
  const ageInput = document.getElementById('student-age');

  const newStudentData = {
    name: nameInput.value.trim(),
    email: emailInput.value.trim(),
    age: parseInt(ageInput.value, 10)
  };

  try {
    const response = await fetch(`${API_BASE}/students/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newStudentData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      if (Array.isArray(errorData.detail)) {
        throw new Error(errorData.detail.map(d => d.msg).join(', '));
      }
      throw new Error(errorData.detail || `Failed to add student (Status ${response.status})`);
    }

    const createdStudent = await response.json();
    
    // Create new card using document.createElement() and append immediately
    const card = createStudentCardElement(createdStudent);
    rosterList.appendChild(card);

    // Reset form fields
    studentForm.reset();
  } catch (err) {
    showError(err.message);
  }
});

// ==========================================
// ALGORITHMS ENGINE UI HANDLERS
// ==========================================
async function fetchSortedStudents(byField) {
  clearError();
  try {
    const response = await fetch(`${API_BASE}/students/sorted?by=${byField}`);
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Sorting failed');
    }
    const data = await response.json();
    sortResultsBox.textContent = data.map(s => `• ${s.name} (Age: ${s.age}, Email: ${s.email})`).join('\n');
  } catch (err) {
    showError(err.message);
  }
}

sortAgeBtn.addEventListener('click', () => fetchSortedStudents('age'));
sortNameBtn.addEventListener('click', () => fetchSortedStudents('name'));

binarySearchForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearError();
  const searchName = searchNameInput.value.trim();
  if (!searchName) return;

  try {
    const response = await fetch(`${API_BASE}/students/search?name=${encodeURIComponent(searchName)}`);
    if (response.status === 404) {
      binarySearchResultsBox.textContent = `Status 404: Student '${searchName}' not found.`;
      return;
    }
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Search failed');
    }
    const student = await response.json();
    binarySearchResultsBox.textContent = `Found Student (200 OK):\nID: ${student.id}\nName: ${student.name}\nEmail: ${student.email}\nAge: ${student.age}`;
  } catch (err) {
    showError(err.message);
  }
});

reportForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearError();
  const minAge = parseInt(reportMinAgeInput.value, 10);
  try {
    const response = await fetch(`${API_BASE}/students/report?min_age=${minAge}`);
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Report generation failed');
    }
    const data = await response.json();
    reportResultsBox.textContent = `Report:\n${data.report}\n\nCount Meeting Min Age (>= ${minAge}): ${data.count_meeting_min_age}`;
  } catch (err) {
    showError(err.message);
  }
});

// ==========================================
// OFFLINE AI ASSISTANT HANDLERS
// ==========================================
summarizeBtn.addEventListener('click', async () => {
  clearError();
  const text = noteInput.value;
  try {
    const response = await fetch(`${API_BASE}/assistant/summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    if (!response.ok) {
      throw new Error('Summarization failed');
    }

    const data = await response.json();
    summaryTopicEl.textContent = data.topic;
    summaryDifficultyEl.textContent = data.difficulty;
    summaryDifficultyEl.className = `badge ${data.difficulty}-badge`;

    summaryPointsEl.replaceChildren();
    if (data.key_points.length === 0) {
      const li = document.createElement('li');
      li.textContent = 'No key points extracted.';
      summaryPointsEl.appendChild(li);
    } else {
      data.key_points.forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        summaryPointsEl.appendChild(li);
      });
    }

    summaryOutputBox.classList.remove('hidden');
  } catch (err) {
    showError(err.message);
  }
});

async function runSemanticSearch() {
  clearError();
  const query = aiSearchQueryInput.value.trim();
  try {
    const response = await fetch(`${API_BASE}/assistant/search?query=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error('Semantic search failed');
    }

    const results = await response.json();
    searchResultsBox.replaceChildren();

    results.forEach(note => {
      const item = document.createElement('div');
      item.className = 'search-result-item';

      const textEl = document.createElement('span');
      textEl.textContent = `[Note #${note.id}] ${note.text}`;

      const simEl = document.createElement('span');
      simEl.className = 'sim-score';
      simEl.textContent = `Score: ${note.similarity}`;

      item.appendChild(textEl);
      item.appendChild(simEl);
      searchResultsBox.appendChild(item);
    });
  } catch (err) {
    showError(err.message);
  }
}

searchNotesBtn.addEventListener('click', runSemanticSearch);

// ==========================================
// COURSE MANAGEMENT HANDLERS
// ==========================================
async function fetchCourses() {
  try {
    const response = await fetch(`${API_BASE}/courses/`);
    if (response.ok) {
      const courses = await response.json();
      coursesListEl.replaceChildren();
      courses.forEach(c => {
        const div = document.createElement('div');
        div.className = 'course-card';
        div.textContent = `ID #${c.id} — ${c.course_name} (${c.credits} Credits) [Student ID: ${c.student_id}]`;
        coursesListEl.appendChild(div);
      });
    }
  } catch (err) {
    console.error('Fetch courses error', err);
  }
}

courseForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearError();
  const studentId = parseInt(courseStudentIdInput.value, 10);
  const courseName = courseNameInput.value.trim();
  const credits = parseInt(courseCreditsInput.value, 10);

  try {
    const response = await fetch(`${API_BASE}/courses/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, course_name: courseName, credits })
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Course enrollment failed');
    }

    courseForm.reset();
    fetchCourses();
    fetchStudentRoster(); // Refresh student roster to update course count badges
  } catch (err) {
    showError(err.message);
  }
});

refreshRosterBtn.addEventListener('click', fetchStudentRoster);
refreshCoursesBtn.addEventListener('click', fetchCourses);

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
  fetchStudentRoster();
  fetchCourses();
  runSemanticSearch(); // Initial search render
});
