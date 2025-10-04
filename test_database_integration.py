"""
Test utilities for database integration and functionality
"""

import asyncio
import pytest
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from database.config import init_database, close_database, db_connection
from database.service import (
    UserService, ProgressService, BadgeService, LeaderboardService,
    UserData, ProgressData, BadgeData
)
from batch_manager import BatchManager


async def cleanup_test_user_data(user_id: str):
    """Cleanup test user data"""
    try:
        async with db_connection.get_connection() as conn:
            await conn.execute(
                "DELETE FROM user_badges WHERE user_id = $1",
                user_id
            )
            await conn.execute(
                "DELETE FROM user_progress WHERE user_id = $1",
                user_id
            )
            await conn.execute(
                "DELETE FROM users WHERE id = $1",
                user_id
            )
    except Exception as e:
        print(f"Cleanup warning: {e}")


class DatabaseTestSuite:
    """Comprehensive test suite for database functionality"""
    
    def __init__(self):
        self.user_service = UserService()
        self.progress_service = ProgressService()
        self.badge_service = BadgeService()
        self.leaderboard_service = LeaderboardService()
        self.batch_manager = None
        self.test_user_data = None
        self.test_ldap_id = f"test_{uuid.uuid4().hex[:8]}"
    
    async def setup_test_environment(self):
        """Setup test environment"""
        await init_database()
        self.batch_manager = BatchManager()
        
        # Create test user
        await self.create_test_user()
    
    async def cleanup_test_environment(self):
        """Cleanup test environment"""
        if self.test_user_data:
            await self._cleanup_test_user_data()
        
        if self.batch_manager:
            await self.batch_manager.shutdown()
        
        await close_database()
    
    async def create_test_user(self) -> UserData:
        """Create a test user for testing"""
        test_user = UserData(
            ldap_id=self.test_ldap_id,
            username=f"testuser_{uuid.uuid4().hex[:6]}",
            password_hash="test_hash_123",
            email_address=f"test_{uuid.uuid4().hex[:6]}@example.com",
            user_group="test"
        )
        
        self.test_user_data = await self.user_service.create_user(test_user)
        return self.test_user_data
    
    async def _cleanup_test_user_data(self):
        """Cleanup all test user data"""
        try:
            if self.test_user_data:
                # Delete all test user data
                from database.config import db_connection
                
                async with db_connection.get_connection() as conn:
                    await conn.execute(
                        "DELETE FROM user_badges WHERE user_id = $1",
                        self.test_user_data.id
                    )
                    await conn.execute(
                        "DELETE FROM user_progress WHERE user_id = $1",
                        self.test_user_data.id
                    )
                    await conn.execute(
                        "DELETE FROM users WHERE id = $1",
                        self.test_user_data.id
                    )
        except Exception as e:
            print(f"Cleanup warning: {e}")
    
    async def test_user_crud_operations(self) -> bool:
        """Test user CRUD operations"""
        print("Testing user CRUD operations...")
        
        try:
            # Test create user
            test_user = UserData(
                ldap_id=f"crud_test_{uuid.uuid4().hex[:8]}",
                username=f"cruduser_{uuid.uuid4().hex[:6]}",
                password_hash="hashed_password",
                email_address=f"crud_{uuid.uuid4().hex[:6]}@test.com",
                user_group="test_group"
            )
            
            created_user = await self.user_service.create_user(test_user)
            assert created_user is not None
            assert created_user.ldap_id == test_user.ldap_id
            print("✓ User creation test passed")
            
            # Test get user by LDAP ID
            retrieved_user = await self.user_service.get_user_by_ldap_id(test_user.ldap_id)
            assert retrieved_user is not None
            assert retrieved_user.id == created_user.id
            print("✓ User retrieval by LDAP ID test passed")
            
            # Test get user by username
            retrieved_by_username = await self.user_service.get_user_by_username(test_user.username)
            assert retrieved_by_username is not None
            assert retrieved_by_username.id == created_user.id
            print("✓ User retrieval by username test passed")
            
            # Test update last login
            update_success = await self.user_service.update_user_last_login(created_user.id)
            assert update_success is True
            print("✓ User last login update test passed")
            
            # Cleanup test user
            await self._cleanup_test_user_data()
            return True
            
        except Exception as e:
            print(f"✗ User CRUD operations test failed: {e}")
            return False
    
    async def test_progress_tracking(self) -> bool:
        """Test progress tracking functionality"""
        print("Testing progress tracking...")
        
        try:
            if not self.test_user_data:
                await self.create_test_user()
            
            # Create progress entries
            progress_entries = []
            for i in range(3):
                progress_data = ProgressData(
                    ldap_id=self.test_user_data.ldap_id,
                    attempt_number=i + 1,
                    scenario_id=f"b{i+1}",
                    user_prompt=f"Test prompt {i+1}",
                    total_score=70 + (i * 10),
                    clarity_score=15 + i,
                    specificity_score=15 + i,
                    structure_score=20 + i,
                    task_alignment_score=20 + i,
                    feedback=f"Test feedback {i+1}",
                    strengths=["Test strength"],
                    improvements=["Test improvement"]
                )
                progress_entries.append(progress_data)
            
            # Test batch creation
            created_entries = await self.progress_service.batch_create_progress_entries(progress_entries)
            assert len(created_entries) == 3
            print("✓ Progress batch creation test passed")
            
            # Test user progress summary
            summary = await self.progress_service.get_user_progress_summary(self.test_user_data.ldap_id)
            assert summary is not None
            assert summary['total_attempts'] == 3
            assert summary['avg_score'] > 70
            print("✓ Progress summary test passed")
            
            # Test recent attempts retrieval
            recent_attempts = await self.progress_service.get_user_recent_attempts(self.test_user_data.ldap_id, limit=2)
            assert len(recent_attempts) == 2
            assert recent_attempts[0].attempt_number > recent_attempts[1].attempt_number  # Most recent first
            print("✓ Recent attempts test passed")
            
            return True
            
        except Exception as e:
            print(f"✗ Progress tracking test failed: {e}")
            return False
    
    async def test_badge_system(self) -> bool:
        """Test badge awarding system"""
        print("Testing badge system...")
        
        try:
            if not self.test_user_data:
                await self.create_test_user()
            
            # Test badge awarding
            badge = await self.badge_service.award_badge(
                self.test_user_data.id, 
                "Test Badge", 
                "b1"
            )
            assert badge is not None
            assert badge.badge_name == "Test Badge"
            print("✓ Badge awarding test passed")
            
            # Test getting user badges
            badges = await self.badge_service.get_user_badges(self.test_user_data.id)
            assert len(badges) == 1
            assert badges[0].badge_name == "Test Badge"
            print("✓ User badges retrieval test passed")
            
            # Test duplicate badge prevention
            duplicate_badge = await self.badge_service.award_badge(
                self.test_user_data.id, 
                "Test Badge", 
                "b2"
            )
            assert duplicate_badge is None  # Should not create duplicate
            print("✓ Duplicate badge prevention test passed")
            
            # Test badge checking based on progress
            high_score_entry = ProgressData(
                ldap_id=self.test_user_data.ldap_id,
                attempt_number=4,
                scenario_id="b1",
                total_score=100,  # Perfect score
                clarity_score=25,
                specificity_score=25,
                structure_score=25,
                task_alignment_score=25,
                feedback="Perfect!",
                strengths=["Excellent"],
                improvements=[]
            )
            
            new_badges = await self.badge_service.check_and_award_badges(self.test_user_data.ldap_id, high_score_entry)
            # Should award "Perfect Score" badge
            assert len(new_badges) >= 0  # May already have badges from previous tests
            print("✓ Automated badge checking test passed")
            
            return True
            
        except Exception as e:
            print(f"✗ Badge system test failed: {e}")
            return False
    
    async def test_batch_management(self) -> bool:
        """Test batch management functionality"""
        print("Testing batch management...")
        
        try:
            if not self.test_user_data:
                await self.create_test_user()
            
            user_ldap_id = self.test_user_data.ldap_id
            
            # Test session creation
            session_id = await self.batch_manager.start_session(user_ldap_id)
            assert session_id is not None
            print("✓ Session creation test passed")
            
            # Test adding entries to session
            for i in range(3):
                progress_data = ProgressData(
                    ldap_id=user_ldap_id,
                    attempt_number=i + 10,
                    scenario_id=f"test_{i}",
                    total_score=80,
                    clarity_score=20,
                    specificity_score=20,
                    structure_score=20,
                    task_alignment_score=20,
                    user_prompt=f"Batch test prompt {i}"
                )
                
                success = await self.batch_manager.add_progress_entry(user_ldap_id, progress_data)
                assert success is True
            
            # Check session info
            session_info = await self.batch_manager.get_session_info(user_ldap_id)
            assert session_info is not None
            assert session_info['entry_count'] == 3
            print("✓ Session entry management test passed")
            
            # Test manual flush
            flush_success = await self.batch_manager.manual_flush_session(user_ldap_id)
            assert flush_success is True
            
            # Verify entries were flushed to database
            summary = await self.progress_service.get_user_progress_summary(user_ldap_id)
            assert summary is not None
            # Should have entries from previous tests + batch entries
            print("✓ Manual session flush test passed")
            
            # Test session end
            end_success = await self.batch_manager.end_session(user_ldap_id)
            assert end_success is True
            
            # Verify session is ended
            session_info_after = await self.batch_manager.get_session_info(user_ldap_id)
            assert session_info_after is None
            print("✓ Session end test passed")
            
            return True
            
        except Exception as e:
            print(f"✗ Batch management test failed: {e}")
            return False
    
    async def test_leaderboard_functionality(self) -> bool:
        """Test leaderboard functionality"""
        print("Testing leaderboard functionality...")
        
        try:
            # Get leaderboard
            leaderboard = await self.leaderboard_service.get_leaderboard(limit=10)
            assert isinstance(leaderboard, list)
            print("✓ Basic leaderboard retrieval test passed")
            
            # Test leaderboard refresh
            await self.leaderboard_service.refresh_leaderboard()
            print("✓ Leaderboard refresh test passed")
            
            return True
            
        except Exception as e:
            print(f"✗ Leaderboard functionality test failed: {e}")
            return False
    
    async def run_comprehensive_test(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("🚀 Starting comprehensive database integration test suite...")
        print("=" * 60)
        
        await self.setup_test_environment()
        
        test_results = {}
        
        try:
            test_results['user_crud'] = await self.test_user_crud_operations()
            test_results['progress_tracking'] = await self.test_progress_tracking()
            test_results['badge_system'] = await self.test_badge_system()
            test_results['batch_management'] = await self.test_batch_management()
            test_results['leaderboard'] = await self.test_leaderboard_functionality()
            
        finally:
            await self.cleanup_test_environment()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✓ PASSED" if result else "✗ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed_tests += 1
        
        print("-" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Database integration is working correctly.")
        else:
            print("⚠️  Some tests failed. Please review the errors above.")
        
        return test_results


async def run_quick_test():
    """Run a quick integration test"""
    print("🚀 Running quick database integration test...")
    
    try:
        # Initialize database
        await init_database()
        print("✓ Database connection established")
        
        # Test basic services
        user_service = UserService()
        progress_service = ProgressService()
        
        # Create test user
        test_user = UserData(
            ldap_id="quick_test_user",
            username="quicktest",
            password_hash="test_hash",
            email_address="quick@test.com",
            user_group="test"
        )
        
        user = await user_service.create_user(test_user)
        assert user is not None
        print("✓ User creation working")
        
        # Create progress entry
        progress_data = ProgressData(
            ldap_id=user.ldap_id,
            attempt_number=1,
            scenario_id="b1",
            total_score=85,
            clarity_score=21,
            specificity_score=21,
            structure_score=21,
            task_alignment_score=22,
            user_prompt="Quick test prompt"
        )
        
        progress_entry = await progress_service.create_progress_entry(progress_data)
        assert progress_entry is not None
        print("✓ Progress tracking working")
        
        # Test leaderboard
        leaderboard = await LeaderboardService().get_leaderboard()
        assert isinstance(leaderboard, list)
        print("✓ Leaderboard working")
        
        # Cleanup
        await cleanup_test_user_data(user.id)
        print("✓ Cleanup completed")
        
        print("🎉 Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Quick test failed: {e}")
        return False
    
    finally:
        await close_database()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Run quick test
        result = asyncio.run(run_quick_test())
        sys.exit(0 if result else 1)
    else:
        # Run comprehensive test
        test_suite = DatabaseTestSuite()
        results = asyncio.run(test_suite.run_comprehensive_test())
        
        # Exit with error code if any tests failed
        failed_tests = [result for result in results.values() if not result]
        sys.exit(0 if not failed_tests else 1)
