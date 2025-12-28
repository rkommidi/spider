# Static Assets

This directory contains all frontend assets for the Product Price Tracker web application.

## Directory Structure

```
static/
├── css/
│   └── style.css          # Main stylesheet
├── js/
│   └── main.js            # JavaScript for table sorting, pagination, and interactivity
└── images/
    └── favicon.svg        # Site favicon
```

## Features

### CSS (style.css)
- **Responsive Design**: Mobile-first approach with breakpoints at 768px and 480px
- **Minimal Clean Style**: Simple, professional design with good readability
- **Table Styling**: Sticky headers, hover effects, and sortable indicators
- **Utility Classes**: Helper classes for spacing and visibility

### JavaScript (main.js)

#### Table Sorting
- Click any sortable column header to sort
- Handles different data types: text, numbers, prices, dates
- Visual indicators (↑/↓) show current sort direction
- Works on all tables with `sortable` class on headers

#### Pagination
- Automatically activates on tables with >10 rows
- Configurable items per page (10, 25, 50, 100)
- Previous/Next navigation
- Shows current page and total items
- Smooth scroll to table top on page change

#### Auto-Applied Features
- Horizontal scroll wrapper for tables on mobile
- Smooth scrolling for hash links

## Usage

### Making Tables Sortable

Add the `sortable` class and `data-type` attribute to table headers:

```html
<table id="my-table">
    <thead>
        <tr>
            <th class="sortable" data-type="text">Name</th>
            <th class="sortable" data-type="price">Price</th>
            <th class="sortable" data-type="number">Quantity</th>
            <th class="sortable" data-type="date">Date</th>
        </tr>
    </thead>
    <tbody>
        <!-- rows here -->
    </tbody>
</table>
```

Supported data types:
- `text`: String comparison (case-insensitive)
- `price`: Removes $ and commas, sorts numerically
- `number`: Numeric comparison
- `date`: Parses dates and sorts chronologically

### Enabling Pagination

Add an `id` attribute to your table. Pagination will auto-initialize for:
- `#products-table`: 25 items per page (default)
- `#price-history-table`: 50 items per page
- Other tables: 10+ rows required to activate

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- IE11 not supported (uses modern JavaScript features)

## Customization

### Changing Colors

Edit CSS variables at the top of `style.css`:
- Primary color: `#3498db`
- Background: `#f5f5f5`
- Dark header: `#2c3e50`

### Pagination Defaults

Edit `main.js` line ~45 to change default rows per page:
```javascript
this.rowsPerPage = options.rowsPerPage || 25;
```

### Mobile Breakpoints

Adjust media queries in `style.css`:
- Tablet: `@media (max-width: 768px)`
- Mobile: `@media (max-width: 480px)`
