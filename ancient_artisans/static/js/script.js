// Login Modal Functionality
function openLoginModal() {
    document.getElementById('loginModal').style.display = 'flex';
    // Reset forms and errors when opening modal
    document.querySelectorAll('form').forEach(form => form.reset());
    const errorDiv = document.getElementById('loginError');
    if (errorDiv) errorDiv.style.display = 'none';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

// Tab switching functionality
const tabs = document.querySelectorAll('.tab');
const buyerForm = document.getElementById('buyerLoginForm');
const sellerForm = document.getElementById('sellerLoginForm');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove 'active' from all tabs
        tabs.forEach(t => t.classList.remove('active'));
        // Add 'active' to clicked tab
        tab.classList.add('active');

        // Show correct form and hide errors
        const errorDiv = document.getElementById('loginError');
        if (errorDiv) errorDiv.style.display = 'none';
        
        if (tab.dataset.tab === 'buyer') {
            buyerForm.style.display = 'block';
            sellerForm.style.display = 'none';
        } else {
            buyerForm.style.display = 'none';
            sellerForm.style.display = 'block';
        }
    });
});

// Buyer login form submission
document.getElementById('buyerLoginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch('/buyer_login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        const errorDiv = document.getElementById('loginError');

        if (response.ok) {
            window.location.href = result.redirect || '/buyer_dashboard';
        } else {
            errorDiv.textContent = result.message || 'Login failed';
            errorDiv.style.display = 'block';
        }
    } catch (err) {
        console.error(err);
        const errorDiv = document.getElementById('loginError');
        errorDiv.textContent = 'Something went wrong. Please try again.';
        errorDiv.style.display = 'block';
    }
});

// Seller login form submission
const sellerLoginForm = document.getElementById('sellerLoginForm');
if (sellerLoginForm) {
    sellerLoginForm.addEventListener('submit', async function(e) {  // Fixed syntax error here
        e.preventDefault();
        
        const formData = new FormData(this);
        const data = {
            email: formData.get('email'),
            password: formData.get('password'),
            verification_code: formData.get('verification_code')
        };
        
        try {
            const response = await fetch('/seller_login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            const errorDiv = document.getElementById('loginError');
            
            if (response.ok) {
                window.location.href = result.redirect || '/seller_dashboard';
            } else {
                errorDiv.textContent = result.message || 'Login failed';
                errorDiv.style.display = 'block';
            }
        } catch (err) {
            console.error(err);
            const errorDiv = document.getElementById('loginError');
            errorDiv.textContent = 'Something went wrong. Please try again.';
            errorDiv.style.display = 'block';
        }
    });
}

// Auto-detect user type when email is entered
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', async function() {
            const email = this.value.trim();
            if (!email) return;
            
            try {
                const response = await fetch('/api/check-user-type', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email })
                });
                
                if (!response.ok) return;
                
                const result = await response.json();
                if (result.user_type) {
                    switchTab(result.user_type);
                }
            } catch (err) {
                console.error('Error checking user type:', err);
            }
        });
    });
});

// Tab switching function (single definition)
window.switchTab = function(tab) {
    const tabs = document.querySelectorAll('.tab');
    const buyerForm = document.getElementById('buyerLoginForm');
    const sellerForm = document.getElementById('sellerLoginForm');
    const errorDiv = document.getElementById('loginError');
    
    // Hide error message when switching tabs
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
    
    tabs.forEach(t => t.classList.remove('active'));
    
    if (tab === 'buyer') {
        document.querySelector('.tab:first-child').classList.add('active');
        if (buyerForm) buyerForm.style.display = 'block';
        if (sellerForm) sellerForm.style.display = 'none';
    } else {
        document.querySelector('.tab:last-child').classList.add('active');
        if (buyerForm) buyerForm.style.display = 'none';
        if (sellerForm) sellerForm.style.display = 'block';
    }
}

// AI Modal Functionality
function openAIModal() {
    document.getElementById('aiModal').style.display = 'flex';
}

function closeAIModal() {
    document.getElementById('aiModal').style.display = 'none';
}

// Messaging Modal Functionality
function openMessaging() {
    document.getElementById('messagingModal').style.display = 'flex';
}

function closeMessaging() {
    document.getElementById('messagingModal').style.display = 'none';
}

// Payment Modal Functionality
function openPaymentModal() {
    document.getElementById('paymentModal').style.display = 'flex';
}

function closePaymentModal() {
    document.getElementById('paymentModal').style.display = 'none';
}

function selectPayment(method) {
    document.querySelectorAll('.payment-method').forEach(el => {
        el.classList.remove('selected');
    });
    
    event.currentTarget.classList.add('selected');
}

// Close modals when clicking outside
window.onclick = function(event) {
    const loginModal = document.getElementById('loginModal');
    const aiModal = document.getElementById('aiModal');
    const messagingModal = document.getElementById('messagingModal');
    const paymentModal = document.getElementById('paymentModal');
    
    if (event.target === loginModal) closeLoginModal();
    if (event.target === aiModal) closeAIModal();
    if (event.target === messagingModal) closeMessaging();
    if (event.target === paymentModal) closePaymentModal();
};
    
    // Language selector functionality
    const languageBtn = document.querySelector('.language-btn');
    if (languageBtn) {
        languageBtn.addEventListener('click', function() {
            const dropdown = document.querySelector('.language-dropdown');
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        });
    }
    
    // Simulate AI price prediction (would use Gemini API in production)
    function simulateAIPricePrediction() {
        const products = document.querySelectorAll('.product-card');
        products.forEach(product => {
            const priceElement = product.querySelector('.product-price');
            if (priceElement) {
                const originalPrice = parseFloat(priceElement.textContent.replace('$', ''));
                const aiRecommended = (originalPrice * 0.95).toFixed(2); // 5% discount for demo
                
                // In a real implementation, this would call the Gemini API
                console.log(`AI price prediction for ${product.querySelector('.product-title').textContent}: $${aiRecommended}`);
            }
        });
    }

    // Initialize the page
    simulateAIPricePrediction();
    
// Get user ID from the data attribute
// script.js
document.addEventListener("DOMContentLoaded", () => {
    const cartContentElem = document.getElementById('cartContent');
    if (!cartContentElem) return;

    const USER_ID = cartContentElem.dataset.userId;


    //...................................

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", async () => {
            const productId = button.dataset.productId;
            const productName = button.dataset.productName || "Item";

            if (!productId) {
                alert("Product ID not found.");
                return;
            }

            button.disabled = true;
            const originalText = button.innerHTML;
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Adding...`;

            try {
                const response = await fetch("/cart/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ product_id: productId, quantity: 1 })
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    alert(`${productName} added to cart!`);
                    updateCartCount(1);
                } else {
                    if (response.status === 401) {
                        // User not logged in, show login modal
                        openLoginModal();
                        alert("Please login to add items to your cart");
                    } else {
                        alert(result.error || "Failed to add item to cart.");
                    }
                }
            } catch (error) {
                console.error("Error adding to cart:", error);
                alert("Error adding item to cart.");
            } finally {
                button.disabled = false;
                button.innerHTML = originalText;
            }
        });
    });
});



// Function to update cart count
function updateCartCount(change) {
    // Update localStorage
    let cartCount = parseInt(localStorage.getItem('cartCount') || '0');
    cartCount += change;
    localStorage.setItem('cartCount', cartCount);
    
    // Update UI
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(element => {
        element.textContent = cartCount;
        element.style.display = cartCount > 0 ? 'inline' : 'none';
    });
    
    // Also update the cart count in the database via API if needed
    // This would require an additional endpoint to get the actual cart count
}

    // ---------------- Load Cart ----------------
    async function loadCart() {
        try {
            const response = await fetch(`/api/cart?user_id=${USER_ID}`);
            if (!response.ok) throw new Error('Failed to fetch cart');

            const result = await response.json();
            let content = "";

            if (!result.items || result.items.length === 0) {
                content = `
                    <div style="text-align: center; padding: 40px;">
                        <i class="fas fa-shopping-cart" style="font-size: 4rem; color: #ddd; margin-bottom: 20px;"></i>
                        <h3>Your cart is empty</h3>
                        <p style="color: #666;">Start shopping to add items to your cart</p>
                        <a href="/products" class="btn btn-primary" style="margin-top: 20px;">
                            <i class="fas fa-shopping-bag"></i> Continue Shopping
                        </a>
                    </div>`;
            } else {
                result.items.forEach(item => {
                    content += `
                        <div class="cart-item" style="display:flex;justify-content:space-between;align-items:center;padding:10px;border-bottom:1px solid #eee;">
                            <div>
                                <strong>${item.name}</strong><br>
                                <span>${item.quantity} × $${item.price} = $${item.total_price}</span>
                            </div>
                            <button class="btn btn-danger btn-sm" onclick="removeItem(${item.cart_item_id})">Remove</button>
                        </div>`;
                });

                const totalAmount = result.items.reduce((sum, i) => sum + parseFloat(i.total_price), 0);
                content += `
                    <div style="margin-top:20px; text-align:right;">
                        <h4>Total: ₹${totalAmount.toFixed(2)}</h4>
                        <button class="btn btn-success">Proceed to Checkout</button>
                    </div>`;
            }

            cartContentElem.innerHTML = content;

        } catch (error) {
            console.error("Error loading cart:", error);
            cartContentElem.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #d9534f;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 4rem; margin-bottom: 20px;"></i>
                    <h3>Error loading cart</h3>
                    <p>Please try again later</p>
                </div>`;
        }
    }

    // ---------------- Remove Item ----------------
    window.removeItem = async function(itemId) {
        try {
            const response = await fetch("/cart/remove", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ cart_item_id: itemId })
            });

            if (response.ok) loadCart();
            else alert("Failed to remove item from cart");

        } catch (error) {
            console.error("Error removing item:", error);
            alert("Error removing item from cart");
        }
    }

    // Initial load
    loadCart();
});


// Initialize cart count on page load
document.addEventListener('DOMContentLoaded', function() {
    // Get actual cart count from server if user is logged in
    if (typeof USER_ID !== 'undefined') {
        fetch(`/api/cart/count?user_id=${USER_ID}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    localStorage.setItem('cartCount', data.count);
                    updateCartCount(0); // Just update UI without changing count
                }
            })
            .catch(error => {
                console.error('Error fetching cart count:', error);
            });
    } else {
        // Use localStorage as fallback
        const cartCount = parseInt(localStorage.getItem('cartCount') || '0');
        updateCartCount(0);
    }
});


    // Product search functionality
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput && searchInput.value.trim()) {
                window.location.href = `/products?search=${encodeURIComponent(searchInput.value.trim())}`;
            }
        });
    }
    
    // Category filter functionality
    const categoryLinks = document.querySelectorAll('.category-filter');
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const category = this.getAttribute('data-category');
            window.location.href = `/products?category=${encodeURIComponent(category)}`;
        });
    });
    
    // Payment method selection
    const paymentMethods = document.querySelectorAll('.payment-method');
    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            paymentMethods.forEach(m => m.classList.remove('selected'));
            this.classList.add('selected');
            
            const paymentMethod = this.getAttribute('data-method');
            document.getElementById('selectedPaymentMethod').value = paymentMethod;
            
            // Show/hide payment form fields based on selection
            const cardFields = document.getElementById('cardFields');
            if (cardFields) {
                if (paymentMethod === 'card') {
                    cardFields.style.display = 'block';
                } else {
                    cardFields.style.display = 'none';
                }
            }
        });
    });
    
    // Chat functionality
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const messageInput = document.getElementById('messageInput');
            if (messageInput && messageInput.value.trim()) {
                const message = messageInput.value.trim();
                
                // In a real implementation, this would send via AJAX
                const chatMessages = document.getElementById('chatMessages');
                if (chatMessages) {
                    const messageElement = document.createElement('div');
                    messageElement.className = 'message sent';
                    messageElement.innerHTML = `<p>${message}</p>`;
                    chatMessages.appendChild(messageElement);
                    
                    // Scroll to bottom
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
                
                // Clear input
                messageInput.value = '';
            }
        });
    }
    
    // Image upload preview
    const imageInput = document.getElementById('productImage');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('imagePreview');
                    if (preview) {
                        preview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 100%; max-height: 200px;">`;
                    }
                }
                reader.readAsDataURL(file);
            }
        });
    }
    
// Function to generate tutorial
// script.js

document.addEventListener('DOMContentLoaded', () => {
    // If tutorial already exists, show "View Tutorial" button
    if (productData.hasTutorial && tutorialData) {
        document.getElementById('tutorialContainer').style.display = 'block';
    }
});

// Function to load and display the tutorial
function loadTutorial() {
    const container = document.getElementById('tutorialContent');
    if (!container) return;
    container.style.display = 'block';
    // Scroll to tutorial
    container.scrollIntoView({ behavior: 'smooth' });
}

// Function to simulate tutorial generation
function generateTutorial(productId) {
    const btn = document.getElementById('generateTutorialBtn');
    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Generating...`;

    // Simulate API call (replace with actual fetch call to backend)
    setTimeout(() => {
        // Example generated tutorial (replace with API response)
        const generatedTutorial = {
            title: `How to Make ${productData.name}`,
            description: `Step-by-step guide to create your ${productData.name}`,
            estimated_time: "2 hours",
            difficulty: "beginner",
            created_date: new Date().toLocaleDateString(),
            materials_needed: productData.materials.split(", "),
            steps: [
                {
                    step_number: 1,
                    title: "Prepare Materials",
                    description: "Gather all the materials listed above.",
                    tips: ["Double-check quantities", "Keep your workspace clean"]
                },
                {
                    step_number: 2,
                    title: "Start Crafting",
                    description: "Follow the steps carefully to assemble your product.",
                    tips: ["Work slowly", "Use safety equipment if needed"]
                },
                {
                    step_number: 3,
                    title: "Finish and Review",
                    description: "Finalize your product and check for mistakes.",
                    tips: ["Take photos", "Share your creation!"]
                }
            ]
        };

        // Inject tutorial into page
        tutorialData = generatedTutorial;
        productData.hasTutorial = true;

        // Replace container HTML
        const containerDiv = document.getElementById('tutorialContainer');
        containerDiv.innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <i class="fas fa-wand-magic-sparkles" style="font-size: 4rem; color: var(--accent); margin-bottom: 20px;"></i>
                <h3>AI Tutorial Generated</h3>
                <p style="color: #666;">Click the button below to view the step-by-step tutorial</p>
                <button class="btn btn-primary" onclick="loadTutorial()" style="margin-top: 20px;">
                    <i class="fas fa-eye"></i> View Tutorial
                </button>
            </div>
        `;
        
        // Optionally also render the tutorial content
        const tutorialContent = document.getElementById('tutorialContent');
        if (tutorialContent) {
            renderTutorialContent(generatedTutorial);
            tutorialContent.style.display = 'none';
        }

    }, 1500); // Simulate 1.5s API call
}

// Function to render tutorial content
function renderTutorialContent(tutorial) {
    const container = document.getElementById('tutorialContent');
    if (!container) return;

    // Difficulty color
    let bgColor = tutorial.difficulty === 'beginner' ? 'var(--success)' :
                  tutorial.difficulty === 'intermediate' ? 'var(--warning)' : 'var(--danger)';

    let materialsHTML = tutorial.materials_needed.map(m => `
        <span style="background: var(--light); padding: 8px 15px; border-radius: 20px;">
            <i class="fas fa-check-circle" style="color: var(--success);"></i> ${m}
        </span>
    `).join("");

    let stepsHTML = tutorial.steps.map(step => `
        <div style="background: var(--light); padding: 25px; border-radius: 8px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <div style="background: var(--accent); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                    ${step.step_number}
                </div>
                <h4 style="margin: 0; color: var(--dark);">${step.title}</h4>
            </div>
            <p style="color: #666; margin-bottom: 15px; line-height: 1.6;">${step.description}</p>
            ${step.tips && step.tips.length ? `
            <div style="background: rgba(255, 255, 255, 0.5); padding: 15px; border-radius: 6px; border-left: 4px solid var(--accent);">
                <h5 style="margin: 0 0 10px 0; color: var(--dark);">
                    <i class="fas fa-lightbulb" style="color: var(--warning);"></i> Pro Tips
                </h5>
                <ul style="margin: 0; color: #666;">
                    ${step.tips.map(t => `<li style="margin-bottom: 5px;">${t}</li>`).join("")}
                </ul>
            </div>` : ""}
        </div>
    `).join("");

    container.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 class="section-title">${tutorial.title}</h2>
            <p style="font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 30px;">
                ${tutorial.description}
            </p>
            <div style="margin-bottom: 30px;">
                <h3 style="margin-bottom: 20px;">Materials Needed</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    ${materialsHTML}
                </div>
            </div>
            <div style="margin-bottom: 30px;">
                <h3 style="margin-bottom: 20px;">Step-by-Step Instructions</h3>
                <div class="tutorial-steps">
                    ${stepsHTML}
                </div>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h3 style="margin-bottom: 15px;">Tutorial Information</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div>
                        <strong>Estimated Time:</strong>
                        <p style="margin: 5px 0 0 0; color: #666;">${tutorial.estimated_time}</p>
                    </div>
                    <div>
                        <strong>Difficulty Level:</strong>
                        <p style="margin: 5px 0 0 0; color: #666;">
                            <span style="background: ${bgColor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">
                                ${tutorial.difficulty.charAt(0).toUpperCase() + tutorial.difficulty.slice(1)}
                            </span>
                        </p>
                    </div>
                    <div>
                        <strong>Generated On:</strong>
                        <p style="margin: 5px 0 0 0; color: #666;">${tutorial.created_date}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Function to share tutorial (simple example)
function shareTutorial() {
    if (!tutorialData) return alert("No tutorial to share yet!");
    const shareText = `${tutorialData.title}\n${tutorialData.description}`;
    navigator.clipboard.writeText(shareText).then(() => {
        alert("Tutorial text copied to clipboard!");
    });
}

// AJAX helper functions
function ajaxRequest(url, method, data, successCallback, errorCallback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (successCallback) successCallback(response);
                } catch (e) {
                    if (successCallback) successCallback(xhr.responseText);
                }
            } else {
                if (errorCallback) errorCallback(xhr.status, xhr.responseText);
            }
        }
    };
    
    xhr.send(JSON.stringify(data));
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltipElement = document.createElement('div');
            tooltipElement.className = 'tooltip';
            tooltipElement.textContent = tooltipText;
            document.body.appendChild(tooltipElement);
            
            const rect = this.getBoundingClientRect();
            tooltipElement.style.top = (rect.top - tooltipElement.offsetHeight - 10) + 'px';
            tooltipElement.style.left = (rect.left + (rect.width - tooltipElement.offsetWidth) / 2) + 'px';
            
            this.addEventListener('mouseleave', function() {
                document.body.removeChild(tooltipElement);
            });
        });
    });
}

// Initialize image lazy loading
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        // Options for the observer: load 200px before entering viewport
        const observerOptions = {
            rootMargin: '200px 0px',
            threshold: 0.01
        };

        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;

                    // Optional: Add a loading state class if needed
                    // img.classList.add('loading');

                    img.onload = function() {
                        // Mark the image as loaded for CSS transitions
                        img.classList.add('loaded');
                    };
                    img.onerror = function() {
                        // Provide a fallback on error
                        img.src = '/images/fallback.jpg';
                    };

                    // Swap the data-src for the real src
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        }, observerOptions); // Pass the options here
        
        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for older browsers: eagerly load all images
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// Don't forget to call the function!
// initLazyLoading(); or call it on DOMContentLoaded

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    initLazyLoading();

});





