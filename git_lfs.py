import os
import subprocess
import logging
import sys
import platform
import time
from typing import List, Dict, Optional, Union, Tuple, Any

class GitLFS:
    """
    A production-grade Python library for managing Git LFS (Large File Storage) operations
    with comprehensive error handling and optimized for large repositories.
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
        self.git_path = git_path or self._find_git_executable()
        
        # Set up logging
        self.logger = logging.getLogger('GitLFS')
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
        # Verify repository path
        if not os.path.exists(os.path.join(self.repo_path, '.git')):
            self.logger.warning(f"Path '{self.repo_path}' may not be a valid Git repository. Operations may fail.")
    
    def _find_git_executable(self) -> str:
        """Find the git executable path"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['where', 'git'], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')[0]
            else:
                result = subprocess.run(['which', 'git'], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            return "git"  # Default if not found
        except Exception:
            return "git"  # Default on error
    
    def _run_command(self, command: List[str], stream_output: bool = False, 
                     timeout: Optional[int] = None, retry_count: int = 3,
                     retry_delay: int = 5) -> Tuple[int, str, str]:
        """
        Run a shell command with advanced error handling, timeout control, and retry logic.
        
        Args:
            command: List of command and arguments
            stream_output: If True, logs stdout/stderr lines in real-time
            timeout: Command timeout in seconds (None = no timeout)
            retry_count: Number of times to retry on failure
            retry_delay: Seconds to wait between retries
            
        Returns:
            Tuple of (return_code, collected_stdout, collected_stderr)
        """
        self.logger.debug(f"Running command: {' '.join(command)}")
        stdout_lines = []
        stderr_lines = []
        
        for attempt in range(retry_count):
            if attempt > 0:
                self.logger.info(f"Retry attempt {attempt}/{retry_count-1} after {retry_delay}s delay...")
                time.sleep(retry_delay)
            
            try:
                # For Windows, ensure correct path handling
                if platform.system() == 'Windows' and command[0] == 'git':
                    command[0] = self.git_path
                    
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.repo_path,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                if stream_output:
                    self.logger.info(f"--- Command Output Start ({' '.join(command[:3])}...) ---")
                    # Process output with timeout handling
                    start_time = time.time()
                    while True:
                        # Check timeout
                        if timeout and (time.time() - start_time > timeout):
                            process.terminate()
                            self.logger.error(f"Command timed out after {timeout}s")
                            return -1, '\n'.join(stdout_lines), '\n'.join(stderr_lines + [f"ERROR: Command timed out after {timeout}s"])
                        
                        # Check stdout
                        stdout_line = process.stdout.readline()
                        if stdout_line:
                            line_content = stdout_line.strip()
                            self.logger.info(f"[stdout] {line_content}")
                            stdout_lines.append(line_content)
                        
                        # Check stderr
                        stderr_line = process.stderr.readline()
                        if stderr_line:
                            line_content = stderr_line.strip()
                            # Filter out progress info for cleaner logs
                            if not line_content.startswith("Downloading") and not line_content.startswith("Uploading"):
                                self.logger.info(f"[stderr] {line_content}")
                            stderr_lines.append(line_content)

                        # Check if process has finished
                        if process.poll() is not None and not stdout_line and not stderr_line:
                            break
                        
                        # Brief pause to prevent CPU hogging
                        if not stdout_line and not stderr_line:
                            time.sleep(0.1)
                            
                    self.logger.info("--- Command Output End ---")
                else:
                    # If not streaming, collect output after completion with timeout
                    try:
                        stdout_data, stderr_data = process.communicate(timeout=timeout)
                        stdout_lines = stdout_data.splitlines()
                        stderr_lines = stderr_data.splitlines()
                    except subprocess.TimeoutExpired:
                        process.terminate()
                        self.logger.error(f"Command timed out after {timeout}s")
                        return -1, '\n'.join(stdout_lines), '\n'.join(stderr_lines + [f"ERROR: Command timed out after {timeout}s"])

                # Check if command was successful
                if process.returncode == 0:
                    return process.returncode, '\n'.join(stdout_lines), '\n'.join(stderr_lines)
                
                # If not successful but we're still going to retry, log the error
                if attempt < retry_count - 1:
                    self.logger.warning(f"Command failed with code {process.returncode}, retrying...")
                
            except Exception as e:
                if attempt < retry_count - 1:
                    self.logger.warning(f"Error executing command: {e}, retrying...")
                else:
                    self.logger.error(f"Error executing command after {retry_count} attempts: {e}")
                    return -1, '\n'.join(stdout_lines), '\n'.join(stderr_lines) + f"\nException: {str(e)}"
        
        # If we've exhausted all retries, return the last attempt's result
        return process.returncode, '\n'.join(stdout_lines), '\n'.join(stderr_lines)
    
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
    
    def optimize_for_large_repo(self) -> bool:
        """
        Configure Git for handling large repositories efficiently.
        
        Returns:
            True if all configurations were applied successfully
        """
        configs = {
            'http.postBuffer': '524288000',  # 500MB
            'http.lowSpeedLimit': '1000',    # 1KB/s minimum transfer rate
            'http.lowSpeedTime': '300',      # 5 minutes of slow transfer before abort
            'core.compression': '0',         # Disable compression for LFS
            'http.maxRequestBuffer': '100M', # Larger request buffer
            'pack.windowMemory': '100m',     # Larger memory window for packing
            'pack.packSizeLimit': '100m',    # Smaller pack size for better parallelism
            'pack.threads': '1',             # Reduce parallel packing to save memory
            'core.bigFileThreshold': '10m',  # Treat files > 10MB as big files
            'lfs.concurrenttransfers': '8',  # Number of concurrent LFS transfers
            'lfs.dialtimeout': '30',         # 30s dial timeout
            'lfs.tlstimeout': '30',          # 30s TLS timeout
            'lfs.activitytimeout': '120',    # 2m activity timeout
            'lfs.fetchrecentrefsdays': '7',  # Only fetch refs from last 7 days
            'lfs.fetchrecentcommitsdays': '0', # Disable recent commit fetching
        }
        
        success = True
        for key, value in configs.items():
            code, _, _ = self._run_command([
                self.git_path, 'config', key, value
            ])
            if code != 0:
                self.logger.warning(f"Failed to set git config {key}={value}")
                success = False
        
        if success:
            self.logger.info("Git configured for large repository handling")
        else:
            self.logger.warning("Some Git configurations for large repos failed to apply")
        
        return success
    
    def get_remote_list(self) -> List[str]:
        """
        Get list of configured remotes.
        
        Returns:
            List of remote names
        """
        code, stdout, _ = self._run_command([self.git_path, 'remote'])
        if code != 0:
            return []
        return [r for r in stdout.splitlines() if r]
    
    def get_branch_list(self, include_remote: bool = True) -> List[str]:
        """
        Get list of branches.
        
        Args:
            include_remote: Whether to include remote branches
            
        Returns:
            List of branch names
        """
        command = [self.git_path, 'branch']
        if include_remote:
            command.append('-a')
            
        code, stdout, _ = self._run_command(command)
        if code != 0:
            return []
            
        branches = []
        for line in stdout.splitlines():
            branch = line.strip()
            if branch.startswith('*'):
                branch = branch[1:].strip()
            if branch:
                branches.append(branch)
                
        return branches
    
    def push(self, remote: str = "origin", force: bool = False, batch_size: int = 0) -> bool:
        """
        Push all LFS objects, branches, and tags to the remote repository.
        
        Args:
            remote: Remote repository name or URL
            force: Whether to force push (required after history rewrite)
            batch_size: Number of branches to push in each batch (0 = all at once)
            
        Returns:
            True if successful, False otherwise
        """
        # First optimize git config for large repos
        self.optimize_for_large_repo()
        
        # Ensure LFS is installed
        if not self.is_lfs_installed():
            self.logger.error("Git LFS is not installed. Run install_lfs() first.")
            return False
            
        # Push LFS objects for all refs
        self.logger.info(f"Pushing LFS objects for all refs to {remote}...")
        lfs_push_command = [self.git_path, 'lfs', 'push', '--all', remote]
        code, stdout, stderr = self._run_command(lfs_push_command, stream_output=True, timeout=3600)
        if code != 0:
            self.logger.error(f"Failed to push LFS objects. See output above.")
            return False
        self.logger.info("LFS objects pushed successfully.")

        # Get branches for batch processing if needed
        branches = []
        if batch_size > 0:
            branches = self.get_branch_list(include_remote=False)
            self.logger.info(f"Found {len(branches)} local branches to push in batches of {batch_size}")
            
            # Push branches in batches
            success = True
            for i in range(0, len(branches), batch_size):
                batch = branches[i:i+batch_size]
                self.logger.info(f"Pushing batch {i//batch_size + 1}/{(len(branches)-1)//batch_size + 1}: {', '.join(batch)}")
                
                for branch in batch:
                    push_branch_command = [self.git_path, 'push']
                    if force:
                        push_branch_command.append('-f')
                    push_branch_command.extend([remote, branch])
                    
                    code, _, _ = self._run_command(push_branch_command, stream_output=True, timeout=1800)
                    if code != 0:
                        self.logger.error(f"Failed to push branch {branch}")
                        success = False
                
                # Small delay between batches
                if i + batch_size < len(branches):
                    time.sleep(5)
                    
            if not success:
                self.logger.error("Some branches failed to push.")
                # Continue to push tags
        else:
            # Push all branches at once
            self.logger.info(f"Pushing all branches to {remote}...")
            push_branches_command = [self.git_path, 'push', '--all']
            if force:
                push_branches_command.append('-f')
            push_branches_command.append(remote)
            
            code, _, _ = self._run_command(push_branches_command, stream_output=True, timeout=3600)
            if code != 0:
                self.logger.error(f"Failed to push branches. See output above.")
                # Continue to tag push attempt

        # Push all tags
        self.logger.info(f"Pushing all tags to {remote}...")
        push_tags_command = [self.git_path, 'push', '--tags']
        if force:
            push_tags_command.append('-f')
        push_tags_command.append(remote)
        
        code, _, _ = self._run_command(push_tags_command, stream_output=True, timeout=1800)
        if code != 0:
            self.logger.error(f"Failed to push tags. See output above.")
            return False

        self.logger.info("All tags pushed successfully.")
        self.logger.info(f"Successfully pushed repository to {remote}")
        return True
    
    def migrate_import(self, file_pattern: str, include_all_branches: bool = True,
                       above_size: Optional[str] = None) -> bool:
        """
        Migrate existing files in history to LFS.
        
        Args:
            file_pattern: Pattern of files to migrate (e.g., "*.psd")
            include_all_branches: Whether to migrate across all branches (--everything flag)
            above_size: Only migrate files above this size (e.g., "10MB")
            
        Returns:
            True if successful, False otherwise
        """
        command = [
            self.git_path, 'lfs', 'migrate', 'import',
            '--include', file_pattern, '--yes'
        ]
        
        if include_all_branches:
            command.append('--everything')
            
        if above_size:
            command.extend(['--above', above_size])
            
        code, stdout, stderr = self._run_command(command, stream_output=True, timeout=7200)
        if code != 0:
            self.logger.error(f"Failed to migrate {file_pattern}: {stderr}")
            return False
        self.logger.info(f"Successfully migrated {file_pattern} to LFS")
        return True
    
    def batch_migrate_by_extension(self, extensions: List[str], include_all_branches: bool = True,
                                 above_size: str = "10MB") -> Dict[str, bool]:
        """
        Migrate multiple file extensions to LFS in batches.
        
        Args:
            extensions: List of file extensions to migrate (e.g., ["psd", "zip"])
            include_all_branches: Whether to include all branches
            above_size: Only migrate files above this size
            
        Returns:
            Dictionary of extension -> success mapping
        """
        results = {}
        for ext in extensions:
            pattern = f"*.{ext}" if not ext.startswith('*') else ext
            self.logger.info(f"Migrating files matching pattern: {pattern}")
            success = self.migrate_import(
                file_pattern=pattern,
                include_all_branches=include_all_branches,
                above_size=above_size
            )
            results[pattern] = success
            # Small delay between migrations
            time.sleep(5)
            
        return results
    
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
    
    def verify_lfs_objects(self) -> bool:
        """
        Verify all LFS objects are valid.
        
        Returns:
            True if all objects are valid, False otherwise
        """
        code, stdout, stderr = self._run_command([self.git_path, 'lfs', 'fsck'], stream_output=True)
        if code != 0:
            self.logger.error(f"LFS object verification failed: {stderr}")
            return False
        self.logger.info("All LFS objects verified successfully")
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
    
    def find_large_files(self, size_threshold_mb: int = 10) -> List[Dict[str, Any]]:
        """
        Find large files in repository history.
        
        Args:
            size_threshold_mb: Minimum file size in MB to report
            
        Returns:
            List of dictionaries with file information
        """
        threshold_bytes = size_threshold_mb * 1024 * 1024
        
        # Temporary file to store results
        temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "large_files_temp.txt")
        
        # Use git-sizer if available for much faster processing
        try:
            code, sizer_out, _ = self._run_command(['git-sizer', '--verbose'], stream_output=False)
            if code == 0:
                self.logger.info("Using git-sizer to find large files")
                return self._parse_sizer_output(sizer_out, threshold_bytes)
        except:
            self.logger.info("git-sizer not available, using standard approach")
        
        # Fall back to standard approach
        self.logger.info(f"Finding files larger than {size_threshold_mb}MB in repository history...")
        
        # Use git rev-list and grep to find large blobs efficiently
        command = [
            self.git_path, 'rev-list', '--all', '--objects', '|', 
            'git', 'cat-file', '--batch-check="%(objectname) %(objecttype) %(objectsize) %(rest)"', '|',
            'grep', 'blob', '|', 'sort', '-k3', '-nr', '|', 'head', '-n', '100'
        ]
        
        # For Windows, we need to use shell=True for pipes
        if platform.system() == 'Windows':
            combined_cmd = ' '.join(command)
            process = subprocess.Popen(
                combined_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=self.repo_path, text=True
            )
            stdout, _ = process.communicate()
        else:
            # For Unix, we can use multiple pipes without shell=True
            p1 = subprocess.Popen(
                [self.git_path, 'rev-list', '--all', '--objects'],
                stdout=subprocess.PIPE, cwd=self.repo_path
            )
            p2 = subprocess.Popen(
                [self.git_path, 'cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize) %(rest)'],
                stdin=p1.stdout, stdout=subprocess.PIPE, cwd=self.repo_path, text=True
            )
            p1.stdout.close()
            p3 = subprocess.Popen(
                ['grep', 'blob'], stdin=p2.stdout, stdout=subprocess.PIPE, text=True
            )
            p2.stdout.close()
            p4 = subprocess.Popen(
                ['sort', '-k3', '-nr'], stdin=p3.stdout, stdout=subprocess.PIPE, text=True
            )
            p3.stdout.close()
            p5 = subprocess.Popen(
                ['head', '-n', '100'], stdin=p4.stdout, stdout=subprocess.PIPE, text=True
            )
            p4.stdout.close()
            stdout, _ = p5.communicate()
        
        # Process results
        large_files = []
        for line in stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 4:
                obj_hash, obj_type, size, *path_parts = parts
                path = ' '.join(path_parts)
                size_bytes = int(size)
                
                if size_bytes >= threshold_bytes:
                    large_files.append({
                        'path': path,
                        'size_bytes': size_bytes,
                        'size_mb': round(size_bytes / (1024 * 1024), 2),
                        'hash': obj_hash
                    })
        
        self.logger.info(f"Found {len(large_files)} files larger than {size_threshold_mb}MB")
        return large_files
    
    def _parse_sizer_output(self, output: str, threshold_bytes: int) -> List[Dict[str, Any]]:
        """Parse git-sizer output to extract large files"""
        large_files = []
        scanning = False
        
        for line in output.splitlines():
            if "Biggest objects" in line:
                scanning = True
                continue
                
            if scanning and line.strip() and not line.startswith("  "):
                scanning = False
                break
                
            if scanning and "blob" in line:
                parts = line.strip().split()
                if len(parts) >= 4:
                    size_str = parts[0]
                    path = ' '.join(parts[3:])
                    
                    # Parse size (e.g. "15.0 MiB")
                    try:
                        size_val = float(size_str)
                        unit = parts[1]
                        size_bytes = 0
                        
                        if unit == "KiB":
                            size_bytes = size_val * 1024
                        elif unit == "MiB":
                            size_bytes = size_val * 1024 * 1024
                        elif unit == "GiB":
                            size_bytes = size_val * 1024 * 1024 * 1024
                            
                        if size_bytes >= threshold_bytes:
                            large_files.append({
                                'path': path,
                                'size_bytes': int(size_bytes),
                                'size_mb': round(size_bytes / (1024 * 1024), 2)
                            })
                    except:
                        continue
                        
        return large_files
    
    def create_gitattributes(self, large_files: List[Dict[str, Any]]) -> bool:
        """
        Create or update .gitattributes file for LFS tracking.
        
        Args:
            large_files: List of dictionaries with file information
            
        Returns:
            True if successful, False otherwise
        """
        gitattributes_path = os.path.join(self.repo_path, '.gitattributes')
        existing_patterns = set()
        
        # Read existing patterns
        if os.path.exists(gitattributes_path):
            with open(gitattributes_path, 'r') as f:
                for line in f:
                    if 'filter=lfs' in line:
                        pattern = line.split('filter=lfs')[0].strip()
                        existing_patterns.add(pattern)
        
        # Create patterns by extension and directory
        new_patterns = set()
        extensions = {}
        directories = {}
        
        for file in large_files:
            file_path = file['path']
            
            # Get directory path and filename
            dir_path = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            
            # Track by extension
            _, ext = os.path.splitext(filename)
            if ext:
                ext = ext.lstrip('.')
                if ext not in extensions:
                    extensions[ext] = []
                extensions[ext].append(file_path)
                
                # Add patterns for this extension
                new_patterns.add(f"*.{ext}")
                
                # Add directory-specific patterns for this extension
                if dir_path:
                    new_patterns.add(f"{dir_path}/*.{ext}")
            else:
                # For files without extension, use the exact path
                new_patterns.add(file_path)
                
            # Track directories
            if dir_path:
                if dir_path not in directories:
                    directories[dir_path] = []
                directories[dir_path].append(file_path)
        
        # Update .gitattributes file
        if new_patterns:
            self.logger.info(f"Updating .gitattributes with {len(new_patterns)} patterns")
            
            # Track patterns to be added
            patterns_to_add = sorted(list(new_patterns - existing_patterns))
            if patterns_to_add:
                self.logger.info(f"Adding {len(patterns_to_add)} new patterns to .gitattributes")
                
                with open(gitattributes_path, 'a') as f:
                    if os.path.exists(gitattributes_path) and os.path.getsize(gitattributes_path) > 0:
                        f.write('\n')
                        
                    for pattern in patterns_to_add:
                        f.write(f'{pattern} filter=lfs diff=lfs merge=lfs -text\n')
                        
                self.logger.info("Successfully updated .gitattributes file")
            else:
                self.logger.info("No new patterns to add to .gitattributes")
        else:
            self.logger.info("No patterns to add to .gitattributes")
            
        return True