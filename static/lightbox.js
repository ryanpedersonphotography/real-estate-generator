/**
 * Lightweight Lightbox for Real Estate Gallery
 * No dependencies, vanilla JavaScript
 */

(function() {
    'use strict';
    
    let currentIndex = 0;
    let galleryImages = [];
    let lightbox = null;
    let lightboxImg = null;
    let lightboxCaption = null;
    let prevBtn = null;
    let nextBtn = null;
    let closeBtn = null;
    let lightboxCounter = null;
    
    // Initialize lightbox on DOM ready
    document.addEventListener('DOMContentLoaded', initLightbox);
    
    function initLightbox() {
        // Create lightbox HTML structure
        createLightboxHTML();
        
        // Get all gallery images
        const galleryItems = document.querySelectorAll('.gallery-item img');
        
        // Store image sources and add click handlers
        galleryItems.forEach((img, index) => {
            galleryImages.push({
                src: img.src,
                alt: img.alt
            });
            
            // Make parent clickable
            const parent = img.closest('.gallery-item');
            if (parent) {
                parent.addEventListener('click', (e) => {
                    e.preventDefault();
                    openLightbox(index);
                });
                parent.style.cursor = 'pointer';
            }
        });
        
        // Add keyboard navigation
        document.addEventListener('keydown', handleKeyboard);
    }
    
    function createLightboxHTML() {
        // Create lightbox container
        lightbox = document.createElement('div');
        lightbox.id = 'lightbox';
        lightbox.className = 'lightbox';
        lightbox.style.display = 'none';
        
        // Create lightbox content wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'lightbox-wrapper';
        
        // Create close button
        closeBtn = document.createElement('button');
        closeBtn.className = 'lightbox-close';
        closeBtn.innerHTML = '×';
        closeBtn.setAttribute('aria-label', 'Close lightbox');
        closeBtn.addEventListener('click', closeLightbox);
        
        // Create image container
        const imgContainer = document.createElement('div');
        imgContainer.className = 'lightbox-image-container';
        
        // Create main image
        lightboxImg = document.createElement('img');
        lightboxImg.className = 'lightbox-image';
        lightboxImg.alt = '';
        
        // Create navigation buttons
        prevBtn = document.createElement('button');
        prevBtn.className = 'lightbox-nav lightbox-prev';
        prevBtn.innerHTML = '‹';
        prevBtn.setAttribute('aria-label', 'Previous image');
        prevBtn.addEventListener('click', showPrevious);
        
        nextBtn = document.createElement('button');
        nextBtn.className = 'lightbox-nav lightbox-next';
        nextBtn.innerHTML = '›';
        nextBtn.setAttribute('aria-label', 'Next image');
        nextBtn.addEventListener('click', showNext);
        
        // Create caption and counter
        const infoBar = document.createElement('div');
        infoBar.className = 'lightbox-info';
        
        lightboxCaption = document.createElement('div');
        lightboxCaption.className = 'lightbox-caption';
        
        lightboxCounter = document.createElement('div');
        lightboxCounter.className = 'lightbox-counter';
        
        // Assemble the lightbox
        imgContainer.appendChild(lightboxImg);
        infoBar.appendChild(lightboxCaption);
        infoBar.appendChild(lightboxCounter);
        
        wrapper.appendChild(closeBtn);
        wrapper.appendChild(prevBtn);
        wrapper.appendChild(nextBtn);
        wrapper.appendChild(imgContainer);
        wrapper.appendChild(infoBar);
        
        lightbox.appendChild(wrapper);
        
        // Add click on backdrop to close
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) {
                closeLightbox();
            }
        });
        
        // Add to body
        document.body.appendChild(lightbox);
    }
    
    function openLightbox(index) {
        currentIndex = index;
        updateLightboxImage();
        
        // Show lightbox
        lightbox.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Focus for accessibility
        lightbox.focus();
        
        // Add active class after a tiny delay for transition
        setTimeout(() => {
            lightbox.classList.add('lightbox-active');
        }, 10);
    }
    
    function closeLightbox() {
        lightbox.classList.remove('lightbox-active');
        
        // Hide after transition
        setTimeout(() => {
            lightbox.style.display = 'none';
            document.body.style.overflow = '';
        }, 300);
    }
    
    function updateLightboxImage() {
        if (galleryImages.length === 0) return;
        
        const image = galleryImages[currentIndex];
        
        // Update image with loading state
        lightbox.classList.add('lightbox-loading');
        
        const tempImg = new Image();
        tempImg.onload = () => {
            lightboxImg.src = image.src;
            lightboxImg.alt = image.alt;
            lightboxCaption.textContent = image.alt;
            lightboxCounter.textContent = `${currentIndex + 1} / ${galleryImages.length}`;
            lightbox.classList.remove('lightbox-loading');
        };
        tempImg.src = image.src;
        
        // Update navigation button visibility
        prevBtn.style.display = currentIndex > 0 ? 'block' : 'none';
        nextBtn.style.display = currentIndex < galleryImages.length - 1 ? 'block' : 'none';
    }
    
    function showNext() {
        if (currentIndex < galleryImages.length - 1) {
            currentIndex++;
            updateLightboxImage();
        }
    }
    
    function showPrevious() {
        if (currentIndex > 0) {
            currentIndex--;
            updateLightboxImage();
        }
    }
    
    function handleKeyboard(e) {
        if (lightbox.style.display !== 'flex') return;
        
        switch(e.key) {
            case 'Escape':
                closeLightbox();
                break;
            case 'ArrowLeft':
                showPrevious();
                break;
            case 'ArrowRight':
                showNext();
                break;
        }
    }
})();