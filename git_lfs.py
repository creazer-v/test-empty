import os
import subprocess
import logging
import sys
import platform
from typing import List, Dict, Optional, Union, Tuple

class GitLFS:
    """
    A Python library for pushing Git LFS (Large File Storage) objects to remote repositories.
    """
    
    def __init__(self, repo_path: str = None, log_level: int = logging.INFO, git_path: str = None):
        """
        Initialize GitLFS with a repository path.
        
        Args:
            repo_path: Path to the git repository. If None, uses current directory.
            log_level: Logging level (default: logging.INFO)
            git_path: Path to git executable (default: "git")
        """
        self.repo_path = repo_path or os.getcwd()
        self.git_path = git_path or "git"
        
        # Set up logging
        self.logger = logging.getLogger('GitLFS')
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _run_command(self, command: List[str], stream_output: bool = False) -> Tuple[int, str, str]:
        """
        Run a shell command and return the exit code, stdout, and stderr.
        Optionally streams output in real-time.
        
        Args:
            command: List of command and arguments
            stream_output: If True, logs stdout/stderr lines in real-time (default: False)
            
        Returns:
            Tuple of (return_code, collected_stdout, collected_stderr)
        """
        self.logger.debug(f"Running command: {' '.join(command)}")
        stdout_lines = []
        stderr_lines = []
        
        try:
            # For Windows, ensure correct path handling
            if platform.system() == 'Windows' and command[0] == 'git':
                command[0] = self.git_path
                
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.repo_path,
                text=True,  # Use text mode for easier line reading
                bufsize=1,  # Line buffered
                universal_newlines=True # Ensure cross-platform newline handling
            )

            # Stream output if requested
            if stream_output:
                self.logger.info("--- Command Output Start ---")
                # Read line by line from stdout and stderr
                while True:
                    # Check stdout
                    stdout_line = process.stdout.readline()
                    if stdout_line:
                        line_content = stdout_line.strip()
                        self.logger.info(f"[stdout] {line_content}")
                        stdout_lines.append(line_content)
                    
                    # Check stderr - LFS progress usually goes here
                    stderr_line = process.stderr.readline()
                    if stderr_line:
                        line_content = stderr_line.strip()
                        # Log stderr as INFO to ensure visibility, tag it clearly
                        self.logger.info(f"[stderr] {line_content}") 
                        stderr_lines.append(line_content)

                    # Check if process has finished
                    if process.poll() is not None and not stdout_line and not stderr_line:
                        break 
                self.logger.info("--- Command Output End ---")
            else:
                # If not streaming, collect output after completion
                stdout_data, stderr_data = process.communicate()
                stdout_lines = stdout_data.splitlines()
                stderr_lines = stderr_data.splitlines()

            return process.returncode, '\n'.join(stdout_lines), '\n'.join(stderr_lines)
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            # Ensure lists are joined even on error if some lines were captured
            return -1, '\n'.join(stdout_lines), '\n'.join(stderr_lines) + f"\nException: {str(e)}"
    
    def is_lfs_installed(self) -> bool:
        """
        Check if Git LFS is installed on the system.
        
        Returns:
            True if installed, False otherwise
        """
        code, _, _ = self._run_command([self.git_path, 'lfs', 'version'])
        return code == 0
    
    def install_lfs(self) -> bool:
        """
        Install Git LFS in the repository.
        
        Returns:
            True if successful, False otherwise
        """
        code, stdout, stderr = self._run_command([self.git_path, 'lfs', 'install'])
        if code != 0:
            self.logger.error(f"Failed to install Git LFS: {stderr}")
            return False
        self.logger.info("Git LFS installed successfully")
        return True
    
    def push(self, remote: str = "origin", force: bool = False) -> bool:
        """
        Push all LFS objects, branches, and tags to the remote repository.
        This should be used after commands like 'git lfs migrate' which rewrite history.
        
        Args:
            remote: Remote repository name or URL (default: origin)
            force: Whether to force push (REQUIRED after history rewrite, default: False)
            
        Returns:
            True if successful, False otherwise
        """
        # First ensure all LFS objects are pushed for all refs
        self.logger.info(f"Pushing LFS objects for all refs to {remote}...")
        lfs_push_command = [self.git_path, 'lfs', 'push', '--all', remote]
        # Stream output for LFS push
        code, stdout, stderr = self._run_command(lfs_push_command, stream_output=True) 
        if code != 0:
            self.logger.error(f"Failed to push LFS objects. See output above.")
            # Stderr might already be logged if streaming, but log again just in case
            self.logger.debug(f"LFS Push Stderr:\n{stderr}") 
            self.logger.debug(f"LFS Push Stdout:\n{stdout}")
            return False
        self.logger.info("LFS objects pushed successfully.")

        # Then push all branches
        self.logger.info(f"Pushing all branches to {remote}...")
        push_branches_command = [self.git_path, 'push', '--all']
        if force:
            push_branches_command.append('-f')
        push_branches_command.append(remote)
        # Stream output for git push branches
        code, stdout, stderr = self._run_command(push_branches_command, stream_output=True)
        if code != 0:
            self.logger.error(f"Failed to push branches. See output above.")
            self.logger.debug(f"Branch Push Stderr:\n{stderr}")
            self.logger.debug(f"Branch Push Stdout:\n{stdout}")
            # Continue to tag push attempt
        else:
             self.logger.info("All branches pushed successfully.")

        # Finally, push all tags
        self.logger.info(f"Pushing all tags to {remote}...")
        push_tags_command = [self.git_path, 'push', '--tags']
        if force:
            push_tags_command.append('-f')
        push_tags_command.append(remote)
        # Stream output for git push tags
        code, stdout, stderr = self._run_command(push_tags_command, stream_output=True)
        if code != 0:
            self.logger.error(f"Failed to push tags. See output above.")
            self.logger.debug(f"Tag Push Stderr:\n{stderr}")
            self.logger.debug(f"Tag Push Stdout:\n{stdout}")
            return False # Return False if tags fail

        self.logger.info("All tags pushed successfully.")
        self.logger.info(f"Successfully pushed all branches and tags to {remote}")
        return True
    
    def status(self) -> Dict[str, List[str]]:
        """
        Show status of Git LFS files.
        
        Returns:
            Dictionary with LFS file status
        """
        code, stdout, stderr = self._run_command([self.git_path, 'lfs', 'status'])
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
        code, stdout, stderr = self._run_command([self.git_path, 'lfs', 'logs', 'last'])
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
            self.git_path, 'lfs', 'migrate', 'import', '--include', file_pattern, '--yes'
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
        code, stdout, stderr = self._run_command([self.git_path, 'lfs', 'prune'])
        if code != 0:
            self.logger.error(f"Failed to clean LFS cache: {stderr}")
            return False
        self.logger.info("Successfully cleaned LFS cache")
        return True