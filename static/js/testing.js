/**
 * Software Testing Laboratory Dashboard - Real-time Pytest Test Runner
 * Communicates with backend /api/run-tests and /api/test-results.
 * Does NOT fabricate results. Parses real pytest outcomes.
 */

let currentTestList = [];
let activeFilter = "all";

document.addEventListener("DOMContentLoaded", () => {
    // Automatically load last execution results if available
    loadInitialTestResults();

    const runBtn = document.getElementById("btn-run-tests");
    if (runBtn) {
        runBtn.addEventListener("click", () => triggerTestExecution("all"));
    }
});

// Expose functions globally for HTML event handlers
window.triggerTestExecution = triggerTestExecution;
window.filterTestList = filterTestList;
window.toggleConsole = toggleConsole;

/**
 * Loads the latest stored test run on initial page load.
 */
async function loadInitialTestResults() {
    try {
        const res = await fetch("/api/test-results");
        const data = await res.json();
        if (data.success && data.has_results && data.data) {
            renderTestResultsUI(data.data);
        }
    } catch (e) {
        console.warn("Could not fetch cached test results:", e);
    }
}

/**
 * Executes pytest on server and updates UI with genuine results.
 * @param {string} suite - 'all' (default, 69 tests) | 'unit' (68 tests) | 'selenium' (1 test)
 */
async function triggerTestExecution(suite = "all") {
    const runBtn = document.getElementById("btn-run-tests");
    const unitBtn = document.getElementById("btn-run-unit");
    const loadingState = document.getElementById("test-loading-state");
    const loadingTitle = document.getElementById("loading-title");
    const loadingDesc = document.getElementById("loading-desc");
    const statusBadge = document.getElementById("test-status-badge");
    const successBanner = document.getElementById("test-success-banner");
    const errorBanner = document.getElementById("test-error-banner");
    const rawConsole = document.getElementById("pytest-raw-console");

    // UI in running state
    if (runBtn) {
        runBtn.disabled = true;
        runBtn.innerHTML = `
            <span class="spinner" style="width: 16px; height: 16px; border-width: 2px; margin-right: 8px;"></span>
            Executing Test Suite...
        `;
    }
    if (unitBtn) unitBtn.disabled = true;

    // Reset banners
    if (successBanner) successBanner.style.display = "none";
    if (errorBanner) errorBanner.style.display = "none";

    // Show loading state
    if (loadingState) {
        loadingState.style.display = "flex";
        if (suite === "unit") {
            loadingTitle.textContent = "Executing Fast Unit & Integration Tests (68 Tests)...";
            loadingDesc.textContent = "Running Boundary Value Analysis, Equivalence Partitioning, Total, Percentage, Pass/Fail logic, and API routes.";
        } else {
            loadingTitle.textContent = "Executing Complete Test Suite (69 Tests)...";
            loadingDesc.textContent = "Running 59 unit tests (BVA/ECP), 9 Flask integration tests, and 1 Selenium WebDriver browser automation test. Please wait...";
        }
    }

    if (statusBadge) {
        statusBadge.textContent = "Running Suite...";
        statusBadge.className = "badge badge-neutral";
    }

    try {
        const response = await fetch("/api/run-tests", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ suite })
        });

        const data = await response.json();

        if (loadingState) loadingState.style.display = "none";

        if (!response.ok || !data.success) {
            if (statusBadge) {
                statusBadge.textContent = "Execution Error";
                statusBadge.className = "badge badge-danger";
            }
            if (errorBanner) {
                errorBanner.style.display = "flex";
                document.getElementById("error-banner-msg").textContent = data.message || "Failed to execute test suite.";
            }
            if (rawConsole) {
                rawConsole.textContent = data.raw_output || data.message || "Error running pytest.";
            }
            return;
        }

        // Render received actual pytest results
        renderTestResultsUI(data);

    } catch (err) {
        if (loadingState) loadingState.style.display = "none";
        if (statusBadge) {
            statusBadge.textContent = "Network Error";
            statusBadge.className = "badge badge-danger";
        }
        if (errorBanner) {
            errorBanner.style.display = "flex";
            document.getElementById("error-banner-msg").textContent = "Could not communicate with Flask backend: " + err.message;
        }
        if (rawConsole) {
            rawConsole.textContent = "Network error: " + err.message;
        }
    } finally {
        if (runBtn) {
            runBtn.disabled = false;
            runBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                Run Complete Test Suite (69 Tests)
            `;
        }
        if (unitBtn) unitBtn.disabled = false;
    }
}

/**
 * Updates Dashboard UI components with actual pytest report data.
 * @param {object} data - Object containing actual pytest metrics and tests array
 */
function renderTestResultsUI(data) {
    const metricsGrid = document.getElementById("test-metrics-grid");
    const resultsContainer = document.getElementById("test-results-container");
    const statusBadge = document.getElementById("test-status-badge");
    const timestampEl = document.getElementById("test-timestamp");
    const successBanner = document.getElementById("test-success-banner");
    const errorBanner = document.getElementById("test-error-banner");
    const rawConsole = document.getElementById("pytest-raw-console");
    const summaryPill = document.getElementById("test-summary-pill");

    if (metricsGrid) metricsGrid.style.display = "grid";
    if (resultsContainer) resultsContainer.style.display = "block";

    // Update real metrics
    document.getElementById("total-tests-run").textContent = data.total ?? data.tests?.length ?? 0;
    document.getElementById("passed-tests-count").textContent = data.passed_count ?? 0;
    document.getElementById("failed-tests-count").textContent = data.failed_count ?? 0;
    document.getElementById("skipped-tests-count").textContent = data.skipped_count ?? 0;
    document.getElementById("tests-duration").textContent = `${data.elapsed_seconds ?? 0.0}s`;

    if (timestampEl && data.timestamp) {
        timestampEl.textContent = `Last Run: ${data.timestamp}`;
    }

    // Determine suite outcome
    const isSuccess = data.passed && (data.failed_count === 0) && (data.error_count === 0);

    if (isSuccess) {
        if (statusBadge) {
            statusBadge.textContent = `All ${data.passed_count} Passed ✓`;
            statusBadge.className = "badge badge-success";
        }
        if (successBanner) {
            successBanner.style.display = "flex";
            const successMsg = document.getElementById("success-banner-msg");
            if (successMsg) {
                successMsg.textContent = `All ${data.total} tests executed cleanly with 0 failures in ${data.elapsed_seconds}s. Boundary Value Analysis, Equivalence Partitioning, and Selenium automated verification all satisfied.`;
            }
        }
        if (errorBanner) errorBanner.style.display = "none";
    } else {
        if (statusBadge) {
            statusBadge.textContent = `${data.failed_count} Failed ✗`;
            statusBadge.className = "badge badge-danger";
        }
        if (errorBanner) {
            errorBanner.style.display = "flex";
            const errorMsg = document.getElementById("error-banner-msg");
            if (errorMsg) {
                errorMsg.textContent = `${data.failed_count} of ${data.total} tests failed. Examine individual test details below.`;
            }
        }
        if (successBanner) successBanner.style.display = "none";
    }

    // Summary pill
    if (summaryPill) {
        summaryPill.textContent = data.summary || `${data.passed_count} passed in ${data.elapsed_seconds}s`;
    }

    // Raw console output
    if (rawConsole && data.raw_output) {
        rawConsole.textContent = data.raw_output;
    }

    // Store tests and populate interactive test list
    currentTestList = data.tests || [];
    updateChipCounts();
    filterTestList(activeFilter);
}

/**
 * Counts tests by status and updates chip counters.
 */
function updateChipCounts() {
    const total = currentTestList.length;
    const passed = currentTestList.filter(t => t.status === "PASSED").length;
    const failed = currentTestList.filter(t => t.status === "FAILED" || t.status === "ERROR").length;
    const skipped = currentTestList.filter(t => t.status === "SKIPPED").length;

    const allEl = document.getElementById("chip-all-count");
    const passedEl = document.getElementById("chip-passed-count");
    const failedEl = document.getElementById("chip-failed-count");
    const skippedEl = document.getElementById("chip-skipped-count");

    if (allEl) allEl.textContent = total;
    if (passedEl) passedEl.textContent = passed;
    if (failedEl) failedEl.textContent = failed;
    if (skippedEl) skippedEl.textContent = skipped;
}

/**
 * Filters the displayed list of test cases by category and search keyword.
 * @param {string} [filterType] - 'all' | 'passed' | 'failed' | 'skipped'
 */
function filterTestList(filterType) {
    if (filterType) {
        activeFilter = filterType;
        document.querySelectorAll(".filter-chip").forEach(chip => {
            if (chip.dataset.filter === filterType) {
                chip.classList.add("active");
            } else {
                chip.classList.remove("active");
            }
        });
    }

    const searchInput = document.getElementById("test-search-input");
    const query = (searchInput ? searchInput.value : "").trim().toLowerCase();

    const filtered = currentTestList.filter(item => {
        // Status filter
        let matchesStatus = true;
        if (activeFilter === "passed") {
            matchesStatus = item.status === "PASSED";
        } else if (activeFilter === "failed") {
            matchesStatus = item.status === "FAILED" || item.status === "ERROR";
        } else if (activeFilter === "skipped") {
            matchesStatus = item.status === "SKIPPED";
        }

        // Search filter
        let matchesQuery = true;
        if (query) {
            const combinedText = `${item.file} ${item.class_name} ${item.name}`.toLowerCase();
            matchesQuery = combinedText.includes(query);
        }

        return matchesStatus && matchesQuery;
    });

    renderTestItems(filtered);
}

/**
 * Renders test items into the container.
 * @param {Array} items - Filtered test case array
 */
function renderTestItems(items) {
    const listEl = document.getElementById("test-case-items");
    if (!listEl) return;

    if (items.length === 0) {
        listEl.innerHTML = `
            <div class="empty-state" style="padding: 2rem; text-align: center; color: #64748b;">
                No test cases match the selected filter.
            </div>
        `;
        return;
    }

    listEl.innerHTML = items.map(t => {
        const statusClass = t.status.toLowerCase();
        const durationText = t.duration ? `${t.duration}s` : "";
        const classBadge = t.class_name ? `<span class="test-class-tag">${escapeHtml(t.class_name)} » </span>` : "";

        return `
            <div class="test-case-item ${t.status === 'FAILED' ? 'item-failed' : ''}">
                <div class="test-info">
                    <span class="test-file-tag">${escapeHtml(t.file)}</span>
                    <span class="test-name">
                        ${classBadge}<strong>${escapeHtml(t.name)}</strong>
                    </span>
                </div>
                <div class="test-meta">
                    ${durationText ? `<span class="test-duration">${durationText}</span>` : ""}
                    <span class="test-badge ${statusClass}">${escapeHtml(t.status)}</span>
                </div>
                ${t.message ? `<div class="test-error-details"><pre>${escapeHtml(t.message)}</pre></div>` : ""}
            </div>
        `;
    }).join("");
}

/**
 * Toggles visibility of raw terminal trace.
 */
function toggleConsole() {
    const consoleEl = document.getElementById("pytest-raw-console");
    const toggleText = document.getElementById("console-toggle-text");
    if (!consoleEl) return;

    if (consoleEl.style.display === "none") {
        consoleEl.style.display = "block";
        toggleText.textContent = "Hide Raw Output ▴";
    } else {
        consoleEl.style.display = "none";
        toggleText.textContent = "Show Raw Output ▾";
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
