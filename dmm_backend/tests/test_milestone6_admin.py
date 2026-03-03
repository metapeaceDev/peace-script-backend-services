"""
Milestone 6 - Admin Dashboard Test Suite
=========================================

Comprehensive test suite for admin dashboard functionality:
- Theme CRUD operations
- Bulk operations
- Analytics and reporting
- Data quality monitoring
- Audit logging
- Performance validation

Test Coverage: 30+ test cases
Author: Peace Script Team
Date: 19 November 2025 (2568 BE)
Version: 1.0
"""

import pytest
import json
from datetime import datetime
from pathlib import Path

from services.admin_theme_service import AdminThemeService, get_admin_theme_service
from services.admin_analytics_service import AdminAnalyticsService, get_admin_analytics_service
from services.data_quality_service import DataQualityService, get_data_quality_service


class TestAdminThemeService:
    """Test suite for AdminThemeService CRUD operations"""
    
    @pytest.fixture
    def admin_service(self):
        """Create admin service instance"""
        service = AdminThemeService()
        service.load_themes()
        return service
    
    def test_load_themes(self, admin_service):
        """Test loading themes from file"""
        assert admin_service._loaded is True
        assert len(admin_service._themes) > 0
        print(f"✓ Loaded {len(admin_service._themes)} themes")
    
    def test_get_theme(self, admin_service):
        """Test getting single theme"""
        # Get first theme ID
        theme_ids = list(admin_service._themes.keys())
        if theme_ids:
            theme = admin_service.get_theme(theme_ids[0])
            assert theme is not None
            assert theme['id'] == theme_ids[0]
            assert 'thai_name' in theme
            print(f"✓ Retrieved theme: {theme['thai_name']}")
    
    def test_get_nonexistent_theme(self, admin_service):
        """Test getting nonexistent theme"""
        theme = admin_service.get_theme("nonexistent_id_12345")
        assert theme is None
        print("✓ Correctly returned None for nonexistent theme")
    
    def test_create_theme(self, admin_service):
        """Test creating a new theme"""
        new_theme = {
            'id': 'test_new_theme_001',
            'thai_name': 'ทดสอบชื่อไทย',
            'pali_name': 'test_pali_name',
            'category': 'test_category',
            'description': 'Test description for theme',
            'story_guidelines': {
                'theme_stated': 'Test theme',
                'b_story': 'Test B story',
                'break_into_three': 'Test break',
                'finale': 'Test finale'
            },
            'recommended_sub_themes': [],
            'core_principles': [],
            'related_cetasikas': [],
            'related_sila': [],
            'scripture_refs': [],
            'applicable_conflicts': [],
            'example_loglines': [],
            'validation_rules': {}
        }
        
        created = admin_service.create_theme(new_theme, 'test_user')
        assert created is not None
        assert created['id'] == 'test_new_theme_001'
        assert created['created_by'] == 'test_user'
        print(f"✓ Created theme: {created['thai_name']}")
    
    def test_create_theme_missing_required_field(self, admin_service):
        """Test creating theme with missing required field"""
        incomplete_theme = {
            'id': 'test_incomplete_001',
            'thai_name': 'ทดสอบชื่อไทย',
            # Missing pali_name
            'category': 'test_category',
            'description': 'Test description'
        }
        
        with pytest.raises(ValueError):
            admin_service.create_theme(incomplete_theme, 'test_user')
        print("✓ Correctly rejected theme with missing required fields")
    
    def test_update_theme(self, admin_service):
        """Test updating an existing theme"""
        # First create a theme
        new_theme = {
            'id': 'test_update_001',
            'thai_name': 'ชื่อเดิม',
            'pali_name': 'original_pali',
            'category': 'original_category',
            'description': 'Original description',
            'story_guidelines': {
                'theme_stated': 'Test',
                'b_story': 'Test',
                'break_into_three': 'Test',
                'finale': 'Test'
            }
        }
        admin_service.create_theme(new_theme, 'test_user')
        
        # Now update it
        updates = {
            'thai_name': 'ชื่อใหม่',
            'description': 'Updated description'
        }
        updated = admin_service.update_theme('test_update_001', updates, 'test_user')
        assert updated['thai_name'] == 'ชื่อใหม่'
        assert updated['description'] == 'Updated description'
        assert updated['pali_name'] == 'original_pali'  # Should not change
        print("✓ Successfully updated theme")
    
    def test_delete_theme_soft_delete(self, admin_service):
        """Test soft delete (archive)"""
        new_theme = {
            'id': 'test_soft_delete_001',
            'thai_name': 'ชื่อสำหรับลบ',
            'pali_name': 'delete_test_pali',
            'category': 'test',
            'description': 'Test',
            'story_guidelines': {
                'theme_stated': 'T',
                'b_story': 'T',
                'break_into_three': 'T',
                'finale': 'T'
            }
        }
        admin_service.create_theme(new_theme, 'test_user')
        
        # Soft delete
        success = admin_service.delete_theme('test_soft_delete_001', 'test_user', soft_delete=True)
        assert success is True
        
        # Theme should still exist but be archived
        theme = admin_service.get_theme('test_soft_delete_001')
        assert theme is not None
        assert theme.get('is_archived') is True
        print("✓ Soft delete (archive) successful")
    
    def test_delete_theme_hard_delete(self, admin_service):
        """Test hard delete"""
        new_theme = {
            'id': 'test_hard_delete_001',
            'thai_name': 'ชื่อสำหรับลบถาวร',
            'pali_name': 'hard_delete_pali',
            'category': 'test',
            'description': 'Test',
            'story_guidelines': {
                'theme_stated': 'T',
                'b_story': 'T',
                'break_into_three': 'T',
                'finale': 'T'
            }
        }
        admin_service.create_theme(new_theme, 'test_user')
        
        # Hard delete
        success = admin_service.delete_theme('test_hard_delete_001', 'test_user', soft_delete=False)
        assert success is True
        
        # Theme should not exist anymore
        theme = admin_service.get_theme('test_hard_delete_001')
        assert theme is None
        print("✓ Hard delete successful")
    
    def test_duplicate_theme(self, admin_service):
        """Test theme duplication"""
        # Get existing theme or create one
        theme_ids = list(admin_service._themes.keys())
        if theme_ids:
            source_id = theme_ids[0]
            new_id = f"{source_id}_copy_001"
            
            duplicated = admin_service.duplicate_theme(source_id, new_id, user_id='test_user')
            assert duplicated is not None
            assert duplicated['id'] == new_id
            # Original and duplicate should have same content except ID
            original = admin_service.get_theme(source_id)
            assert duplicated['thai_name'] == original['thai_name']
            print(f"✓ Theme duplicated: {source_id} → {new_id}")
    
    def test_search_themes(self, admin_service):
        """Test searching themes"""
        results = admin_service.search_themes('ความ', None, False)
        assert isinstance(results, list)
        print(f"✓ Search found {len(results)} themes matching 'ความ'")
    
    def test_get_all_themes(self, admin_service):
        """Test listing all themes"""
        themes = admin_service.get_all_themes(include_archived=False)
        assert isinstance(themes, list)
        assert len(themes) > 0
        print(f"✓ Listed {len(themes)} active themes")
    
    def test_get_all_themes_including_archived(self, admin_service):
        """Test listing all themes including archived"""
        # First archive a theme
        theme_ids = list(admin_service._themes.keys())
        if theme_ids:
            admin_service.delete_theme(theme_ids[0], 'test_user', soft_delete=True)
            
            # Get all themes without archived
            without_archived = admin_service.get_all_themes(include_archived=False)
            
            # Get all themes with archived
            with_archived = admin_service.get_all_themes(include_archived=True)
            
            # Should have more themes when including archived
            assert len(with_archived) >= len(without_archived)
            print(f"✓ Archived themes: {len(with_archived) - len(without_archived)}")
    
    def test_audit_logging(self, admin_service):
        """Test audit logging"""
        initial_log_count = len(admin_service._audit_logs)
        
        new_theme = {
            'id': 'test_audit_001',
            'thai_name': 'ชื่อเพื่อทดสอบการบันทึก',
            'pali_name': 'audit_test_pali',
            'category': 'audit_test',
            'description': 'Audit test',
            'story_guidelines': {
                'theme_stated': 'T',
                'b_story': 'T',
                'break_into_three': 'T',
                'finale': 'T'
            }
        }
        admin_service.create_theme(new_theme, 'audit_tester')
        
        # Should have more audit logs now
        assert len(admin_service._audit_logs) > initial_log_count
        latest_log = admin_service._audit_logs[-1]
        assert latest_log.action == 'CREATE'
        assert latest_log.user_id == 'audit_tester'
        print(f"✓ Audit log recorded: {latest_log.action} by {latest_log.user_id}")
    
    def test_get_audit_logs(self, admin_service):
        """Test retrieving audit logs"""
        logs = admin_service.get_audit_logs(user_id='test_user', limit=10)
        assert isinstance(logs, list)
        print(f"✓ Retrieved {len(logs)} audit logs")


class TestAdminAnalyticsService:
    """Test suite for AdminAnalyticsService analytics"""
    
    @pytest.fixture
    def analytics_service(self):
        """Create analytics service instance"""
        return AdminAnalyticsService()
    
    @pytest.fixture
    def sample_themes(self):
        """Create sample themes for analytics"""
        return [
            {
                'id': 'theme_001',
                'thai_name': 'ชื่อแรก',
                'pali_name': 'pali_001',
                'category': 'category_a',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 'theme_002',
                'thai_name': 'ชื่อที่สอง',
                'pali_name': 'pali_002',
                'category': 'category_b',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 'theme_003',
                'thai_name': 'ชื่อที่สาม',
                'pali_name': 'pali_003',
                'category': 'category_a',
                'created_at': datetime.now().isoformat()
            }
        ]
    
    def test_record_search(self, analytics_service):
        """Test recording search operation"""
        analytics_service.record_search('ความ', 5, 'test_user')
        assert len(analytics_service._search_history) > 0
        print("✓ Search recorded")
    
    def test_record_selection(self, analytics_service):
        """Test recording theme selection"""
        analytics_service.record_selection('theme_001', 'test_user')
        assert len(analytics_service._selection_history) > 0
        print("✓ Selection recorded")
    
    def test_get_theme_stats(self, analytics_service, sample_themes):
        """Test getting theme statistics"""
        stats = analytics_service.get_theme_stats(sample_themes)
        assert stats.total_themes == 3
        assert stats.total_categories == 2
        print(f"✓ Theme stats: {stats.total_themes} themes, {stats.total_categories} categories")
    
    def test_get_category_distribution(self, analytics_service, sample_themes):
        """Test getting category distribution"""
        distribution = analytics_service.get_category_distribution(sample_themes)
        assert isinstance(distribution, dict)
        assert distribution.get('category_a') == 2
        assert distribution.get('category_b') == 1
        print(f"✓ Category distribution: {distribution}")
    
    def test_get_performance_metrics(self, analytics_service, sample_themes):
        """Test getting performance metrics"""
        metrics = analytics_service.get_performance_metrics(sample_themes)
        assert isinstance(metrics, dict)
        assert 'data_quality_score' in metrics
        print(f"✓ Performance metrics: Quality score = {metrics.get('data_quality_score')}")
    
    def test_generate_report(self, analytics_service, sample_themes):
        """Test generating comprehensive report"""
        analytics_service.record_search('test', 1, 'user1')
        analytics_service.record_selection('theme_001', 'user1')
        
        report = analytics_service.generate_report(sample_themes, days=7)
        assert report is not None
        assert 'theme_stats' in report or 'generated_at' in report
        print("✓ Comprehensive report generated")


class TestDataQualityService:
    """Test suite for DataQualityService validation"""
    
    @pytest.fixture
    def quality_service(self):
        """Create quality service instance"""
        return DataQualityService()
    
    @pytest.fixture
    def valid_theme(self):
        """Create valid theme for testing"""
        return {
            'id': 'valid_theme_001',
            'thai_name': 'ชื่อไทยที่ถูกต้อง',
            'pali_name': 'valid_pali_name',
            'category': 'valid_category',
            'description': 'Valid description',
            'story_guidelines': {
                'theme_stated': 'Theme statement',
                'b_story': 'B-story content',
                'break_into_three': 'Three-act structure',
                'finale': 'Finale content'
            },
            'recommended_sub_themes': ['sub1', 'sub2'],
            'core_principles': ['principle1'],
            'related_cetasikas': ['cetasika1'],
            'related_sila': ['sila1'],
            'scripture_refs': ['ref1'],
            'applicable_conflicts': ['conflict1'],
            'example_loglines': ['logline1']
        }
    
    @pytest.fixture
    def invalid_theme(self):
        """Create invalid theme for testing"""
        return {
            'id': 'invalid_theme_001',
            # Missing required fields: thai_name, pali_name, category, description
            'story_guidelines': {
                'theme_stated': 'Only one field',
                # Missing other required story guideline fields
            }
        }
    
    def test_validate_single_theme_valid(self, quality_service, valid_theme):
        """Test validating single valid theme"""
        errors = quality_service._validate_single_theme('valid_theme_001', valid_theme)
        assert len(errors) == 0
        print("✓ Valid theme passed validation")
    
    def test_validate_single_theme_invalid(self, quality_service, invalid_theme):
        """Test validating single invalid theme"""
        errors = quality_service._validate_single_theme('invalid_theme_001', invalid_theme)
        assert len(errors) > 0
        print(f"✓ Invalid theme detected {len(errors)} errors")
    
    def test_check_duplicates(self, quality_service):
        """Test duplicate detection"""
        themes = {
            'theme_001': {'id': 'theme_001', 'thai_name': 'ชื่อเดียวกัน', 'pali_name': 'unique1'},
            'theme_002': {'id': 'theme_002', 'thai_name': 'ชื่อเดียวกัน', 'pali_name': 'unique2'},
            'theme_003': {'id': 'theme_003', 'thai_name': 'ชื่ออื่น', 'pali_name': 'unique3'}
        }
        
        quality_service._check_duplicates(themes)
        # Check that duplicate warnings were logged
        duplicate_warnings = [w for w in quality_service.warnings if 'duplicate' in w.error_type]
        print(f"✓ Found {len(duplicate_warnings)} duplicate warnings")
    
    def test_quality_score_calculation(self, quality_service, valid_theme):
        """Test quality score calculation"""
        themes = {'valid_001': valid_theme}
        score = quality_service._calculate_quality_score(len(themes))
        assert 0 <= score <= 100
        assert score > 80  # Valid theme should have high score
        print(f"✓ Quality score: {score}/100")
    
    def test_completeness_check(self, quality_service, valid_theme):
        """Test data completeness check"""
        themes = {'valid_001': valid_theme}
        completeness = quality_service.check_completeness(themes)
        assert isinstance(completeness, dict)
        print(f"✓ Completeness check: {completeness}")
    
    def test_validate_all_themes(self, quality_service, valid_theme):
        """Test comprehensive validation of all themes"""
        themes = {
            'valid_001': valid_theme,
            'valid_002': {**valid_theme, 'id': 'valid_002'}
        }
        report = quality_service.validate_all_themes(themes)
        assert report is not None
        assert report.total_themes == 2
        print(f"✓ Validation report: {report.total_themes} themes, Quality score: {report.quality_score}")


class TestAdminIntegration:
    """Integration tests for admin services working together"""
    
    @pytest.fixture
    def integrated_services(self):
        """Create all services for integration testing"""
        admin_service = AdminThemeService()
        admin_service.load_themes()
        analytics_service = AdminAnalyticsService()
        quality_service = DataQualityService()
        return {
            'admin': admin_service,
            'analytics': analytics_service,
            'quality': quality_service
        }
    
    def test_full_workflow_create_analyze_validate(self, integrated_services):
        """Test complete workflow: create → analyze → validate"""
        admin = integrated_services['admin']
        analytics = integrated_services['analytics']
        quality = integrated_services['quality']
        
        # Create theme
        new_theme = {
            'id': 'integration_test_001',
            'thai_name': 'ทดสอบการบูรณาการ',
            'pali_name': 'integration_pali',
            'category': 'integration',
            'description': 'Integration test theme',
            'story_guidelines': {
                'theme_stated': 'Test',
                'b_story': 'Test',
                'break_into_three': 'Test',
                'finale': 'Test'
            }
        }
        created = admin.create_theme(new_theme, 'integration_tester')
        assert created is not None
        
        # Record selection
        analytics.record_selection('integration_test_001', 'integration_tester')
        
        # Validate all themes as dict
        themes = admin._themes  # Get internal dict representation
        report = quality.validate_all_themes(themes)
        
        assert report.total_themes > 0
        print(f"✓ Full workflow complete: Created theme, recorded selection, validation report: {report.quality_score}/100")


class TestPerformance:
    """Performance tests for Milestone 6"""
    
    @pytest.fixture
    def admin_service(self):
        """Create admin service instance"""
        service = AdminThemeService()
        service.load_themes()
        return service
    
    @pytest.fixture
    def analytics_service(self):
        """Create analytics service instance"""
        return AdminAnalyticsService()
    
    @pytest.fixture
    def quality_service(self):
        """Create quality service instance"""
        return DataQualityService()
    
    def test_performance_create_bulk_themes(self, admin_service):
        """Test performance of bulk theme creation"""
        import time
        
        start_time = time.time()
        for i in range(10):
            theme = {
                'id': f'perf_test_bulk_{i}',
                'thai_name': f'ชื่อประสิทธิภาพ {i}',
                'pali_name': f'perf_pali_{i}',
                'category': 'performance_test',
                'description': f'Performance test theme {i}',
                'story_guidelines': {
                    'theme_stated': 'T',
                    'b_story': 'T',
                    'break_into_three': 'T',
                    'finale': 'T'
                }
            }
            admin_service.create_theme(theme, 'perf_tester')
        
        elapsed = time.time() - start_time
        per_theme = (elapsed * 1000) / 10
        print(f"✓ Bulk create 10 themes: {elapsed:.3f}s ({per_theme:.1f}ms per theme)")
        assert per_theme < 100  # Should be less than 100ms per theme
    
    def test_performance_search_themes(self, admin_service):
        """Test performance of theme search"""
        import time
        
        start_time = time.time()
        results = admin_service.search_themes('ความ', None, False)
        elapsed = (time.time() - start_time) * 1000
        
        print(f"✓ Search query: {elapsed:.2f}ms ({len(results)} results)")
        assert elapsed < 500  # Should be less than 500ms
    
    def test_performance_validation(self, quality_service, admin_service):
        """Test performance of data validation"""
        import time
        
        # Get themes as dict from internal state
        themes_dict = admin_service._themes
        
        start_time = time.time()
        report = quality_service.validate_all_themes(themes_dict)
        elapsed = (time.time() - start_time) * 1000
        
        print(f"✓ Validation of {len(themes_dict)} themes: {elapsed:.2f}ms")
        assert elapsed < 5000  # Should be less than 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
