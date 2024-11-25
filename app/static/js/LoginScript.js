const forgotBtn = document.getElementById('forgotBtn');
const btnSubmit = document.getElementById('loginForm');
const divAlert = document.getElementById('div-alert');
if (btnSubmit) {
    btnSubmit.addEventListener('submit', async (e) => {
        e.preventDefault();
        const emailInput = document.getElementById('EmailInput').value;
        const passwordInput = document.getElementById('PasswordInput').value;
        let data = {
            email: emailInput,
            password: passwordInput
        };
        try {
            const result = await axios.post('/user/check-login/', data, {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            });
            if (result.data.message === 'success') {
                await displayNotification('Login Successful', 'success', divAlert);
                const token = result.data.token;
                const expiryDate = new Date();
                expiryDate.setDate(expiryDate.getDate() + 1);
                const expires = expiryDate.toUTCString();
                document.cookie = `ExpenseToken=${token}; expires=${expires}; path=/`;
                window.location.href = '/expense/MainHome/';
            }
        } catch (error) {
            console.log(error);
            if (error.response.data.message) {
                if (error.response.data.message == 'Failed') {
                    await displayNotification("Invalid Credentials!", 'warning', divAlert);
                } else if (error.response.data.message === 'NotExist') {
                    await displayNotification("User not exist please register yourself first!", 'warning', divAlert);
                }
                else {
                    await displayNotification(error.response.data.message, 'danger', divAlert);
                }
            }
            else {
                await displayNotification("Internal Server Error!", 'danger', divAlert);
            }
        }
    });
}

function displayNotification(message, type, container) {
    return new Promise((resolve) => {
        const notificationDiv = document.createElement('div');
        notificationDiv.className = `alert alert-${type}`;
        notificationDiv.textContent = message;
        container.appendChild(notificationDiv);
        setTimeout(() => {
            notificationDiv.remove();
            resolve();
        }, 2000);
    });
}



