# StudyTrack — Unified Full-Stack Study Management Platform

StudyTrack is a unified full-stack Study Management Platform featuring an integrated Algorithms Engine and an Offline AI Assistant. Built strictly using FastAPI, SQLAlchemy, SQLite, and vanilla HTML/CSS/JavaScript.

---

## 1. Project Overview

StudyTrack provides a single-process unified web application for managing student academic rosters, course enrollments, algorithmic data sorting/searching, and AI-driven study note summarization and semantic search.

---

## 2. Features

* **Core Roster Management**: Full Student and Course CRUD with strict Pydantic validation (email format with `@`, positive age validation, credit ranges 1–6) and handled duplicate email responses.
* **Database Aggregates**: Calculates student course enrollments using SQL `func.count()` aggregates directly in SQLite.
* **Algorithms Engine**:
  * **In-Place Insertion Sort**: Sorts live DB roster by age or name without using Python's built-in `sorted()` or `.sort()`.
  * **Iterative Binary Search**: Fast $O(\log n)$ student lookup by name on name-sorted rosters using `mid = low + (high - low) // 2`.
  * **Roster Report Generator**: Formatted roster overview string generator and accumulator-based age filter counting.
* **Offline AI Assistant**:
  * **Deterministic Note Summarizer**: Extracts main topic, up to 3 sentence key points, and word-count difficulty level.
  * **Semantic Note Search**: 12-token vocabulary vector embedding and manual cosine similarity note ranking.
* **Responsive UI Dashboard**: Semantic HTML5 layout, CSS box model, glassmorphism dark theme, event delegation on `#roster-list`, and dynamic DOM elements using `document.createElement()`.

---

## 3. Architecture

```text
+-------------------------------------------------------------------+
|                        Browser Dashboard                          |
|    HTML5 / Vanilla CSS (Box Model, Media Queries) / Plain JS      |
|           (Event Delegation, document.createElement DOM)          |
+-------------------------------------------------------------------+
                                 |
                          HTTP / REST API
                                 |
+-------------------------------------------------------------------+
|                         FastAPI Backend                           |
|  +-------------------+  +-------------------+  +----------------+ |
|  |   Core Roster     |  | Algorithms Engine |  | Offline AI     | |
|  |   CRUD Routes     |  | (Insertion Sort,  |  | (Summarizer &  | |
|  |   (SQLAlchemy)    |  |  Binary Search)   |  | Cosine Search) | |
|  +-------------------+  +-------------------+  +----------------+ |
|                                |                                  |
|                    SQLAlchemy ORM + SQLite DB                     |
+-------------------------------------------------------------------+
```

---

## 4. Folder Structure

```text
studytrack/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── algorithms.py
│   ├── ai_service.py
│   ├── seed_data.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── .env.example
├── .gitignore
└── README.md
```

---

## 5. Requirements

* Python 3.10+
* Dependencies:
  * `fastapi>=0.100.0`
  * `uvicorn[standard]>=0.20.0`
  * `sqlalchemy>=2.0.0`
  * `pydantic>=2.0.0`

---

## 6–10. Installation & Running Instructions

### Virtual Environment Setup & Requirements Installation

```bash
# 1. Navigate to the studytrack directory
cd studytrack

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r backend/requirements.txt
```

### Starting FastAPI Server & URLs

Run the single-process server command from the `studytrack` directory:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 5500 --reload
```

* **Dashboard URL**: `http://localhost:5500`
* **API Documentation (Swagger UI)**: `http://localhost:5500/docs`

---

## 11–12. Exact API Endpoints List & Samples

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/students/` | Create student record (Status 201) |
| `GET` | `/students/` | List students (optional `min_age` filter) |
| `GET` | `/students/sorted` | Sort DB roster in-place (`by=age` or `by=name`) |
| `GET` | `/students/search` | Binary search student by name (`name=Priya Iyer`) |
| `GET` | `/students/report` | Generate roster report (`min_age=21`) |
| `GET` | `/students/{student_id}` | Get student by ID |
| `PATCH` | `/students/{student_id}` | Partial update student record |
| `DELETE` | `/students/{student_id}` | Delete student record |
| `GET` | `/students/{student_id}/course-count` | SQL aggregate course count |
| `POST` | `/courses/` | Enroll student into course (Status 201) |
| `GET` | `/courses/` | List all courses |
| `GET` | `/courses/{course_id}` | Get course by ID |
| `PATCH` | `/courses/{course_id}` | Update course record |
| `DELETE` | `/courses/{course_id}` | Delete course record |
| `POST` | `/assistant/summarize` | Offline AI study notes summarizer |
| `GET` | `/assistant/search` | Offline AI semantic note search |

---

## 13–19. How to Use Features

### 13. Student CRUD
* **Add Student**: Submit form with Name, Email (containing `@`), and Age (`> 0`). Returns 201 CREATED.
* **Edit Age**: Change age input on card and click "Save Age" (`PATCH /students/{id}`).
* **Delete Student**: Click "Delete" (`DELETE /students/{id}`).

### 14. Course CRUD
* Submit Student ID, Course Name, and Credits (1–6). Returns 201 CREATED.

### 15. Sorting
* Click "Sort by Age" or "Sort by Name" on the Algorithms panel to trigger `/students/sorted?by=...`.

### 16. Binary Search
* Enter exact student name (e.g. `Priya Iyer`) to execute `/students/search?name=Priya%20Iyer`.

### 17. Roster Report
* Enter minimum age threshold to calculate accumulator match count and view report strings.

### 18. AI Summarizer
* Type study notes into the textarea and click "Summarize Notes".

### 19. Semantic Search
* Enter query text (e.g. `binary search algorithm`) and click "Search Notes" to view ranked similarity scores.

---

## 20–25. AI Assistant Offline Implementation Details

### 20. Offline Mock Mode
All AI features operate completely offline without external network calls, paid APIs, or secret API keys.

### 21. Topic Derivation Rule
* Non-empty text: First non-empty line after trimming whitespace.
* Empty/whitespace-only text: `"untitled"`.

### 22. Difficulty Thresholds
Word count calculated via whitespace splitting:
* `< 40 words` → `easy`
* `40–100 words` → `medium`
* `> 100 words` → `hard`
* Empty input → `easy`

### 23. Mock Embedding
Generates a 12-dimensional vector over the exact vocabulary:
`["sort", "search", "binary", "insertion", "sql", "join", "fastapi", "pydantic", "prompt", "llm", "database", "validate"]`.
Tokens are lowercased and split on non-alphanumeric characters `[^a-z0-9]+`. Counts exact whole-token matches (no stemming; `"sorted"` does not match `"sort"`, while `"LLM's"` tokenizes as `"llm"` and `"s"`).

### 24. Cosine Similarity Formula
$$\text{Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|} = \frac{\sum_{i=1}^{12} A_i B_i}{\sqrt{\sum_{i=1}^{12} A_i^2} \sqrt{\sum_{i=1}^{12} B_i^2}}$$

### 25. Zero-Vector Handling
If vector magnitude is zero ($0.0$), the function returns `0.0` immediately without raising a `ZeroDivisionError`. If query produces a zero vector, notes retain their original ID order.

---

## 26–28. Frontend Technical Decisions

### 26. Event Delegation
A single event listener is attached to `#roster-list`. Clicks are inspected using `event.target` to determine if `save-age-btn` or `delete-btn` was pressed. This avoids attaching hundreds of individual listeners and prevents memory leaks when cards are dynamically added or removed.

### 27. Dynamic Element Creation (`document.createElement()`)
Cards are constructed programmatically via `document.createElement()`, setting attributes and text content safely. `innerHTML` string interpolation is avoided for list building to prevent XSS vulnerabilities, preserve existing event bindings, and avoid unnecessary full-page DOM reflows.

### 28. SQL Aggregate Course Count
Course count is calculated using SQLAlchemy's `func.count(Course.id)` aggregate directly in SQL. This ensures efficient $O(1)$ database execution without fetching all course records into Python memory.

---

## 31–33. Algorithmic Complexity & Analysis

### 32. Insertion Sort Complexity (4–8 Sentence Explanation)
Insertion Sort operates by dividing the array into a sorted and an unsorted region. For each element in the unsorted region, it performs an inner `while` loop to shift larger elements to the right until finding the correct insertion position. In the worst-case scenario (an array sorted in reverse order), every new element must be compared and shifted past all previously sorted elements, resulting in $\frac{n(n-1)}{2}$ comparisons and shifts, which yields a time complexity of $O(n^2)$. In the best-case scenario (an already sorted array), the inner loop condition fails immediately on the first comparison, executing in $O(n)$ time. Insertion Sort is an in-place sorting algorithm requiring only $O(1)$ auxiliary memory. It is highly efficient for small datasets or nearly sorted arrays.

### 33. Why Binary Search Requires Sorted Data
Binary Search operates by repeatedly comparing the target value with the midpoint element of an array and discarding half of the remaining search space based on the comparison result. This elimination strategy fundamentally relies on the monotonic ordering property of sorted data: if the target is less than the midpoint value, it is guaranteed to lie in the left sub-array. If the array is unsorted, this guarantee breaks down completely, as elements can appear anywhere, leading to incorrect search results.

---

## 34–35. Mode & Grading Notice

* **No Real API Key Required**: No external LLM keys or secrets are required or used.
* **Offline Mock Mode**: Grading and demonstration rely entirely on the offline deterministic AI engine.

---

## 36. End-to-End Walkthrough

1. **Open Dashboard**: Navigate to `http://localhost:5500`.
2. **Seeded Roster Appears**: The 8 initial seeded students (Aditi Rao, Rohan Mehta, Kavya Nair, etc.) render automatically.
3. **Edit Age**: On Aditi Rao's card, change age input from `22` to `23` and click **Save Age**. The displayed age updates instantly without page reload via `PATCH /students/1`.
4. **Add Student**: Enter `Nikhil Sharma`, `nikhil@example.com`, `24` in `#student-form` and submit. A new card appears dynamically via `document.createElement()`.
5. **Delete Student**: Click **Delete** on Rohan Mehta's card. The card is removed from the DOM via `DELETE /students/2`.
6. **Use Sorting**: Click **Sort by Age** under Algorithms Engine to see roster ordered from youngest (Farhan Sheikh — 18) to oldest.
7. **Use Search**: Enter `Priya Iyer` in Binary Search to retrieve record at index 5.
8. **Use Report**: Click **Generate Report** for `min_age=21` to view formatted summary and match count (5).
9. **Summarize Notes**: Type notes into AI Helper textarea and click **Summarize Notes** to inspect extracted topic, key points, and difficulty.
10. **Search Notes**: Click **Search Notes** for query `binary search algorithm` to confirm note ID 1 is ranked first with highest cosine similarity.

---

## Appendix: Theoretical Real-LLM Prompt

For production environments using a live LLM API (e.g. OpenAI GPT-4 or Google Gemini), the following system prompt would produce the exact required JSON structure:

```text
You are an expert academic note summarizer.
Analyze the user's raw study notes and output ONLY a valid JSON object with no Markdown formatting, extra text, or explanation.

JSON Schema:
{
  "topic": "String (First main concept or title)",
  "key_points": ["Up to 3 concise summary sentences"],
  "difficulty": "easy | medium | hard"
}

Rules:
1. "topic": Extract the primary subject line from the first line of text.
2. "key_points": Provide 1 to 3 key bullet sentences summarizing core concepts.
3. "difficulty": Classify as "easy" (<40 words), "medium" (40-100 words), or "hard" (>100 words).
```
