from git_lfs import GitLFS
from git import Repo
import os
import sys
import subprocess
import time
from git.exc import GitCommandError  # Import the specific exception

# Keep existing credentials and URLs for future use
SOURCE_REPO_PATH = "/var/www/html/backup-create/co-resource.git"  # Use forward slashes for Linux paths
GH_TOKEN = "g4cX9"
ORG_NAME = "CloudServices"
REPO_NAME = "cfx-resource"
TARGET_REPO_URL = f"https://{GH_TOKEN}@github.com/{ORG_NAME}/{REPO_NAME}.git"


def find_large_files_in_history(repo_path, size_threshold_mb=5):
    """
    Scan through commit history to find large files that were ever committed
    
    Args:
        repo_path: Path to the Git repository
        size_threshold_mb: Minimum file size to consider as large (in MB)
    """
    print(f"Scanning commit history for large files (>{size_threshold_mb}MB) in {repo_path}...\n")
    
    # Convert MB to bytes
    size_threshold = size_threshold_mb * 1024 * 1024
    
    # Initialize repository
    repo = Repo(repo_path)
    
    large_files = []
    file_sizes = {}
    
    # Using git rev-list to get all commit IDs
    commits = list(repo.iter_commits('--all'))
    total_commits = len(commits)
    
    print(f"Scanning {total_commits} commits...")
    
    for i, commit in enumerate(commits):
        if i % 50 == 0:
            print(f"Progress: {i}/{total_commits} commits")
        
        try:
            # For the root commit, get all files in the tree
            if not commit.parents:
                for blob in commit.tree.traverse():
                    if blob.type == 'blob':  # Only process files, not trees
                        try:
                            size = blob.size
                            if size > size_threshold:
                                path = blob.path
                                if path not in file_sizes or size > file_sizes[path]['size']:
                                    file_sizes[path] = {
                                        'size': size,
                                        'size_mb': round(size / (1024 * 1024), 2),
                                        'commit': commit.hexsha[:7],
                                        'date': commit.committed_datetime.strftime('%Y-%m-%d'),
                                        'message': commit.message.split('\n')[0]
                                    }
                        except (ValueError, AttributeError, KeyError) as e:
                            continue
                continue  # Skip to next commit after processing root
                
            # For non-root commits, compare with parents
            for parent in commit.parents:
                try:
                    diffs = commit.diff(parent, R=True)  # R=True to detect renames
                    
                    for diff in diffs:
                        try:
                            # Safely check a_blob
                            if diff.a_blob:
                                try:
                                    size = diff.a_blob.size
                                    if size > size_threshold:
                                        path = diff.a_path
                                        if path not in file_sizes or size > file_sizes[path]['size']:
                                            file_sizes[path] = {
                                                'size': size,
                                                'size_mb': round(size / (1024 * 1024), 2),
                                                'commit': commit.hexsha[:7],
                                                'date': commit.committed_datetime.strftime('%Y-%m-%d'),
                                                'message': commit.message.split('\n')[0]
                                            }
                                except (ValueError, AttributeError, KeyError) as e:
                                    continue  # Skip if we can't get the size
                            
                            # Safely check b_blob
                            if diff.b_blob:
                                try:
                                    size = diff.b_blob.size
                                    if size > size_threshold:
                                        path = diff.b_path
                                        if path not in file_sizes or size > file_sizes[path]['size']:
                                            file_sizes[path] = {
                                                'size': size,
                                                'size_mb': round(size / (1024 * 1024), 2),
                                                'commit': commit.hexsha[:7],
                                                'date': commit.committed_datetime.strftime('%Y-%m-%d'),
                                                'message': commit.message.split('\n')[0]
                                            }
                                except (ValueError, AttributeError, KeyError) as e:
                                    continue  # Skip if we can't get the size
                                    
                        except (ValueError, AttributeError, KeyError) as e:
                            continue  # Skip problematic diffs
                            
                except GitCommandError as e:
                    print(f"\nWarning: Failed to diff commit {commit.hexsha[:7]} against parent {parent.hexsha[:7]}. Error: {e}")
                    continue # Skip this parent diff and continue with the next parent or commit
                except (ValueError, AttributeError, KeyError) as e:
                    print(f"\nWarning: Could not process diff for commit {commit.hexsha[:7]}. Error: {e}")
                    continue
                    
        except (ValueError, AttributeError, KeyError) as e:
            print(f"\nWarning: Could not process commit {commit.hexsha[:7]}. Error: {e}")
            continue
    
    # Convert dictionary to list
    for path, info in file_sizes.items():
        large_files.append({
            'path': path,
            'size_mb': info['size_mb'],
            'commit': info['commit'],
            'date': info['date'],
            'message': info['message']
        })
    
    # Sort files by size (largest first)
    large_files.sort(key=lambda x: x['size_mb'], reverse=True)
    
    # Display results
    if large_files:
        print(f"\nFound {len(large_files)} large files (>{size_threshold_mb}MB) in commit history:")
        print(f"{'Size (MB)':<10} {'Path':<50} {'Commit':<10} {'Date':<12} {'Message':<30}")
        print("-" * 110)
        for file in large_files:
            print(f"{file['size_mb']:<10.2f} {file['path']:<50} {file['commit']:<10} {file['date']:<12} {file['message'][:30]}")
    else:
        print(f"No large files (>{size_threshold_mb}MB) found in commit history.")
    
    return large_files

def create_gitattributes_for_large_files(repo_path, large_files):
    """
    Create or update .gitattributes file to track large files with Git LFS
    
    Args:
        repo_path: Path to the Git repository
        large_files: List of dictionaries containing large file information
    """
    gitattributes_path = os.path.join(repo_path, '.gitattributes')
    existing_patterns = set()
    
    # Read existing patterns if .gitattributes exists
    if os.path.exists(gitattributes_path):
        with open(gitattributes_path, 'r') as f:
            for line in f:
                if 'filter=lfs' in line:
                    pattern = line.split('filter=lfs')[0].strip()
                    existing_patterns.add(pattern)
    
    # Create patterns for new files
    new_patterns = set()
    for file in large_files:
        file_path = file['path']
        
        # Get directory path and filename
        dir_path = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        
        # Create patterns based on the file location
        if dir_path:
            # Pattern for the specific file in its directory
            specific_pattern = file_path
            # Pattern for similar files in the same directory
            _, ext = os.path.splitext(filename)
            if ext:
                dir_pattern = f"{dir_path}/*{ext}"
            else:
                dir_pattern = specific_pattern
                
            new_patterns.add(specific_pattern)
            if ext:  # Only add directory pattern if it's a file with extension
                new_patterns.add(dir_pattern)
        else:
            # File is in root directory
            new_patterns.add(filename)
    
    # Update .gitattributes file
    if new_patterns:
        print(f"\nUpdating .gitattributes file with {len(new_patterns)} new patterns...")
        print("New patterns to be added:")
        for pattern in sorted(new_patterns):
            if pattern not in existing_patterns:
                print(f"  {pattern}")
        
        with open(gitattributes_path, 'a') as f:
            if os.path.getsize(gitattributes_path) > 0:
                f.write('\n')  # Add newline if file is not empty
            for pattern in sorted(new_patterns):
                if pattern not in existing_patterns:
                    f.write(f'{pattern} filter=lfs diff=lfs merge=lfs -text\n')
        print("Successfully updated .gitattributes file")
    else:
        print("\nNo new patterns to add to .gitattributes file")

def convert_files_to_lfs(lfs: GitLFS, repo_path, large_files):
    """
    Convert identified large files to Git LFS using our GitLFS library
    
    Args:
        lfs: Initialized GitLFS object
        repo_path: Path to the Git repository
        large_files: List of dictionaries containing large file information
    """
    print("\nInitializing Git LFS and converting files...")
    
    # Check if LFS is installed
    if not lfs.is_lfs_installed():
        print("Git LFS is not installed. Installing...")
        if not lfs.install_lfs():
            print("Failed to install Git LFS. Please install it manually.")
            return False, lfs
    
    # Group files by extension for more efficient migration
    extensions = {}
    for file_info in large_files:
        file_path = file_info['path']
        _, ext = os.path.splitext(file_path)
        if ext:
            if ext not in extensions:
                extensions[ext] = []
            extensions[ext].append(file_path)
        else:
            # For files without extension, use the full path
            extensions[file_path] = [file_path]
    
    # Convert files to LFS
    success = True
    converted_patterns = []
    failed_patterns = []
    
    # First ensure we have all objects
    print("\nFetching all LFS objects...")
    fetch_code, fetch_out, fetch_err = lfs._run_command([
        'git', 'lfs', 'fetch', '--all'
    ], stream_output=True)
    if fetch_code != 0:
        print(f"Warning: Failed to fetch all LFS objects: {fetch_err}")
    
    for pattern, files in extensions.items():
        if pattern.startswith('.'):
            # For files with extension, use pattern like "*.ext"
            migrate_pattern = f"*{pattern}"
        else:
            # For files without extension, use the exact path
            migrate_pattern = pattern
            
        print(f"\nMigrating pattern: {migrate_pattern}")
        print(f"This will affect the following files:")
        for file in files:
            print(f"  - {file}")
            
        if lfs.migrate_import(migrate_pattern):
            converted_patterns.append(migrate_pattern)
            print(f"Successfully migrated pattern: {migrate_pattern}")
        else:
            failed_patterns.append(migrate_pattern)
            success = False
            print(f"Failed to migrate pattern: {migrate_pattern}")
    
    # Print summary
    print("\nConversion Summary:")
    if converted_patterns:
        print("\nSuccessfully converted patterns:")
        for pattern in converted_patterns:
            print(f"  - {pattern}")
    
    if failed_patterns:
        print("\nFailed to convert patterns:")
        for pattern in failed_patterns:
            print(f"  - {pattern}")
    
    # Get final LFS status
    status = lfs.status()
    if status:
        print("\nFinal LFS Status:")
        if status['tracked_files']:
            print("\nTracked files:")
            for file in status['tracked_files']:
                print(f"  - {file}")
        if status['not_tracked']:
            print("\nFiles not tracked by LFS:")
            for file in status['not_tracked']:
                print(f"  - {file}")
    
    # Ensure all objects are properly tracked
    print("\nChecking LFS objects...")
    check_code, check_out, check_err = lfs._run_command([
        'git', 'lfs', 'fsck'
    ], stream_output=True)
    if check_code != 0:
        print(f"Warning: LFS integrity check failed: {check_err}")
    
    return success, lfs

# Update the main block to include the conversion and push steps
if __name__ == "__main__":
    # Initialize GitLFS once
    lfs_handler = GitLFS(repo_path=SOURCE_REPO_PATH)

    large_files = find_large_files_in_history(SOURCE_REPO_PATH, size_threshold_mb=1)
    if large_files:
        create_gitattributes_for_large_files(SOURCE_REPO_PATH, large_files)
        
        # Perform conversion
        conversion_success, _ = convert_files_to_lfs(lfs_handler, SOURCE_REPO_PATH, large_files)
        
        if conversion_success:
            print("\nMigration successful. Proceeding to push...")
            # Push all branches and tags to the target remote
            # Force push is required after history rewrite
            push_success = lfs_handler.push(remote=TARGET_REPO_URL, force=True)
            
            if push_success:
                print(f"\nSuccessfully pushed all branches and tags to {TARGET_REPO_URL}")
            else:
                print(f"\nError: Failed to push changes to {TARGET_REPO_URL}. Check logs above.")
        else:
            print("\nError: LFS migration failed. Push operation cancelled.")
            
    else:
        print("No large files found to convert to LFS")

