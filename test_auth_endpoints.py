import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add project root to sys.path to allow importing main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

# --- Mock Data ---
MOCK_USER_ID = 1
MOCK_EMAIL = "test@example.com"
MOCK_USERNAME = "testuser"
MOCK_PASSWORD = "password123"
MOCK_HASHED_PASSWORD = "hashed_password_123"
MOCK_TOKEN = "mock_access_token"
MOCK_RESET_TOKEN = "mock_reset_token"

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = MOCK_USER_ID
    user.email = MOCK_EMAIL
    user.username = MOCK_USERNAME
    user.hashed_password = MOCK_HASHED_PASSWORD
    user.is_active = True
    user.is_superuser = False
    user.role = "user"
    user.reset_token = "hashed_otp"
    # Set reset token to expire in the future
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    return user


# --- Registration Tests ---
def test_register_success(mock_user):
    """Test successful user registration."""
    with patch("api.v1.auth.crud_user.get_user_by_email") as mock_get_user_by_email, \
         patch("api.v1.auth.crud_user.get_user_by_username") as mock_get_user_by_username, \
         patch("api.v1.auth.crud_user.create_user") as mock_create_user:
        
        mock_get_user_by_email.return_value = None
        mock_get_user_by_username.return_value = None
        mock_create_user.return_value = mock_user

        payload = {"email": MOCK_EMAIL, "username": MOCK_USERNAME, "password": MOCK_PASSWORD}
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user"]["email"] == MOCK_EMAIL
        assert data["user"]["username"] == MOCK_USERNAME


# --- Login Tests ---

def test_login_success(mock_user):
    """Test successful login returns access token."""
    with patch("api.v1.auth.crud_user.get_user_by_email") as mock_get_user, \
         patch("api.v1.auth.verify_password") as mock_verify, \
         patch("api.v1.auth.create_access_token") as mock_create_token:
        
        mock_get_user.return_value = mock_user
        mock_verify.return_value = True
        mock_create_token.return_value = MOCK_TOKEN
        
        payload = {"email": MOCK_EMAIL, "password": MOCK_PASSWORD}
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["token"] == MOCK_TOKEN
        assert data["user"]["email"] == MOCK_EMAIL

def test_login_incorrect_password(mock_user):
    """Test login fails with incorrect password."""
    with patch("api.v1.auth.crud_user.get_user_by_email") as mock_get_user, \
         patch("api.v1.auth.verify_password") as mock_verify:
        
        mock_get_user.return_value = mock_user
        mock_verify.return_value = False # Simulate wrong password
        
        payload = {"email": MOCK_EMAIL, "password": "wrong_password"}
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"


# --- Forgot Password Tests ---

def test_forgot_password_email_sent(mock_user):
    """Test forgot password triggers token generation and 'sends' email."""
    with patch("api.v1.auth.crud_user.get_user_by_email") as mock_get_user, \
         patch("api.v1.auth.crud_otp.invalidate_active_otps") as mock_invalidate, \
         patch("api.v1.auth.crud_otp.create_otp_code") as mock_create_otp:
        
        mock_get_user.return_value = mock_user
        
        response = client.post("/api/v1/auth/forgot-password", json={"email": MOCK_EMAIL})
        
        assert response.status_code == 200
        assert response.json()["message"] == "If the email exists, an OTP has been sent."
        mock_invalidate.assert_called_once()
        mock_create_otp.assert_called_once()

def test_forgot_password_user_not_found():
    """Test forgot password returns success message even if user doesn't exist (security)."""
    with patch("api.v1.auth.crud_user.get_user_by_email") as mock_get_user:
        mock_get_user.return_value = None
        
        response = client.post("/api/v1/auth/forgot-password", json={"email": "unknown@example.com"})
        
        assert response.status_code == 200
        assert response.json()["message"] == "If the email exists, an OTP has been sent."

# --- Reset Password Tests ---

def test_reset_password_success(mock_user):
    """Test password reset with valid token."""
    with patch("api.v1.auth.crud_user.get_user_by_reset_token") as mock_get_by_reset, \
         patch("api.v1.auth.crud_user.update_user_password") as mock_update_pwd, \
         patch("api.v1.auth.crud_user.update_user_reset_token") as mock_clear_reset:
        
        mock_user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        mock_get_by_reset.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/reset-password", 
            headers={"X-Reset-Token": MOCK_RESET_TOKEN},
            json={"new_password": "new_secure_password", "confirm_password": "new_secure_password"},
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Password has been reset successfully."
        mock_update_pwd.assert_called_once()
        mock_clear_reset.assert_called_once()


def test_reset_password_expired_token(mock_user):
    """Test password reset fails with expired token."""
    mock_user.reset_token_expires = datetime.utcnow() - timedelta(hours=1) # Expired
    
    with patch("api.v1.auth.crud_user.get_user_by_reset_token") as mock_get_by_reset:
        mock_get_by_reset.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/reset-password", 
            headers={"X-Reset-Token": MOCK_RESET_TOKEN},
            json={"new_password": "new_secure_password", "confirm_password": "new_secure_password"},
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token."


def test_otp_verify_success(mock_user):
    """Test OTP verify returns reset token."""
    with patch("api.v1.auth.crud_user.get_user_by_email") as mock_get_by_email, \
         patch("api.v1.auth.crud_otp.get_latest_active_otp") as mock_get_otp, \
         patch("api.v1.auth.crud_user.update_user_reset_token") as mock_update_reset, \
         patch("api.v1.auth.crud_otp.mark_used") as mock_mark_used:
        
        mock_get_by_email.return_value = mock_user
        mock_otp = MagicMock()
        mock_otp.id = 1
        mock_otp.otp_hash = "hashed_otp"
        mock_otp.expires_at = datetime.utcnow() + timedelta(hours=1)
        mock_otp.attempts = 0
        mock_get_otp.return_value = mock_otp
        
        with patch("api.v1.auth.hashlib.sha256") as mock_sha:
            mock_sha.return_value.hexdigest.return_value = "hashed_otp"
            response = client.post(
                "/api/v1/auth/otp/verify",
                json={"email": MOCK_EMAIL, "otp": "123456"},
            )
        
        assert response.status_code == 200
        assert response.json()["message"] == "OTP verified successfully."
        assert "reset_token" in response.json()
        mock_update_reset.assert_called_once()
        mock_mark_used.assert_called_once()
