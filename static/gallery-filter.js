/**
 * Gallery Filter Functionality
 * Allows filtering photos by category when multiple folders are detected
 */

(function() {
    'use strict';
    
    // Initialize gallery filters on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGalleryFilters);
    } else {
        initGalleryFilters();
    }
    
    function initGalleryFilters() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        const galleryItems = document.querySelectorAll('.gallery-item');
        
        // Skip if no filters present
        if (filterBtns.length === 0) return;
        
        filterBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const filter = this.dataset.filter;
                
                // Update active button
                filterBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Filter items with animation
                galleryItems.forEach(item => {
                    const category = item.dataset.category || 'uncategorized';
                    
                    if (filter === 'all' || category === filter) {
                        // Show item
                        item.style.display = '';
                        setTimeout(() => {
                            item.style.opacity = '1';
                            item.style.transform = 'scale(1)';
                        }, 10);
                    } else {
                        // Hide item
                        item.style.opacity = '0';
                        item.style.transform = 'scale(0.8)';
                        setTimeout(() => {
                            item.style.display = 'none';
                        }, 300);
                    }
                });
                
                // Update URL hash for bookmarking
                if (filter !== 'all') {
                    window.location.hash = filter;
                } else {
                    history.pushState("", document.title, window.location.pathname + window.location.search);
                }
            });
        });
        
        // Check for hash on load and apply filter
        if (window.location.hash) {
            const hashFilter = window.location.hash.substring(1);
            const targetBtn = document.querySelector(`[data-filter="${hashFilter}"]`);
            if (targetBtn) {
                targetBtn.click();
            }
        }
        
        // Add transition styles to gallery items
        galleryItems.forEach(item => {
            item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        });
    }
})();