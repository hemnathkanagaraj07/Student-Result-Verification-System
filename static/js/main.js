/**
 * Student Result Verification System - Frontend Logic
 * BSc IT Software Testing Laboratory
 */

document.addEventListener("DOMContentLoaded", () => {
    initFormLiveCalculations();
    initFormSubmission();
    initTableFilters();
    initCsvExport();
    initResetButton();
});

const SUBJECT_KEYS = ["sub1", "sub2", "sub3", "sub4", "sub5"];
const PASSING_MARK = 35.0;

/**
 * Attaches real-time validation and calculation listeners to form inputs.
 */
function initFormLiveCalculations() {
    const markInputs = document.querySelectorAll(".mark-input");
    const nameInput = document.getElementById("name");
    const rollInput = document.getElementById("roll_no");

    markInputs.forEach(input => {
        input.addEventListener("input", () => {
            validateSingleMarkInput(input);
            updateLivePreview();
        });
        input.addEventListener("blur", () => {
            validateSingleMarkInput(input);
        });
    });

    if (nameInput) {
        nameInput.addEventListener("input", () => {
            const val = nameInput.value.trim();
            const feedback = document.getElementById("feedback-name");
            if (val.length === 0) {
                nameInput.classList.remove("is-valid");
                nameInput.classList.add("is-invalid");
                feedback.textContent = "Student Name is required.";
                feedback.className = "field-feedback error";
            } else if (val.length < 2) {
                nameInput.classList.remove("is-valid");
                nameInput.classList.add("is-invalid");
                feedback.textContent = "Must be at least 2 characters.";
                feedback.className = "field-feedback error";
            } else {
                nameInput.classList.remove("is-invalid");
                nameInput.classList.add("is-valid");
                feedback.textContent = "";
                feedback.className = "field-feedback";
            }
        });
    }

    if (rollInput) {
        rollInput.addEventListener("input", () => {
            const val = rollInput.value.trim();
            const feedback = document.getElementById("feedback-roll_no");
            if (val.length === 0) {
                rollInput.classList.remove("is-valid");
                rollInput.classList.add("is-invalid");
                feedback.textContent = "Roll Number is required.";
                feedback.className = "field-feedback error";
            } else {
                rollInput.classList.remove("is-invalid");
                rollInput.classList.add("is-valid");
                feedback.textContent = "";
                feedback.className = "field-feedback";
            }
        });
    }
}

/**
 * Validates a single mark input against [0, 100] and updates its badge.
 */
function validateSingleMarkInput(input) {
    const valStr = input.value.trim();
    const key = input.id;
    const pill = document.getElementById(`pill-${key}`);

    if (valStr === "") {
        input.classList.remove("is-valid", "is-invalid");
        if (pill) {
            pill.textContent = "Pending";
            pill.className = "mark-status-pill";
        }
        return false;
    }

    const num = parseFloat(valStr);
    if (isNaN(num) || num < 0 || num > 100) {
        input.classList.remove("is-valid");
        input.classList.add("is-invalid");
        if (pill) {
            pill.textContent = num < 0 ? "< 0" : (num > 100 ? "> 100" : "Invalid");
            pill.className = "mark-status-pill invalid";
        }
        return false;
    }

    input.classList.remove("is-invalid");
    input.classList.add("is-valid");

    if (pill) {
        if (num >= PASSING_MARK) {
            pill.textContent = "Pass";
            pill.className = "mark-status-pill pass";
        } else {
            pill.textContent = "Fail";
            pill.className = "mark-status-pill fail";
        }
    }
    return true;
}

/**
 * Computes live total, percentage, pass/fail status, and projected grade.
 */
function updateLivePreview() {
    let total = 0;
    let filledCount = 0;
    let hasFailSubject = false;
    let hasInvalid = false;

    SUBJECT_KEYS.forEach(k => {
        const input = document.getElementById(k);
        if (!input) return;
        const valStr = input.value.trim();
        if (valStr !== "") {
            const num = parseFloat(valStr);
            if (isNaN(num) || num < 0 || num > 100) {
                hasInvalid = true;
            } else {
                total += num;
                filledCount++;
                if (num < PASSING_MARK) {
                    hasFailSubject = true;
                }
            }
        }
    });

    const totalEl = document.getElementById("preview-total");
    const pctEl = document.getElementById("preview-percentage");
    const statusTextEl = document.getElementById("preview-status-text");
    const statusBadgeEl = document.getElementById("preview-status-badge");
    const gradeEl = document.getElementById("preview-grade");
    const noteEl = document.getElementById("preview-note");

    if (hasInvalid) {
        totalEl.textContent = "Error";
        pctEl.textContent = "Error";
        statusTextEl.textContent = "Invalid Marks";
        gradeEl.textContent = "—";
        statusBadgeEl.textContent = "Invalid Input";
        statusBadgeEl.className = "badge badge-danger";
        noteEl.textContent = "Marks must be between 0 and 100.";
        return;
    }

    if (filledCount === 0) {
        totalEl.textContent = "— / 500";
        pctEl.textContent = "— %";
        statusTextEl.textContent = "—";
        gradeEl.textContent = "—";
        statusBadgeEl.textContent = "Enter Marks";
        statusBadgeEl.className = "badge badge-neutral";
        noteEl.textContent = "Fill in all five subject marks to calculate final status.";
        return;
    }

    const percentage = ((total / 500) * 100).toFixed(1);
    totalEl.textContent = `${total.toFixed(1)} / 500`;
    pctEl.textContent = `${percentage}%`;

    if (filledCount === 5) {
        if (hasFailSubject) {
            statusTextEl.textContent = "Fail";
            statusBadgeEl.textContent = "Status: FAIL";
            statusBadgeEl.className = "badge badge-danger";
            gradeEl.textContent = "F";
            noteEl.textContent = "Student fails because at least one subject mark is below 35.";
        } else {
            statusTextEl.textContent = "Pass";
            statusBadgeEl.textContent = "Status: PASS";
            statusBadgeEl.className = "badge badge-success";
            gradeEl.textContent = calculateGrade(parseFloat(percentage), "Pass");
            noteEl.textContent = "All subjects ≥ 35. Result eligible for verification.";
        }
    } else {
        statusTextEl.textContent = `${filledCount}/5 Subjects`;
        statusBadgeEl.textContent = "In Progress";
        statusBadgeEl.className = "badge badge-neutral";
        gradeEl.textContent = "—";
        noteEl.textContent = `Completed ${filledCount} of 5 subjects.`;
    }
}

function calculateGrade(pct, status) {
    if (status === "Fail") return "F";
    if (pct >= 90) return "A+";
    if (pct >= 80) return "A";
    if (pct >= 70) return "B+";
    if (pct >= 60) return "B";
    if (pct >= 50) return "C";
    if (pct >= 35) return "D";
    return "F";
}

/**
 * Handles Form Submission via AJAX for instant user feedback.
 */
function initFormSubmission() {
    const form = document.getElementById("student-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const errorBox = document.getElementById("form-error-box");
        const errorList = document.getElementById("form-error-list");
        errorBox.style.display = "none";
        errorList.innerHTML = "";

        const name = document.getElementById("name").value.trim();
        const roll_no = document.getElementById("roll_no").value.trim();
        const marks = {};
        SUBJECT_KEYS.forEach(k => {
            marks[k] = document.getElementById(k).value.trim();
        });

        const payload = { name, roll_no, marks };

        const submitBtn = document.getElementById("btn-submit-form");
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = "Verifying...";

        try {
            const res = await fetch("/api/results", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (!res.ok || !data.success) {
                // Show errors
                errorBox.style.display = "block";
                const errs = data.errors || [data.message || "Validation failed."];
                errs.forEach(err => {
                    const li = document.createElement("li");
                    li.textContent = err;
                    errorList.appendChild(li);
                });
                showToast(data.message || "Please fix validation errors.", "error");
                return;
            }

            // Success
            showToast(data.message, "success");
            upsertTableRow(data.data);
            updateStatsView(data.stats);
            resetForm();

        } catch (err) {
            showToast("Server connection error: " + err.message, "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
}

/**
 * Inserts or updates row in the result table smoothly.
 */
function upsertTableRow(rec) {
    const tbody = document.getElementById("results-tbody");
    const emptyRow = document.getElementById("empty-row");
    if (emptyRow) emptyRow.remove();

    const existingRow = document.getElementById(`row-${rec.roll_no}`);
    const rowHtml = `
        <td class="font-mono font-bold text-navy">${rec.roll_no}</td>
        <td class="font-medium">${rec.name}</td>
        <td class="mark-cell ${rec.marks.sub1 < 35 ? 'mark-fail' : ''}">${rec.marks.sub1}</td>
        <td class="mark-cell ${rec.marks.sub2 < 35 ? 'mark-fail' : ''}">${rec.marks.sub2}</td>
        <td class="mark-cell ${rec.marks.sub3 < 35 ? 'mark-fail' : ''}">${rec.marks.sub3}</td>
        <td class="mark-cell ${rec.marks.sub4 < 35 ? 'mark-fail' : ''}">${rec.marks.sub4}</td>
        <td class="mark-cell ${rec.marks.sub5 < 35 ? 'mark-fail' : ''}">${rec.marks.sub5}</td>
        <td class="font-semibold">${rec.total}</td>
        <td class="font-semibold">${rec.percentage}%</td>
        <td>
            <span class="badge ${rec.status === 'Pass' ? 'badge-success' : 'badge-danger'}">
                ${rec.status.toUpperCase()}
            </span>
        </td>
        <td>
            <span class="grade-pill grade-${rec.grade}">${rec.grade}</span>
        </td>
        <td class="text-right">
            <button class="btn-icon text-danger" title="Delete Student" onclick="deleteStudentRecord('${rec.roll_no}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
            </button>
        </td>
    `;

    if (existingRow) {
        existingRow.innerHTML = rowHtml;
        existingRow.dataset.roll = rec.roll_no;
        existingRow.dataset.name = rec.name;
        existingRow.dataset.status = rec.status;
    } else {
        const tr = document.createElement("tr");
        tr.id = `row-${rec.roll_no}`;
        tr.dataset.roll = rec.roll_no;
        tr.dataset.name = rec.name;
        tr.dataset.status = rec.status;
        tr.innerHTML = rowHtml;
        tbody.prepend(tr);
    }

    updateShowingCount();
}

/**
 * Updates Dashboard Stats cards.
 */
function updateStatsView(stats) {
    if (!stats) return;
    const totalEl = document.getElementById("stat-total");
    const passedEl = document.getElementById("stat-passed");
    const passPctEl = document.getElementById("stat-pass-pct");
    const failedEl = document.getElementById("stat-failed");
    const avgEl = document.getElementById("stat-avg");
    const topperPctEl = document.getElementById("stat-topper-pct");
    const topperNameEl = document.getElementById("stat-topper-name");

    if (totalEl) totalEl.textContent = stats.total_students;
    if (passedEl) passedEl.textContent = stats.passed_count;
    if (passPctEl) passPctEl.textContent = `${stats.pass_percentage}%`;
    if (failedEl) failedEl.textContent = stats.failed_count;
    if (avgEl) avgEl.textContent = `${stats.class_average}%`;

    if (topperPctEl && topperNameEl) {
        if (stats.highest_score) {
            topperPctEl.textContent = `${stats.highest_score.percentage}%`;
            topperNameEl.textContent = `${stats.highest_score.name} (${stats.highest_score.roll_no})`;
        } else {
            topperPctEl.textContent = "N/A";
            topperNameEl.textContent = "No data";
        }
    }
}

/**
 * Filter & Search on results table.
 */
function initTableFilters() {
    const searchInput = document.getElementById("table-search");
    const filterSelect = document.getElementById("status-filter");

    function applyFilter() {
        const query = (searchInput ? searchInput.value : "").trim().toLowerCase();
        const filter = filterSelect ? filterSelect.value : "ALL";

        const rows = document.querySelectorAll("#results-tbody tr:not(#empty-row)");
        let visibleCount = 0;

        rows.forEach(r => {
            const roll = (r.dataset.roll || "").toLowerCase();
            const name = (r.dataset.name || "").toLowerCase();
            const status = r.dataset.status || "";

            const matchesQuery = roll.includes(query) || name.includes(query);
            const matchesFilter = (filter === "ALL") || (status === filter);

            if (matchesQuery && matchesFilter) {
                r.style.display = "";
                visibleCount++;
            } else {
                r.style.display = "none";
            }
        });

        const showingCountEl = document.getElementById("showing-count");
        if (showingCountEl) showingCountEl.textContent = visibleCount;
    }

    if (searchInput) searchInput.addEventListener("input", applyFilter);
    if (filterSelect) filterSelect.addEventListener("change", applyFilter);
}

function updateShowingCount() {
    const visible = document.querySelectorAll("#results-tbody tr:not(#empty-row):not([style*='display: none'])");
    const showingCountEl = document.getElementById("showing-count");
    if (showingCountEl) showingCountEl.textContent = visible.length;
}

/**
 * Deletes student record with modal confirmation.
 */
let pendingDeleteRoll = null;

function deleteStudentRecord(rollNo) {
    pendingDeleteRoll = rollNo;
    const modal = document.getElementById("delete-modal");
    const modalRoll = document.getElementById("delete-student-roll");
    if (modalRoll) modalRoll.textContent = rollNo;
    if (modal) modal.style.display = "flex";

    const confirmBtn = document.getElementById("btn-confirm-delete");
    if (confirmBtn) {
        confirmBtn.onclick = async () => {
            if (!pendingDeleteRoll) return;
            try {
                const res = await fetch(`/api/results/${encodeURIComponent(pendingDeleteRoll)}`, {
                    method: "DELETE"
                });
                const data = await res.json();
                if (data.success) {
                    showToast(data.message, "success");
                    const row = document.getElementById(`row-${pendingDeleteRoll}`);
                    if (row) row.remove();
                    updateStatsView(data.stats);
                    updateShowingCount();
                } else {
                    showToast(data.message, "error");
                }
            } catch (e) {
                showToast("Failed to delete record: " + e.message, "error");
            } finally {
                closeDeleteModal();
            }
        };
    }
}

function closeDeleteModal() {
    const modal = document.getElementById("delete-modal");
    if (modal) modal.style.display = "none";
    pendingDeleteRoll = null;
}

/**
 * Preset data fill helper for laboratory demonstrations.
 */
function fillSampleData(type) {
    const nameEl = document.getElementById("name");
    const rollEl = document.getElementById("roll_no");

    const presets = {
        valid: {
            name: "Ananya Joshi",
            roll_no: "IT2026-050",
            marks: { sub1: 78, sub2: 85, sub3: 72, sub4: 80, sub5: 88 }
        },
        boundary: {
            name: "Vikas Patil",
            roll_no: "IT2026-051",
            marks: { sub1: 35, sub2: 35, sub3: 35, sub4: 35, sub5: 35 }
        },
        fail_one: {
            name: "Deepak Rawat",
            roll_no: "IT2026-052",
            marks: { sub1: 90, sub2: 95, sub3: 34, sub4: 88, sub5: 92 }
        },
        topper: {
            name: "Tanvi Mehta",
            roll_no: "IT2026-053",
            marks: { sub1: 96, sub2: 98, sub3: 94, sub4: 95, sub5: 97 }
        }
    };

    const data = presets[type];
    if (!data) return;

    if (nameEl) nameEl.value = data.name;
    if (rollEl) rollEl.value = data.roll_no;

    SUBJECT_KEYS.forEach(k => {
        const input = document.getElementById(k);
        if (input) {
            input.value = data.marks[k];
            validateSingleMarkInput(input);
        }
    });

    updateLivePreview();
}

/**
 * Resets the form to blank state.
 */
function resetForm() {
    const form = document.getElementById("student-form");
    if (form) form.reset();

    const feedbacks = document.querySelectorAll(".field-feedback");
    feedbacks.forEach(f => {
        f.textContent = "";
        f.className = "field-feedback";
    });

    const inputs = document.querySelectorAll(".form-control");
    inputs.forEach(i => i.classList.remove("is-valid", "is-invalid"));

    const pills = document.querySelectorAll(".mark-status-pill");
    pills.forEach(p => {
        p.textContent = "Pending";
        p.className = "mark-status-pill";
    });

    const errorBox = document.getElementById("form-error-box");
    if (errorBox) errorBox.style.display = "none";

    updateLivePreview();
}

/**
 * Export results table to CSV.
 */
function initCsvExport() {
    const exportBtn = document.getElementById("btn-export-csv");
    if (!exportBtn) return;

    exportBtn.addEventListener("click", () => {
        const rows = document.querySelectorAll("#results-tbody tr:not(#empty-row)");
        if (rows.length === 0) {
            showToast("No student records to export.", "error");
            return;
        }

        const headers = ["Roll Number", "Student Name", "SE", "PP", "DBMS", "WT", "STQA", "Total", "Percentage", "Status", "Grade"];
        const csvRows = [headers.join(",")];

        rows.forEach(r => {
            const cells = r.querySelectorAll("td");
            if (cells.length < 11) return;
            const rowData = [
                `"${cells[0].innerText.trim()}"`,
                `"${cells[1].innerText.trim()}"`,
                cells[2].innerText.trim(),
                cells[3].innerText.trim(),
                cells[4].innerText.trim(),
                cells[5].innerText.trim(),
                cells[6].innerText.trim(),
                cells[7].innerText.trim(),
                cells[8].innerText.trim().replace("%", ""),
                cells[9].innerText.trim(),
                cells[10].innerText.trim()
            ];
            csvRows.push(rowData.join(","));
        });

        const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Student_Results_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        showToast("CSV exported successfully!", "success");
    });
}

/**
 * Reset to default sample students.
 */
function initResetButton() {
    const btn = document.getElementById("btn-reset-data");
    if (!btn) return;

    btn.addEventListener("click", async () => {
        if (!confirm("Reset all student records to default laboratory sample dataset?")) return;
        try {
            const res = await fetch("/api/results/reset", { method: "POST" });
            const data = await res.json();
            if (data.success) {
                showToast(data.message, "success");
                setTimeout(() => window.location.reload(), 600);
            }
        } catch (e) {
            showToast("Failed to reset dataset: " + e.message, "error");
        }
    });
}

/**
 * Toast notifications.
 */
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${type === 'success' ? '✓' : '!'}</div>
        <div class="toast-msg">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
