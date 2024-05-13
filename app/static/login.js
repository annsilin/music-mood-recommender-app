const loginForm = document.getElementById("login-form");

const submitLoginForm = async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                password
            })
        });

        if (response.ok) {
            window.location.replace('/admin');
        } else {
            document.getElementById("error").textContent = "Invalid username or password";
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

loginForm.addEventListener("submit", submitLoginForm);