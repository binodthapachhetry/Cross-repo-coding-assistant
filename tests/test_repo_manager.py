import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

from aider.repo_manager import RepositoryManager
from aider.io import InputOutput

class TestRepositoryManager(unittest.TestCase):
    def setUp(self):
        self.io = MagicMock(spec=InputOutput)
        self.repo_manager = RepositoryManager(self.io)
        
        # Create temporary directories for test repositories
        self.temp_dirs = []
        for i in range(2):
            temp_dir = tempfile.TemporaryDirectory()
            self.temp_dirs.append(temp_dir)
            
            # Create .git directory to make it look like a git repo
            os.makedirs(os.path.join(temp_dir.name, '.git'))
    
    def tearDown(self):
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            temp_dir.cleanup()
    
    @patch('aider.repo_manager.GitRepo')
    @patch('aider.repo_manager.RepoMap')
    def test_add_repository(self, mock_repo_map, mock_git_repo):
        # Setup mocks
        mock_git_repo_instance = MagicMock()
        mock_git_repo_instance.root = self.temp_dirs[0].name
        mock_git_repo.return_value = mock_git_repo_instance
        
        mock_repo_map_instance = MagicMock()
        mock_repo_map.return_value = mock_repo_map_instance
        
        # Test adding a repository
        repo = self.repo_manager.add_repository('test_repo', self.temp_dirs[0].name)
        
        # Verify repository was added
        self.assertEqual(repo, mock_git_repo_instance)
        self.assertEqual(self.repo_manager.repositories['test_repo'], mock_git_repo_instance)
        self.assertEqual(self.repo_manager.repo_maps['test_repo'], mock_repo_map_instance)
        self.assertEqual(self.repo_manager.active_repo, 'test_repo')
        
        # Verify GitRepo was created with correct parameters
        mock_git_repo.assert_called_once()
        args, kwargs = mock_git_repo.call_args
        self.assertEqual(args[0], self.io)
        self.assertEqual(args[1], [])
        self.assertEqual(args[2], self.temp_dirs[0].name)
        
        # Verify RepoMap was created with correct parameters
        mock_repo_map.assert_called_once()
        args, kwargs = mock_repo_map.call_args
        self.assertEqual(kwargs['root'], self.temp_dirs[0].name)
        self.assertEqual(kwargs['name'], 'test_repo')
    
    @patch('aider.repo_manager.GitRepo')
    @patch('aider.repo_manager.RepoMap')
    def test_set_active_repository(self, mock_repo_map, mock_git_repo):
        # Setup mocks
        mock_git_repo_instance1 = MagicMock()
        mock_git_repo_instance1.root = self.temp_dirs[0].name
        
        mock_git_repo_instance2 = MagicMock()
        mock_git_repo_instance2.root = self.temp_dirs[1].name
        
        mock_git_repo.side_effect = [mock_git_repo_instance1, mock_git_repo_instance2]
        
        # Add two repositories
        self.repo_manager.add_repository('repo1', self.temp_dirs[0].name)
        self.repo_manager.add_repository('repo2', self.temp_dirs[1].name)
        
        # Test setting active repository
        result = self.repo_manager.set_active_repository('repo2')
        
        # Verify active repository was set
        self.assertTrue(result)
        self.assertEqual(self.repo_manager.active_repo, 'repo2')
        
        # Test setting non-existent repository
        result = self.repo_manager.set_active_repository('non_existent')
        
        # Verify operation failed
        self.assertFalse(result)
        self.assertEqual(self.repo_manager.active_repo, 'repo2')
    
    @patch('aider.repo_manager.GitRepo')
    @patch('aider.repo_manager.RepoMap')
    def test_resolve_path(self, mock_repo_map, mock_git_repo):
        # Setup mocks
        mock_git_repo_instance1 = MagicMock()
        mock_git_repo_instance1.root = self.temp_dirs[0].name
        
        mock_git_repo_instance2 = MagicMock()
        mock_git_repo_instance2.root = self.temp_dirs[1].name
        
        mock_git_repo.side_effect = [mock_git_repo_instance1, mock_git_repo_instance2]
        
        # Add two repositories
        self.repo_manager.add_repository('repo1', self.temp_dirs[0].name)
        self.repo_manager.add_repository('repo2', self.temp_dirs[1].name)
        
        # Test resolving path with repo prefix
        repo, path = self.repo_manager.resolve_path('repo2/path/to/file.py')
        
        # Verify correct repository and path were returned
        self.assertEqual(repo, mock_git_repo_instance2)
        self.assertEqual(path, 'path/to/file.py')
        
        # Test resolving path without repo prefix
        repo, path = self.repo_manager.resolve_path('path/to/file.py')
        
        # Verify active repository and original path were returned
        self.assertEqual(repo, mock_git_repo_instance1)
        self.assertEqual(path, 'path/to/file.py')

if __name__ == '__main__':
    unittest.main()
