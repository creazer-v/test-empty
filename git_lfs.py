import os
import subprocess
import logging
from typing import List, Dict, Optional, Union, Tuple

class GitLFS:
    """
    A Python library for interacting with Git LFS (Large File Storage) 
    to handle large files in GitHub repositories.
    """
    
    def __init__(self, repo_path: str = None, log_level: int = logging.INFO):
        """
        Initialize GitLFS with a repository path.
        
        Args:
            repo_path: Path to the git repository. If None, uses current directory.
            log_level: Logging level (default: logging.INFO)
        """
        self.repo_path = repo_path or os.getcwd()
        
        # Set up logging
        self.logger = logging.getLogger('GitLFS')
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _run_command(self, command: List[str]) -> Tuple[int, str, str]:
        """
        Run a shell command and return the exit code, stdout, and stderr.
        
        Args:
            command: List of command and arguments
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        self.logger.debug(f"Running command: {' '.join(command)}")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.repo_path,
                text=True
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return -1, "", str(e)
    
    def is_lfs_installed(self) -> bool:
        """
        Check if Git LFS is installed on the system.
        
        Returns:
            True if installed, False otherwise
        """
        code, _, _ = self._run_command(['git', 'lfs', 'version'])
        return code == 0
    
    def install_lfs(self) -> bool:
        """
        Install Git LFS in the repository.
        
        Returns:
            True if successful, False otherwise
        """
        code, stdout, stderr = self._run_command(['git', 'lfs', 'install'])
        if code != 0:
            self.logger.error(f"Failed to install Git LFS: {stderr}")
            return False
        self.logger.info("Git LFS installed successfully")
        return True
    
    def track_file(self, file_pattern: str) -> bool:
        """
        Track files matching the pattern with Git LFS.
        
        Args:
            file_pattern: Pattern of files to track (e.g., "*.psd", "*.zip")
            
        Returns:
            True if successful, False otherwise
        """
        code, stdout, stderr = self._run_command(['git', 'lfs', 'track', file_pattern])
        if code != 0:
            self.logger.error(f"Failed to track {file_pattern}: {stderr}")
            return False
        self.logger.info(f"Now tracking {file_pattern} with Git LFS")
        return True
    
    def untrack_file(self, file_pattern: str) -> bool:
        """
        Stop tracking files matching the pattern with Git LFS.
        
        Args:
            file_pattern: Pattern of files to untrack
            
        Returns:
            True if successful, False otherwise
        """
        code, stdout, stderr = self._run_command(['git', 'lfs', 'untrack', file_pattern])
        if code != 0:
            self.logger.error(f"Failed to untrack {file_pattern}: {stderr}")
            return False
        self.logger.info(f"Stopped tracking {file_pattern} with Git LFS")
        return True
    
    def list_tracked_files(self) -> List[str]:
        """
        List all patterns currently tracked by Git LFS.
        
        Returns:
            List of tracked patterns
        """
        code, stdout, stderr = self._run_command(['git', 'lfs', 'track'])
        if code != 0:
            self.logger.error(f"Failed to list tracked files: {stderr}")
            return []
        
        tracked_patterns = []
        for line in stdout.splitlines():
            if line.startswith("Tracking "):
                pattern = line.replace("Tracking ", "").strip()
                tracked_patterns.append(pattern)
        
        return tracked_patterns
    
    def add_file(self, file_path: str) -> bool:
        """
        Add a file to git staging area.
        
        Args:
            file_path: Path to the file to add
            
        Returns:
            True if successful, False otherwise
        """
        code, stdout, stderr = self._run_command(['git', 'add', file_path])
        if code != 0:
            self.logger.error(f"Failed to add {file_path}: {stderr}")
            return False
        self.logger.info(f"Added {file_path} to staging area")
        return True
    
    def commit(self, message: str) -> bool:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            
        Returns:
            True if successful, False otherwise
        """
        code, stdout, stderr = self._run_command(['git', 'commit', '-m', message])
        if code != 0:
            self.logger.error(f"Failed to commit: {stderr}")
            return False
        self.logger.info(f"Committed with message: {message}")
        return True
    
    def push(self, remote: str = "origin", branch: str = "main") -> bool:
        """
        Push commits and LFS objects to remote repository.
        
        Args:
            remote: Remote repository name (default: origin)
            branch: Branch to push to (default: main)
            
        Returns:
            True if successful, False otherwise
        """
        # First push LFS objects
        code, stdout, stderr = self._run_command(['git', 'lfs', 'push', remote, branch])
        if code != 0:
            self.logger.error(f"Failed to push LFS objects: {stderr}")
            return False
        
        # Then push the commits
        code, stdout, stderr = self._run_command(['git', 'push', remote, branch])
        if code != 0:
            self.logger.error(f"Failed to push commits: {stderr}")
            return False
        
        self.logger.info(f"Successfully pushed to {remote}/{branch}")
        return True
    
    def pull(self, remote: str = "origin", branch: str = "main") -> bool:
        """
        Pull changes and LFS objects from remote repository.
        
        Args:
            remote: Remote repository name (default: origin)
            branch: Branch to pull from (default: main)
            
        Returns:
            True if successful, False otherwise
        """
        code, stdout, stderr = self._run_command(['git', 'lfs', 'pull', remote, branch])
        if code != 0:
            self.logger.error(f"Failed to pull: {stderr}")
            return False
        self.logger.info(f"Successfully pulled from {remote}/{branch}")
        return True
    
    def check_large_files(self, size_threshold_mb: int = 100) -> List[Dict[str, Union[str, int]]]:
        """
        Find potentially large files in the repository that might need LFS.
        
        Args:
            size_threshold_mb: Size threshold in MB to consider a file as large
            
        Returns:
            List of dictionaries with file information
        """
        large_files = []
        for root, _, files in os.walk(self.repo_path):
            # Skip .git directory
            if ".git" in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.repo_path)
                
                try:
                    size_bytes = os.path.getsize(file_path)
                    size_mb = size_bytes / (1024 * 1024)
                    
                    if size_mb >= size_threshold_mb:
                        large_files.append({
                            'path': rel_path,
                            'size_bytes': size_bytes,
                            'size_mb': round(size_mb, 2)
                        })
                except Exception as e:
                    self.logger.warning(f"Could not check size of {rel_path}: {e}")
        
        return large_files
    
    def status(self) -> Dict[str, List[str]]:
        """
        Show status of Git LFS files.
        
        Returns:
            Dictionary with LFS file status
        """
        code, stdout, stderr = self._run_command(['git', 'lfs', 'status'])
        if code != 0:
            self.logger.error(f"Failed to get LFS status: {stderr}")
            return {}
        
        status = {
            'tracked_files': [],
            'not_tracked': []
        }
        
        # Parse output to extract tracked files and untracked files
        current_section = None
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("Tracked files:"):
                current_section = 'tracked_files'
            elif line.startswith("Objects not tracked by Git LFS:"):
                current_section = 'not_tracked'
            elif current_section and not line.startswith("("):
                status[current_section].append(line)
        
        return status
    
    def lfs_logs(self) -> str:
        """
        Get Git LFS logs.
        
        Returns:
            String containing LFS logs
        """
        code, stdout, stderr = self._run_command(['git', 'lfs', 'logs', 'last'])
        if code != 0:
            self.logger.error(f"Failed to get LFS logs: {stderr}")
            return ""
        return stdout
    
    def migrate_import(self, file_pattern: str) -> bool:
        """
        Migrate existing files in history to LFS.
        
        Args:
            file_pattern: Pattern of files to migrate
            
        Returns:
            True if successful, False otherwise
        """
        code, stdout, stderr = self._run_command([
            'git', 'lfs', 'migrate', 'import', '--include', file_pattern, '--yes'
        ])
        if code != 0:
            self.logger.error(f"Failed to migrate {file_pattern}: {stderr}")
            return False
        self.logger.info(f"Successfully migrated {file_pattern} to LFS")
        return True
    
    def cleanup(self) -> bool:
        """
        Clean up local LFS cache.
        
        Returns:
            True if successful, False otherwise
        """
        code, stdout, stderr = self._run_command(['git', 'lfs', 'prune'])
        if code != 0:
            self.logger.error(f"Failed to clean LFS cache: {stderr}")
            return False
        self.logger.info("Successfully cleaned LFS cache")
        return True
