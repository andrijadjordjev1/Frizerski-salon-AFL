// Glavni JavaScript fajl za aplikaciju

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts nakon 5 sekundi
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Potvrda brisanja
    const deleteButtons = document.querySelectorAll('a[href*="obrisi"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const confirmed = confirm('Da li ste sigurni da želite da obrišete ovu stavku?');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });

    // Animacija za kartice termina
    const terminCards1 = document.querySelectorAll('.termin-card');
    terminCards1.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    }); 

    // Validacija formi
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // Ukloni error klasu nakon unosa
                    field.addEventListener('input', function() {
                        field.classList.remove('error');
                    });
                }
            });

            if (!isValid) {
                e.preventDefault();
                showNotification('Molimo vas da popunite sva obavezna polja!', 'error');
            }
        });
    });

    // Mobile menu toggle
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }

    // Smooth scroll za anchor linkove
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Loading overlay za forme
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form.checkValidity()) {
               this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Šalje se...';
               this.disabled = true;

              // ✅ pokreni submit forme
              form.submit();
            }
        });
    });

    // Funkcija za prikazivanje notifikacija
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.textContent = message;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        notification.style.transition = 'all 0.3s ease';

        document.body.appendChild(notification);

        // Animacija pojavljivanja
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto uklanjanje
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    };

    // Funkcija za formatiranje datuma
    window.formatDate = function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('sr-RS', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    // Funkcija za formatiranje vremena
    window.formatTime = function(timeString) {
        return timeString.slice(0, 5); // Uzmi samo HH:MM
    };

    // Dark mode toggle (opciono)
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
        });

        // Učitaj dark mode iz localStorage
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'true') {
            document.body.classList.add('dark-mode');
        }
    }

    // Pretraga u tabelama
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.table-container').querySelector('table');
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });

    // Sortiranje tabela
    const sortHeaders = document.querySelectorAll('.sortable');
    sortHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(this.parentNode.children).indexOf(this);
            const isAscending = !this.classList.contains('sort-asc');

            // Sortiranje redova
            rows.sort((a, b) => {
                const aText = a.children[columnIndex].textContent.trim();
                const bText = b.children[columnIndex].textContent.trim();
                
                // Pokušaj numeričko sortiranje
                const aNum = parseFloat(aText.replace(/[^\d.-]/g, ''));
                const bNum = parseFloat(bText.replace(/[^\d.-]/g, ''));
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAscending ? aNum - bNum : bNum - aNum;
                }
                
                // Tekstualno sortiranje
                return isAscending ? 
                    aText.localeCompare(bText) : 
                    bText.localeCompare(aText);
            });

            // Ukloni sve redove i dodaj sortirane
            rows.forEach(row => tbody.removeChild(row));
            rows.forEach(row => tbody.appendChild(row));

            // Updejtuj sort indikatore
            sortHeaders.forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            this.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        });
    });

    // Funkcija za validaciju email-a
    window.isValidEmail = function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    // Funkcija za validaciju telefona
    window.isValidPhone = function(phone) {
        const phoneRegex = /^[\d\s\+\-\(\)]+$/;
        return phoneRegex.test(phone) && phone.length >= 8;
    };

    // Auto-resize textarea
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Countdown za termine
    const terminCards2 = document.querySelectorAll('.termin-card[data-datum][data-vreme]');
    terminCards2.forEach(card => {
        const datum = card.dataset.datum;
        const vreme = card.dataset.vreme;
        const terminTime = new Date(`${datum}T${vreme}`);
        
        updateCountdown(card, terminTime);
        setInterval(() => updateCountdown(card, terminTime), 60000); // Update svaki minut
    });

    function updateCountdown(card, terminTime) {
        const now = new Date();
        const timeDiff = terminTime - now;

        if (timeDiff > 0) {
            const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));

            let countdownText = '';
            if (days > 0) {
                countdownText = `${days} dan${days > 1 ? 'a' : ''}`;
            } else if (hours > 0) {
                countdownText = `${hours} sat${hours > 1 ? 'a' : ''}`;
            } else {
                countdownText = `${minutes} minut${minutes > 1 ? 'a' : ''}`;
            }

            let countdownEl = card.querySelector('.countdown');
            if (!countdownEl) {
                countdownEl = document.createElement('div');
                countdownEl.className = 'countdown';
                card.appendChild(countdownEl);
            }
            countdownEl.innerHTML = `<i class="fas fa-hourglass-half"></i> Preostalo: ${countdownText}`;
        }
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S za čuvanje forme
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const submitBtn = document.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }

        // Escape za otkazivanje/zatvaranje
        if (e.key === 'Escape') {
            const cancelBtn = document.querySelector('a[href*="dashboard"], a[href*="lista"]');
            if (cancelBtn) {
                cancelBtn.click();
            }
        }
    });

    // Lazy loading za slike
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Print funkcionalnost
    window.printTable = function(tableSelector) {
        const table = document.querySelector(tableSelector);
        if (table) {
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Štampa</title>
                        <style>
                            body { font-family: Arial, sans-serif; }
                            table { width: 100%; border-collapse: collapse; }
                            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                            th { background-color: #f2f2f2; }
                            .actions { display: none; }
                        </style>
                    </head>
                    <body>
                        <h2>Evidencija termina - Frizerski salon</h2>
                        ${table.outerHTML}
                    </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.print();
        }
    };

    // Export funkcionalnost (CSV)
    window.exportToCSV = function(tableSelector, filename = 'export.csv') {
        const table = document.querySelector(tableSelector);
        if (!table) return;

        let csv = [];
        const rows = table.querySelectorAll('tr');

        rows.forEach(row => {
            const cols = row.querySelectorAll('td, th');
            const rowData = Array.from(cols)
                .filter(col => !col.classList.contains('actions'))
                .map(col => `"${col.textContent.trim().replace(/"/g, '""')}"`)
                .join(',');
            csv.push(rowData);
        });

        const csvFile = new Blob([csv.join('\n')], { type: 'text/csv' });
        const downloadLink = document.createElement('a');
        downloadLink.download = filename;
        downloadLink.href = window.URL.createObjectURL(csvFile);
        downloadLink.style.display = 'none';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    };

    console.log('Frizerski salon - Evidencija termina inicijalizovana');
});