// ===== PREMIUM LANDING PAGE JAVASCRIPT =====

// Global variables
let scene, camera, renderer, particles, mouse, animationId;
let scrollY = 0;
let currentScrollY = 0;

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initThreeJS();
    initScrollAnimations();
    initNavigation();
    initChatbot();
    initCounterAnimations();
    initParallax();
    initSmoothScrolling();
    initFormValidation();
    initIntersectionObserver();
});

// Three.js 3D Background Animation
function initThreeJS() {
    try {
        // Scene setup
        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        renderer = new THREE.WebGLRenderer({ 
            canvas: document.getElementById('three-canvas'),
            alpha: true,
            antialias: true 
        });
        
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        // Create particles
        createParticles();
        
        // Create floating medical elements
        createMedicalElements();
        
        // Camera position
        camera.position.z = 5;
        
        // Mouse tracking
        mouse = { x: 0, y: 0 };
        document.addEventListener('mousemove', onMouseMove);
        
        // Start animation loop
        animate();
        
        // Handle window resize
        window.addEventListener('resize', onWindowResize);
        
    } catch (error) {
        console.log('WebGL not supported, falling back to CSS animations');
        // Fallback to CSS-only animations
        document.getElementById('three-canvas').style.display = 'none';
    }
}

function createParticles() {
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 500;
    const posArray = new Float32Array(particlesCount * 3);
    
    for(let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 20;
    }
    
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    
    const particlesMaterial = new THREE.PointsMaterial({
        size: 0.005,
        color: '#667eea',
        transparent: true,
        opacity: 0.3
    });
    
    particles = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particles);
}

function createMedicalElements() {
    // Create floating DNA helix
    const helixGeometry = new THREE.TorusGeometry(0.3, 0.1, 8, 20);
    const helixMaterial = new THREE.MeshBasicMaterial({ 
        color: '#10b981', 
        transparent: true, 
        opacity: 0.6,
        wireframe: true 
    });
    
    for(let i = 0; i < 3; i++) {
        const helix = new THREE.Mesh(helixGeometry, helixMaterial);
        helix.position.set(
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 5
        );
        helix.rotation.set(
            Math.random() * Math.PI,
            Math.random() * Math.PI,
            Math.random() * Math.PI
        );
        scene.add(helix);
    }
    
    // Create floating cross shapes
    const crossGeometry = new THREE.BoxGeometry(0.1, 0.4, 0.1);
    const crossMaterial = new THREE.MeshBasicMaterial({ 
        color: '#667eea', 
        transparent: true, 
        opacity: 0.4 
    });
    
    for(let i = 0; i < 5; i++) {
        const crossGroup = new THREE.Group();
        
        const vertical = new THREE.Mesh(crossGeometry, crossMaterial);
        const horizontal = new THREE.Mesh(crossGeometry, crossMaterial);
        horizontal.rotation.z = Math.PI / 2;
        
        crossGroup.add(vertical);
        crossGroup.add(horizontal);
        
        crossGroup.position.set(
            (Math.random() - 0.5) * 15,
            (Math.random() - 0.5) * 15,
            (Math.random() - 0.5) * 8
        );
        
        scene.add(crossGroup);
    }
}

function onMouseMove(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
}

function animate() {
    animationId = requestAnimationFrame(animate);
    
    // Rotate particles
    if (particles) {
        particles.rotation.x += 0.0005;
        particles.rotation.y += 0.0005;
    }
    
    // Animate medical elements
    scene.children.forEach((child, index) => {
        if (child.type === 'Mesh' || child.type === 'Group') {
            child.rotation.x += 0.001 * (index + 1);
            child.rotation.y += 0.002 * (index + 1);
            child.position.y += Math.sin(Date.now() * 0.001 + index) * 0.001;
        }
    });
    
    // Mouse interaction
    if (camera) {
        camera.position.x += (mouse.x * 0.5 - camera.position.x) * 0.05;
        camera.position.y += (mouse.y * 0.5 - camera.position.y) * 0.05;
    }
    
    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Scroll Animations with GSAP
function initScrollAnimations() {
    // Check if GSAP is available
    if (typeof gsap === 'undefined') {
        console.log('GSAP not loaded, using fallback animations');
        initFallbackAnimations();
        return;
    }
    
    // Hero section animations
    gsap.timeline()
        .from('.hero-badge', { duration: 1, y: 50, opacity: 0, ease: 'power3.out' })
        .from('.hero-title', { duration: 1, y: 80, opacity: 0, ease: 'power3.out' }, '-=0.5')
        .from('.hero-subtitle', { duration: 1, y: 60, opacity: 0, ease: 'power3.out' }, '-=0.5')
        .from('.hero-buttons', { duration: 1, y: 40, opacity: 0, ease: 'power3.out' }, '-=0.5')
        .from('.hero-stats', { duration: 1, y: 30, opacity: 0, ease: 'power3.out' }, '-=0.5');
    
    // Parallax effects
    gsap.registerPlugin(ScrollTrigger);
    
    // Hero parallax
    gsap.to('.hero-visual', {
        yPercent: -50,
        ease: 'none',
        scrollTrigger: {
            trigger: '.hero-section',
            start: 'top bottom',
            end: 'bottom top',
            scrub: true
        }
    });
    
    // Section animations
    gsap.utils.toArray('.section-header').forEach(header => {
        gsap.from(header, {
            y: 100,
            opacity: 0,
            duration: 1,
            ease: 'power3.out',
            scrollTrigger: {
                trigger: header,
                start: 'top 80%',
                end: 'bottom 20%',
                toggleActions: 'play none none reverse'
            }
        });
    });
    
    // Feature cards stagger animation
    gsap.from('.feature-card', {
        y: 80,
        opacity: 0,
        duration: 1,
        stagger: 0.2,
        ease: 'power3.out',
        scrollTrigger: {
            trigger: '.features-grid',
            start: 'top 80%'
        }
    });
    
    // Testimonial cards animation
    gsap.from('.testimonial-card', {
        scale: 0.8,
        opacity: 0,
        duration: 1,
        stagger: 0.3,
        ease: 'back.out(1.7)',
        scrollTrigger: {
            trigger: '.testimonials-grid',
            start: 'top 80%'
        }
    });
}

function initFallbackAnimations() {
    // CSS-based animations for when GSAP is not available
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 1s ease forwards';
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.feature-card, .testimonial-card, .section-header').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(50px)';
        observer.observe(el);
    });
}

// Navigation functionality
function initNavigation() {
    const nav = document.getElementById('main-nav');
    const navLinks = document.querySelectorAll('.nav-link');
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    // Glassmorphism effect on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });
    
    // Smooth scroll for nav links
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update active link
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            }
        });
    });
    
    // Mobile menu toggle
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            mobileToggle.classList.toggle('active');
        });
    }
    
    // Update active link on scroll
    window.addEventListener('scroll', updateActiveNavLink);
}

function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.scrollY >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

// Counter animations
function initCounterAnimations() {
    const counters = document.querySelectorAll('[data-count]');
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.dataset.count);
                animateCounter(counter, target);
                counterObserver.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => {
        counterObserver.observe(counter);
    });
}

function animateCounter(element, target) {
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current).toLocaleString() + '+';
    }, 40);
}

// Parallax effects
function initParallax() {
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    });
}

// Smooth scrolling
function initSmoothScrolling() {
    // Add smooth scroll behavior to all internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Chatbot functionality
function initChatbot() {
    const chatToggle = document.getElementById('chatbot-toggle');
    const chatPanel = document.getElementById('chatbot-panel');
    const closeChat = document.getElementById('close-chat');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-message');
    const messagesContainer = document.querySelector('.chatbot-messages');
    
    if (!chatToggle || !chatPanel) return;
    
    // Toggle chat panel
    chatToggle.addEventListener('click', () => {
        chatPanel.classList.toggle('active');
    });
    
    // Close chat
    if (closeChat) {
        closeChat.addEventListener('click', () => {
            chatPanel.classList.remove('active');
        });
    }
    
    // Send message
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';
        
        // Simulate bot response
        setTimeout(() => {
            const responses = [
                "Thank you for your message! Our healthcare team will get back to you soon.",
                "I'm here to help with your health questions. Would you like to book an appointment?",
                "For urgent medical concerns, please contact your healthcare provider directly.",
                "I can help you find doctors, book appointments, or answer general health questions.",
                "Your health is important to us. How can I assist you today?"
            ];
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addMessage(randomResponse, 'bot');
        }, 1000);
    }
    
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div style="background: var(--primary-gradient); color: white; padding: var(--space-3); border-radius: var(--radius-lg); margin-bottom: var(--space-3); margin-left: var(--space-8); text-align: right;">
                    <p style="margin: 0; font-size: 0.875rem;">${text}</p>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div style="background: var(--bg-secondary); padding: var(--space-3); border-radius: var(--radius-lg); margin-bottom: var(--space-3); margin-right: var(--space-8);">
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.875rem; line-height: 1.5;">${text}</p>
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Send on enter key
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Send on button click
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
}

// Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('.premium-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Simple form validation
            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = 'var(--error-color)';
                    input.addEventListener('input', () => {
                        input.style.borderColor = '';
                    }, { once: true });
                }
            });
            
            if (isValid) {
                // Show success message
                showNotification('Message sent successfully! We\'ll get back to you soon.', 'success');
                form.reset();
            } else {
                showNotification('Please fill in all required fields.', 'error');
            }
        });
    });
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? 'var(--success-color)' : 'var(--error-color)'};
        color: white;
        padding: var(--space-4) var(--space-6);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        z-index: 10000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 5000);
}

// Intersection Observer for animations
function initIntersectionObserver() {
    // Create AOS (Animate On Scroll) effect
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 1000,
            easing: 'ease-out-cubic',
            once: true,
            offset: 100
        });
    }
    
    // Custom intersection observer for elements without AOS
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements that need fade-in animation
    document.querySelectorAll('.fade-in').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        fadeInObserver.observe(el);
    });
}

// Performance optimization
function optimizePerformance() {
    // Throttle scroll events
    let ticking = false;
    
    function updateOnScroll() {
        updateActiveNavLink();
        ticking = false;
    }
    
    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(updateOnScroll);
            ticking = true;
        }
    });
    
    // Preload critical images
    const criticalImages = [
        // Add any critical image URLs here
    ];
    
    criticalImages.forEach(src => {
        const img = new Image();
        img.src = src;
    });
}

// Initialize performance optimizations
optimizePerformance();

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (animationId) {
        cancelAnimationFrame(animationId);
    }
    
    if (renderer) {
        renderer.dispose();
    }
});

// Add custom CSS animations for fallback
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
`;
document.head.appendChild(style);

// Log successful initialization
console.log('Premium landing page initialized successfully!');