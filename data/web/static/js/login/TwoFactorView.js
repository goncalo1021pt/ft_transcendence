export class TwofactorView extends BaseComponent {
    constructor() {
        super('/two-factor-view/');
    }

    async onIni() {
        // Fetch the QR code from the backend
        try {
            const response = await fetch('/twoFactor/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('Failed to fetch QR code');
            }

            const data = await response.json();

            // Update the QR code image source
            const qrCodeImage = this.querySelector('#qr-code');
            qrCodeImage.src = `data:image/png;base64,${data.qr_image}`;
        } catch (error) {
            console.error('Error fetching QR code:', error);
            // alert('Failed to load the QR code. Please try again.');
        }

        // Add event listener for the "Next" button
        const nextButton = this.querySelector('#next-button');
        nextButton.addEventListener('click', () => {
            // Hide the QR code container and "Next" button
            this.querySelector('#qrcode-container').style.display = 'none';
            nextButton.style.display = 'none';

            // Show the 2FA code input container
            this.querySelector('#two-factor-container').style.display = 'block';
        });
        const verifyButton = this.querySelector('#verify-button');
        verifyButton.addEventListener('click', async () => {
            const otpToken = this.querySelector('#two-factor-code-input').value.trim();
            if (!otpToken || otpToken.length !== 6) {
                alert('Please enter the 2FA code.');
                return;
            }
            try {
                const response = await fetch('/verify_2fa_enable/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'), // Ensure CSRF token is included
                    },
                    body: JSON.stringify({ otp_token: otpToken }),
            
                });

                const data = await response.json();

                if (response.ok) {
                    window.location.href = '#/profile/'; // Redirect to the profile page
                } else {
                    console.error('Failed to verify 2FA code.');
                }
            } catch (error) {
                console.error('Error verifying 2FA code:', error);
                alert('An error occurred while verifying the 2FA code. Please try again.');
            }
        });     
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find((row) => row.startsWith(name + '='))
        ?.split('=')[1];
    return cookieValue || '';
}

customElements.define('two-factor-view', TwofactorView);