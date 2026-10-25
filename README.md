# Student Result Verification System
### BSc IT Software Testing Laboratory Mini-Project

A complete, production-grade mini project built with **Python Flask**, **HTML5/CSS3/Vanilla JavaScript**, **pytest**, and **Selenium WebDriver**.

Developed specifically to demonstrate **Software Testing Techniques** including **Boundary Value Analysis (BVA)**, **Equivalence Class Partitioning (ECP)**, **Automated Unit & Integration Testing**, and **Browser Automation**.

---

## 🌟 Key Features

1. **Modern Navy-Blue & White Dashboard**: Clean responsive UI with metric cards, instant calculation preview, and verified results table.
2. **Subject Mark Verification**: Validates 5 BSc IT subjects (Software Engineering, Python Programming, Database Management, Web Technologies, Software Testing & QA).
3. **Rigorous Validation**:
   - Required name and roll number check.
   - Marks constrained strictly to the range `0.0` to `100.0`.
   - Real-time instant validation as you type.
4. **Calculations**:
   - **Total Marks**: Sum of 5 subjects (out of 500).
   - **Percentage**: `(Total / 500) * 100`.
   - **Passing Rule**: Default passing threshold is **35/100**. A student passes **only if EVERY subject is ≥ 35.0**. If even one subject is `< 35`, status is **Fail**.
   - **Academic Grade**: Computes `A+`, `A`, `B+`, `B`, `C`, `D`, or `F`.
5. **Interactive Testing Presets**: Quick-fill buttons for standard pass, exact boundary (35), failure edge case (one subject 34), and topper.
6. **Real-Time Testing Dashboard (`/testing`)**:
   - Live automated test execution button that runs real `pytest` on the server without fabricated numbers.
   - BVA & ECP reference tables and test case matrix.
7. **CSV Export**: Export verified student ledger directly to CSV.
8. **Zero Database Configuration**: Lightweight JSON file storage (`data/results.json`) that persists data across restarts without setting up MySQL or SQLite.

---

## 📁 Project Structure

```
StudentResultVerification/
├── app.py                     # Flask application routes, REST API & test runner
├── calculator.py              # Pure calculation & validation engine (ECP/BVA logic)
├── storage.py                 # File-based JSON persistence & statistics engine
├── requirements.txt           # Project dependencies (Flask, pytest, selenium)
├── README.md                  # Comprehensive documentation & lab guide
├── data/
│   └── results.json           # Stored student records (sample data included)
├── static/
│   ├── css/
│   │   └── style.css          # Navy-blue & white responsive design
│   └── js/
│       ├── main.js            # Live validation, calculation preview, AJAX
│       └── testing.js         # Real pytest runner client for Testing Dashboard
├── templates/
│   ├── base.html              # Common navbar, footer & toast containers
│   ├── index.html             # Student Result Verification Dashboard
│   └── testing.html           # Software Testing Laboratory Dashboard
└── tests/
    ├── __init__.py
    ├── test_calculator.py     # 59 automated unit tests (BVA, ECP, Formulas)
    ├── test_app.py            # 9 Flask integration and REST API tests
    └── test_selenium.py       # End-to-end browser automation test
```

---

## 🚀 How to Run on Windows (Step-by-Step)

### Step 1: Open PowerShell or Command Prompt
Navigate to the project folder:
```powershell
cd C:\Users\hemna\OneDrive\Desktop\StudentResultVerification
```

### Step 2: Install Dependencies
Run:
```powershell
python -m pip install -r requirements.txt
```
*(Dependencies: Flask, pytest, selenium)*

### Step 3: Run Automated Unit Tests (pytest)
To execute all 69 automated tests (unit, integration, and browser):
```powershell
python -m pytest -v
```

To run only the Boundary Value Analysis tests:
```powershell
python -m pytest -v tests/test_calculator.py -k "Boundary"
```

To run only Pass/Fail business logic tests:
```powershell
python -m pytest -v tests/test_calculator.py -k "PassFail"
```

### Step 4: Start the Flask Web Application
Run:
```powershell
python app.py
```

Open your browser and visit:
- **Student Dashboard**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Testing Dashboard**: [http://127.0.0.1:5000/testing](http://127.0.0.1:5000/testing)

### Step 5: Run Selenium Browser Automation Test
Make sure Google Chrome or Microsoft Edge is installed, then run:
```powershell
python tests/test_selenium.py
```
*(This automatically opens the browser, fills student data, tests the live calculations, verifies form submission, and checks the ledger table).*

---

## 🧪 Software Testing Concepts Demonstrated

### 1. Boundary Value Analysis (BVA)
Marks domain is `[0.0, 100.0]` with passing threshold `35.0`:
| Boundary | Test Value | Expected Outcome |
| :--- | :--- | :--- |
| **Below Min** | `-0.01` | Rejection: Below minimum 0.0 |
| **Min Boundary** | `0.0` | Accepted: Mark = 0.0 |
| **Just Below Passing** | `34.99` | Accepted: Subject Status = FAIL |
| **Passing Boundary** | `35.0` | Accepted: Subject Status = PASS |
| **Near Max** | `99.99` | Accepted: Distinction mark |
| **Max Boundary** | `100.0` | Accepted: Full marks |
| **Above Max** | `100.01` | Rejection: Exceeds maximum 100.0 |

### 2. Equivalence Class Partitioning (ECP)
- **Valid Classes**: Numbers between 0 and 100 (e.g. `75`, `88.5`, `92`).
- **Invalid Class 1**: Negative numbers (`< 0`).
- **Invalid Class 2**: Excessive numbers (`> 100`).
- **Invalid Class 3**: Non-numeric strings (`"abc"`, `"!@#"`, `"None"`).
- **Invalid Class 4**: Empty or whitespace fields (`""`, `"   "`).

### 3. Critical Business Rule Verification
- **Rule**: If a student scores `100` in 4 subjects, but `34` in the 5th subject:
  - Total = `434 / 500` (86.8%)
  - **Status**: **FAIL**
  - **Grade**: **F**
- This rule is verified by test `test_student_fails_when_single_subject_below_35`.

---

## 🎓 Viva Questions & Answers for Your Lab Exam

**Q1: Why did you separate `calculator.py` from `app.py`?**
> *Answer*: Separation of Concerns. It isolates pure business logic from the web framework, allowing clean, fast, deterministic unit testing without needing HTTP mocks or database dependencies.

**Q2: What is Boundary Value Analysis and how did you implement it?**
> *Answer*: BVA is a black-box testing technique focusing on inputs at the boundaries of equivalence partitions where bugs commonly occur. We tested values like `0`, `-0.01`, `34.99`, `35.0`, `100.0`, and `100.01`.

**Q3: How does the Testing Dashboard work without fabricating results?**
> *Answer*: When the user clicks "Run Automated Tests Now", the Flask backend executes `python -m pytest` as a subprocess, collects the actual output stream and exit code, and sends genuine real-time test outcomes to the frontend.
