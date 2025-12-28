/**
 * Product Price Tracker - Main JavaScript
 * Handles table sorting, pagination, and interactive features
 */

// Table Sorting Functionality
class TableSorter {
    constructor(table) {
        this.table = table;
        this.tbody = table.querySelector('tbody');
        this.headers = table.querySelectorAll('th.sortable');
        this.currentSort = { column: -1, direction: 'asc' };

        this.init();
    }

    init() {
        this.headers.forEach((header, index) => {
            header.addEventListener('click', () => this.sortColumn(index, header));
        });
    }

    sortColumn(columnIndex, header) {
        const rows = Array.from(this.tbody.querySelectorAll('tr'));
        const isNumeric = header.dataset.type === 'number';
        const isPrice = header.dataset.type === 'price';
        const isDate = header.dataset.type === 'date';

        // Determine sort direction
        let direction = 'asc';
        if (this.currentSort.column === columnIndex) {
            direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        }

        // Sort rows
        rows.sort((a, b) => {
            let aValue = a.cells[columnIndex].textContent.trim();
            let bValue = b.cells[columnIndex].textContent.trim();

            // Handle different data types
            if (isPrice) {
                aValue = parseFloat(aValue.replace(/[$,]/g, '')) || 0;
                bValue = parseFloat(bValue.replace(/[$,]/g, '')) || 0;
            } else if (isNumeric) {
                aValue = parseFloat(aValue) || 0;
                bValue = parseFloat(bValue) || 0;
            } else if (isDate) {
                aValue = new Date(aValue).getTime() || 0;
                bValue = new Date(bValue).getTime() || 0;
            } else {
                aValue = aValue.toLowerCase();
                bValue = bValue.toLowerCase();
            }

            if (aValue < bValue) return direction === 'asc' ? -1 : 1;
            if (aValue > bValue) return direction === 'asc' ? 1 : -1;
            return 0;
        });

        // Clear previous sort indicators
        this.headers.forEach(h => {
            h.classList.remove('sort-asc', 'sort-desc');
        });

        // Add new sort indicator
        header.classList.add(`sort-${direction}`);

        // Update table
        rows.forEach(row => this.tbody.appendChild(row));

        // Update current sort state
        this.currentSort = { column: columnIndex, direction };
    }
}

// Table Pagination Functionality
class TablePaginator {
    constructor(table, options = {}) {
        this.table = table;
        this.tbody = table.querySelector('tbody');
        this.rows = Array.from(this.tbody.querySelectorAll('tr'));
        this.currentPage = 1;
        this.rowsPerPage = options.rowsPerPage || 25;
        this.paginationContainer = null;

        this.init();
    }

    init() {
        if (this.rows.length <= 10) {
            return; // Don't paginate if less than 10 rows
        }

        this.createPaginationControls();
        this.render();
    }

    createPaginationControls() {
        // Create pagination container
        this.paginationContainer = document.createElement('div');
        this.paginationContainer.className = 'pagination';

        // Insert after table
        this.table.parentNode.insertBefore(
            this.paginationContainer,
            this.table.nextSibling
        );
    }

    render() {
        if (!this.paginationContainer) return;

        const totalPages = Math.ceil(this.rows.length / this.rowsPerPage);
        const start = (this.currentPage - 1) * this.rowsPerPage;
        const end = start + this.rowsPerPage;

        // Hide all rows
        this.rows.forEach(row => row.style.display = 'none');

        // Show current page rows
        this.rows.slice(start, end).forEach(row => row.style.display = '');

        // Update pagination controls
        this.paginationContainer.innerHTML = `
            <button class="pagination-btn" id="prev-page" ${this.currentPage === 1 ? 'disabled' : ''}>
                Previous
            </button>
            <span class="pagination-info">
                Page ${this.currentPage} of ${totalPages} (${this.rows.length} total items)
            </span>
            <button class="pagination-btn" id="next-page" ${this.currentPage === totalPages ? 'disabled' : ''}>
                Next
            </button>
            <select class="pagination-select" id="rows-per-page">
                <option value="10" ${this.rowsPerPage === 10 ? 'selected' : ''}>10 per page</option>
                <option value="25" ${this.rowsPerPage === 25 ? 'selected' : ''}>25 per page</option>
                <option value="50" ${this.rowsPerPage === 50 ? 'selected' : ''}>50 per page</option>
                <option value="100" ${this.rowsPerPage === 100 ? 'selected' : ''}>100 per page</option>
            </select>
        `;

        // Add event listeners
        this.paginationContainer.querySelector('#prev-page')?.addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.render();
                this.scrollToTop();
            }
        });

        this.paginationContainer.querySelector('#next-page')?.addEventListener('click', () => {
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.render();
                this.scrollToTop();
            }
        });

        this.paginationContainer.querySelector('#rows-per-page')?.addEventListener('change', (e) => {
            this.rowsPerPage = parseInt(e.target.value);
            this.currentPage = 1;
            this.render();
            this.scrollToTop();
        });
    }

    scrollToTop() {
        const tableTop = this.table.getBoundingClientRect().top + window.pageYOffset - 100;
        window.scrollTo({ top: tableTop, behavior: 'smooth' });
    }

    refresh() {
        this.rows = Array.from(this.tbody.querySelectorAll('tr'));
        this.currentPage = 1;
        this.render();
    }
}

// Real-time Search Filter
class SearchFilter {
    constructor(input, table) {
        this.input = input;
        this.table = table;
        this.tbody = table.querySelector('tbody');
        this.rows = Array.from(this.tbody.querySelectorAll('tr'));

        this.init();
    }

    init() {
        this.input.addEventListener('input', (e) => this.filter(e.target.value));
    }

    filter(searchTerm) {
        const term = searchTerm.toLowerCase().trim();

        this.rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(term);
            row.style.display = matches ? '' : 'none';
        });

        // Update count if exists
        const countElement = document.querySelector('.filter-results-count');
        if (countElement) {
            const visibleRows = this.rows.filter(row => row.style.display !== 'none').length;
            countElement.textContent = `Showing ${visibleRows} of ${this.rows.length} items`;
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Highlight active navigation link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav a');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Initialize table sorting for all tables with sortable headers
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const sortableHeaders = table.querySelectorAll('th.sortable');
        if (sortableHeaders.length > 0) {
            new TableSorter(table);
        }

        // Initialize pagination for main product table
        if (table.id === 'products-table') {
            new TablePaginator(table, { rowsPerPage: 25 });
        } else if (table.id === 'price-history-table') {
            new TablePaginator(table, { rowsPerPage: 50 });
        }
    });

    // Add real-time search if search input exists
    const searchInput = document.querySelector('input[name="search"]');
    const productTable = document.querySelector('#products-table');
    if (searchInput && productTable && !searchInput.form?.querySelector('[type="submit"]')) {
        new SearchFilter(searchInput, productTable);
    }

    // Add table wrapper for horizontal scrolling on mobile
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-wrapper';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });

    // Auto-scroll to element if hash is present
    if (window.location.hash) {
        setTimeout(() => {
            const element = document.querySelector(window.location.hash);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);
    }

    console.log('Product Price Tracker initialized');
});

// Utility: Format numbers as currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Utility: Format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Export for use in other scripts
window.PriceTracker = {
    TableSorter,
    TablePaginator,
    SearchFilter,
    formatCurrency,
    formatDate
};
