document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('nav a');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    const toggleNav = document.querySelector('.toggle-nav');
    if (toggleNav) {
        toggleNav.addEventListener('click', function() {
            const nav = document.querySelector('nav');
            nav.classList.toggle('open');
        });
    }

    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const data = {
                age: parseInt(formData.get('age')),
                lifestyle: formData.get('lifestyle'),
                family_history: formData.get('family_history'),
                health_metrics: JSON.parse(formData.get('health_metrics'))
            };
            fetch('/api/profiles', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }).then(response => response.json()).then(data => {
                alert('Profile created successfully!');
                window.location.href = '/assessment';
            }).catch(error => {
                console.error('Error:', error);
            });
        });
    }
});
