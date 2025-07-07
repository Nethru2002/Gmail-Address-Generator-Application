// gmail-generator/static/script.js

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element Selection ---
    const form = document.getElementById('generator-form');
    const nameInput = document.getElementById('name');
    const quantityInput = document.getElementById('quantity');
    const generateBtn = document.getElementById('generate-btn');
    const resultsHeader = document.getElementById('results-header');
    const resultsList = document.getElementById('results-list');
    const copyAllBtn = document.getElementById('copy-all-btn');
    const toast = document.getElementById('toast');
    
    // The URL of our Flask backend API
    const API_URL = 'http://127.0.0.1:5000/generate';
    
    // Store emails globally to access them for 'Copy All'
    let currentEmails = [];

    // --- Event Listeners ---
    form.addEventListener('submit', handleFormSubmit);
    copyAllBtn.addEventListener('click', handleCopyAll);

    // --- Functions ---
    async function handleFormSubmit(event) {
        event.preventDefault();

        const name = nameInput.value.trim();
        const quantity = parseInt(quantityInput.value, 10);

        if (!name || !quantity || quantity < 1) {
            showToast('Please enter a valid name and quantity.', 'error');
            return;
        }
        
        setLoadingState(true);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, quantity }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error');
            }

            const data = await response.json();
            currentEmails = data.emails; // Store for 'Copy All'
            displayResults(currentEmails);

        } catch (error) {
            console.error('Error:', error);
            displayError(error.message);
        } finally {
            setLoadingState(false);
        }
    }

    function setLoadingState(isLoading) {
        generateBtn.disabled = isLoading;
        if (isLoading) {
            generateBtn.innerHTML = `<span>Generating...</span>`;
            resultsHeader.style.display = 'none';
            resultsList.innerHTML = `<div class="loader-container">Generating your emails...</div>`;
        } else {
            generateBtn.innerHTML = `<span>Generate Addresses</span>`;
        }
    }

    function displayResults(emails) {
        resultsList.innerHTML = ''; // Clear loader/placeholder

        if (!emails || emails.length === 0) {
            resultsList.innerHTML = `<div class="placeholder"><p>Could not generate emails. Please try a different name.</p></div>`;
            return;
        }

        resultsHeader.style.display = 'flex'; // Show the results header
        
        emails.forEach(email => {
            const item = document.createElement('div');
            item.className = 'email-item';
            item.textContent = email;
            item.addEventListener('click', () => copyToClipboard(email, `Copied: ${email}`));
            resultsList.appendChild(item);
        });
    }
    
    function displayError(message) {
        resultsHeader.style.display = 'none';
        resultsList.innerHTML = `<div class="placeholder"><p style="color: #d9534f;">Error: ${message}</p></div>`;
    }

    function handleCopyAll() {
        if (currentEmails.length > 0) {
            const allEmailsText = currentEmails.join('\n');
            copyToClipboard(allEmailsText, `${currentEmails.length} emails copied to clipboard!`);
        }
    }

    function copyToClipboard(text, message) {
        navigator.clipboard.writeText(text).then(() => {
            showToast(message);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            showToast('Failed to copy to clipboard.', 'error');
        });
    }

    let toastTimeout;
    function showToast(message) {
        clearTimeout(toastTimeout); // Clear previous toast timeout if any
        toast.textContent = message;
        toast.className = 'toast show';
        
        toastTimeout = setTimeout(() => {
            toast.className = 'toast';
        }, 3000); // Hide after 3 seconds
    }
});