"""
Enhanced Authentication Manager for Prompt Training App
Handles user registration, login validation, and account verification
"""

import asyncio
import streamlit as st
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timezone

from database.service import UserService, UserData
from database.config import init_database, close_database

logger = logging.getLogger(__name__)


class AuthState:
    """Authentication state management"""
    
    @staticmethod
    def init_session_state():
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
        if 'auth_step' not in st.session_state:
            st.session_state.auth_step = 'ldap_check'  # ldap_check -> login/register -> verify -> main_app
        
        # Registration state
        if 'pending_registration' not in st.session_state:
            st.session_state.pending_registration = None
        if 'registration_complete' not in st.session_state:
            st.session_state.registration_complete = False
        
        # Login state  
        if 'login_step' not in st.session_state:
            st.session_state.login_step = 'ldap_input'  # ldap_input -> password_input -> verify


class AuthenticationManager:
    """Enhanced authentication manager with onboarding flow"""
    
    def __init__(self):
        self.user_service = UserService()
        self.auth_state = AuthState()
        
    async def check_user_exists(self, ldap_id: str) -> Optional[UserData]:
        """Check if user exists by LDAP ID"""
        try:
            return await self.user_service.get_user_by_ldap_id(ldap_id.strip())
        except Exception as e:
            logger.error(f"Error checking user existence: {e}")
            return None
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    async def register_user(self, ldap_id: str, nickname: str, email: str, password: str, group: str) -> Optional[UserData]:
        """Register a new user"""
        try:
            # Validate all fields are provided
            if not all([ldap_id.strip(), nickname.strip(), email.strip(), password.strip(), group.strip()]):
                st.error("All fields are mandatory")
                return None
            
            # Check if user already exists
            existing_user = await self.check_user_exists(ldap_id.strip())
            if existing_user:
                st.error(f"User with LDAP ID '{ldap_id}' already exists")
                return None
            
            # Create user data
            user_data = UserData(
                ldap_id=ldap_id.strip(),
                username=nickname.strip(),
                password_hash=self._hash_password(password),
                email_address=email.strip(),
                user_group=group.strip()
            )
            
            # Create user in database
            user = await self.user_service.create_user(user_data)
            
            if user:
                st.success(f"✅ Account created successfully for {nickname}!")
                return user
            else:
                st.error("Failed to create account")
                return None
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            st.error(f"Registration failed: {str(e)}")
            return None
    
    async def authenticate_user(self, ldap_id: str, password: str) -> Optional[UserData]:
        """Authenticate user with LDAP ID and password"""
        try:
            user = await self.check_user_exists(ldap_id.strip())
            if user:
                user_password_hash = self._hash_password(password)
                if user.password_hash == user_password_hash:
                    # Update last login
                    await self.user_service.update_user_last_login(user.id)
                    return user
                else:
                    st.error("Invalid password")
                    return None
            else:
                st.error(f"User '{ldap_id}' not found")
                return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            st.error(f"Authentication failed: {str(e)}")
            return None
    
    async def render_ldap_check_page(self):
        """Render LDAP ID check page"""
        st.title("🔐 Login to Prompt Training Lab")
        st.markdown("*Enter your LDAP ID to begin*")
        
        # Show current step for debugging (only if debug mode is enabled)
        # Remove debug display from main UI to avoid confusion
        
        with st.form("ldap_check_form"):
            ldap_id = st.text_input(
                "LDAP ID", 
                placeholder="e.g., john.doe, jane.smith", 
                help="Your corporate LDAP identifier"
            )
            
            check_ldap = st.form_submit_button("Check Account", use_container_width=True)
            
            if check_ldap and ldap_id:
                with st.spinner("Checking account..."):
                    # Run async function
                    user = await self.check_user_exists(ldap_id)
                    
                    if user:
                        st.session_state.found_user = user
                        st.session_state.auth_step = "login"
                        st.session_state.login_ldap_id = ldap_id
                        st.rerun()
                    else:
                        # Store the LDAP ID for registration
                        st.session_state.temp_ldap_id = ldap_id
                        st.rerun()
        
        # Handle new user detection (outside the form)
        if st.session_state.get('temp_ldap_id') and not st.session_state.get('temp_ldap_processed', False):
            st.info("👤 New User Detected")
            st.markdown("This LDAP ID doesn't exist in our system.")
            st.markdown(f"**LDAP ID:** `{st.session_state.temp_ldap_id}`")
            st.markdown("Would you like to register with this LDAP ID?")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("✅ Yes, Register Now", use_container_width=True, type="primary"):
                    st.session_state.auth_step = "register"
                    st.session_state.new_ldap_id = st.session_state.temp_ldap_id
                    st.session_state.temp_ldap_processed = True
                    st.rerun()
            
            with col2:
                if st.button("❌ No, Cancel", use_container_width=True):
                    # Clear temp state
                    del st.session_state.temp_ldap_id
                    st.session_state.temp_ldap_processed = False
                    st.rerun()
    
    async def render_registration_page(self):
        """Render user registration page"""
        st.title("📝 Create Your Account")
        st.markdown("*Complete your profile to get started*")
        
        # Pre-fill LDAP ID if coming from login check
        default_ldap = st.session_state.get('new_ldap_id', '')
        st.info(f"Ready to register user: **{default_ldap}**")
        
        with st.form("registration_form"):
            st.markdown("**All fields are mandatory**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                ldap_id = st.text_input(
                    "LDAP ID *", 
                    value=default_ldap,
                    placeholder="e.g., john.doe",
                    help="Your corporate LDAP identifier",
                    disabled=bool(default_ldap)  # Disable if pre-filled
                )
                
                nickname = st.text_input(
                    "Display Name *", 
                    placeholder="e.g., John Doe",
                    help="Your preferred display name"
                )
                
                email = st.text_input(
                    "Email Address *", 
                    placeholder="john.doe@company.com",
                    help="Your corporate email address"
                )
            
            with col2:
                password = st.text_input(
                    "Password *", 
                    type="password",
                    placeholder="Create a secure password",
                    help="Choose a strong password"
                )
                
                confirm_password = st.text_input(
                    "Confirm Password *", 
                    type="password",
                    placeholder="Re-enter your password"
                )
                
                group_options = ["GBS", "T&E", "PCC"]
                group = st.selectbox(
                    "Department/Group *", 
                    options=[""] + group_options,
                    help="Your organizational group"
                )
            
            # Password validation
            if password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
            
            submit_registration = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit_registration:
                # Validate all fields
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif not all([ldap_id.strip(), nickname.strip(), email.strip(), password.strip(), group.strip()]):
                    st.error("All fields are mandatory")
                else:
                    with st.spinner("Creating your account..."):
                        user = await self.register_user(ldap_id, nickname, email, password, group)
                        
                        if user:
                            st.session_state.pending_registration = user
                            st.session_state.auth_step = "verify_login"
                            st.session_state.registration_ldap_id = ldap_id
                            st.rerun()
        
        # Back button
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("← Back to Login Check", use_container_width=True):
                st.session_state.auth_step = "ldap_check"
                st.session_state.new_ldap_id = None
                st.rerun()
        
        with col2:
            if st.button("🧪 Enable Debug Mode", use_container_width=True):
                st.session_state.debug = True
                st.rerun()
    
    async def render_login_page(self):
        """Render login page for existing users"""
        st.title("🔑 Login to Prompt Training Lab")
        
        user_data = st.session_state.get('found_user')
        if user_data:
            st.info(f"Welcome back, **{user_data.username}**! ({user_data.user_group})")
        
        with st.form("login_form"):
            # Pre-fill LDAP ID
            default_ldap = st.session_state.get('login_ldap_id', '')
            
            ldap_id = st.text_input(
                "LDAP ID", 
                value=default_ldap,
                placeholder="e.g., john.doe"
            )
            
            password = st.text_input(
                "Password", 
                type="password",
                placeholder="Enter your password"
            )
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                login_button = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if login_button and ldap_id and password:
                with st.spinner("Authenticating..."):
                    user = await self.authenticate_user(ldap_id, password)
                    
                    if user:
                        st.success("✅ Login successful!")
                        st.session_state.authenticated = True
                        st.session_state.user_data = user
                        st.session_state.auth_step = "main_app"
                        st.rerun()
        
        # Back button
        if st.button("← Back to Login Check"):
            st.session_state.auth_step = "ldap_check"
            st.session_state.found_user = None
            st.session_state.login_ldap_id = None
            st.rerun()
    
    async def render_verification_login(self):
        """Render verification login page after registration"""
        st.title("✅ Account Created Successfully!")
        
        pending_user = st.session_state.get('pending_registration')
        if pending_user:
            st.success(f"Account created for **{pending_user.username}** ({pending_user.ldap_id})")
        
        st.markdown("Please login again to verify your credentials were saved correctly:")
        
        with st.form("verify_login_form"):
            ldap_id = st.text_input(
                "LDAP ID", 
                value=st.session_state.get('registration_ldap_id', ''),
                placeholder="Enter your LDAP ID to verify"
            )
            
            password = st.text_input(
                "Password", 
                type="password",
                placeholder="Enter the password you just created"
            )
            
            verify_login = st.form_submit_button("Verify Login", type="primary", use_container_width=True)
            
            if verify_login and ldap_id and password:
                with st.spinner("Verifying credentials..."):
                    user = await self.authenticate_user(ldap_id, password)
                    
                    if user:
                        st.success("🎉 Account verification successful!")
                        st.markdown("You can now access the Prompt Training Lab!")
                        
                        st.session_state.authenticated = True
                        st.session_state.user_data = user
                        st.session_state.auth_step = "main_app"
                        st.rerun()
                    else:
                        st.error("❌ Verification failed. Please check your credentials")
        
        # Back button
        if st.button("← Back to Registration"):
            st.session_state.auth_step = "register"
            st.session_state.pending_registration = None
            st.rerun()
    
    async def render_main_app_access_page(self):
        """Render page after successful authentication"""
        user_data = st.session_state.user_data
        
        st.title("🎯 Prompt Training Lab")
        st.markdown("*Welcome to advanced prompt engineering training*")
        
        st.success(f"✅ Logged in as **{user_data.username}**")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            **Account Details:**
            - **LDAP ID:** {user_data.ldap_id}  
            - **Name:** {user_data.username}
            - **Email:** {user_data.email_address}
            - **Group:** {user_data.user_group}
            - **Member since:** {user_data.created_at.strftime('%B %d, %Y') if user_data.created_at else 'Recently'}
            """)
        
        with col2:
            if st.button("🚪 Sign Out", use_container_width=True):
                # Clear authentication state
                st.session_state.authenticated = False
                st.session_state.user_data = None
                st.session_state.auth_step = "ldap_check"
                
                # Clear auth-related session state
                for key in ['found_user', 'new_ldap_id', 'login_ldap_id', 'pending_registration', 
                           'registration_complete', 'registration_ldap_id', 'debug']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.rerun()
        
        st.markdown("---")
        
        # Proceed to main app buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 Start Training", use_container_width=True, type="primary"):
                st.session_state.proceed_app = True
                st.rerun()
        
        with col2:
            if st.button("📊 View Progress", use_container_width=True):
                st.session_state.view_progress_app = True
                st.rerun()
        
        with col3:
            if st.button("🏆 Leaderboard", use_container_width=True):
                st.session_state.view_leaderboard_app = True
                st.rerun()
    
    async def run_auth_flow(self):
        """Main authentication flow controller"""
        await init_database()
        
        try:
            # Initialize session state
            AuthState.init_session_state()
            
            current_step = st.session_state.auth_step
            
            # Render appropriate page based on current step
            if current_step == "ldap_check":
                await self.render_ldap_check_page()
            
            elif current_step == "register":
                await self.render_registration_page()
            
            elif current_step == "login":
                await self.render_login_page()
            
            elif current_step == "verify_login":
                await self.render_verification_login()
            
            elif current_step == "main_app":
                await self.render_main_app_access_page()
            
            else:
                # Default fallback
                st.session_state.auth_step = "ldap_check"
                st.rerun()
        
        finally:
            # Don't close database here as we might continue to main app
            pass
    
    async def get_authenticated_user(self) -> Optional[UserData]:
        """Get currently authenticated user"""
        if st.session_state.get('authenticated') and st.session_state.get('user_data'):
            return st.session_state.user_data
        return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def require_auth(self):
        """Decorator to require authentication"""
        if not self.is_authenticated():
            st.warning("🔐 Please login to access this page")
            if st.button("Go to Login"):
                st.session_state.auth_step = "ldap_check"
                st.rerun()
            st.stop()


# Global auth manager instance
auth_manager = AuthenticationManager()


# Convenience functions for easy integration
async def run_auth_flow():
    """Run the authentication flow"""
    auth_manager = AuthenticationManager()
    await auth_manager.run_auth_flow()


def require_authentication():
    """Require user to be authenticated"""
    auth_manager = AuthenticationManager()
    auth_manager.require_auth()


def get_current_user() -> Optional[UserData]:
    """Get current authenticated user synchronously"""
    return st.session_state.get('user_data') if st.session_state.get('authenticated') else None


def is_logged_in() -> bool:
    """Check if user is logged in"""
    return st.session_state.get('authenticated', False)
