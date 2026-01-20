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
         patch("api.v1.auth.crud_user.update_user_reset_token") as mock_update_token:
        
        mock_get_user.return_value = mock_user
        
        response = client.post("/api/v1/auth/forgot-password", json={"email": MOCK_EMAIL})
        
        assert response.status_code == 200
        assert response.json()["message"] == "Password reset link sent successfully."
        mock_update_token.assert_called_once()

def test_forgot_password_user_not_found():
    """Test forgot password returns success message even if user doesn't exist (security)."""
    with patch("api.v1.auth.crud_user.get_user_by_email") as mock_get_user:
        mock_get_user.return_value = None
        
        response = client.post("/api/v1/auth/forgot-password", json={"email": "unknown@example.com"})
        
        assert response.status_code == 404

# --- Reset Password Tests ---

def test_reset_password_success(mock_user):
    """Test password reset with valid token."""
    with patch("api.v1.auth.crud_user.get_user_by_reset_token") as mock_get_by_token, \
         patch("api.v1.auth.crud_user.update_user_password") as mock_update_pwd, \
         patch("api.v1.auth.crud_user.update_user_reset_token") as mock_update_reset_token:
        
        mock_get_by_token.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/reset-password", 
            json={"token": "valid_reset_token", "new_password": "new_secure_password"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Password has been reset successfully."
        mock_update_pwd.assert_called_once()
        mock_update_reset_token.assert_called_once()


def test_reset_password_expired_token(mock_user):
    """Test password reset fails with expired token."""
    mock_user.reset_token_expires = datetime.utcnow() - timedelta(hours=1) # Expired
    
    with patch("api.v1.auth.crud_user.get_user_by_reset_token") as mock_get_by_token:
        mock_get_by_token.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/reset-password", 
            json={"token": "expired_token", "new_password": "new_secure_password"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token."