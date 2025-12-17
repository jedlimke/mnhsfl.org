/**
 * Responsive Tables
 * Adds data-label attributes to table cells for mobile card layout
 */
(function() {
	'use strict';

	function makeTablesResponsive() {
		// Find all tables
		const tables = document.querySelectorAll('table');
		
		tables.forEach(table => {
			// Get all header cells
			const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
			
			// Add data-label to each body cell
			const rows = table.querySelectorAll('tbody tr');
			rows.forEach(row => {
				const cells = row.querySelectorAll('td');
				cells.forEach((cell, index) => {
					if (headers[index]) {
						cell.setAttribute('data-label', headers[index]);
					}
				});
			});
		});
	}

	// Run on page load
	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', makeTablesResponsive);
	} else {
		makeTablesResponsive();
	}
})();
