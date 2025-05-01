#!/usr/bin/env python3
import os
import sys
import logging
import argparse
import time
from git_lfs import GitLFS
from typing import List, Dict, Any

def find_large_files_and_prepare_lfs(repo_path: str, size_threshold_mb: int = 5, 
                                   target_repo_url: str = None, batch_size: int = 0) -> bool:
    """
    Production-grade function to find large files, prepare LFS tracking,
    and push to target repository.
    
    Args:
        repo_path: Path to the Git repository
        size_threshold_mb: Minimum file size to consider as large (in MB)
        target_repo_url: Target repository URL for push (if None, just prepare LFS)
        batch_size: Number of branches to push in each batch (0 = all at once)
        
    Returns:
        True if successful, False otherwise
    """
    # Set up logging
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('git_lfs_migration.log')
        ]
    )
    logger = logging.getLogger('LFSMigration')
    logger.info(f"Starting LFS migration for repository: {repo_path}")
    logger.info(f"Size threshold: {size_threshold_mb}MB")
    
    start_time = time.time()
    
    # Initialize GitLFS
    try:
        lfs_handler = GitLFS(repo_path=repo_path, log_level=logging.INFO)
    except Exception as e:
        logger.error(f"Failed to initialize GitLFS: {e}")
        return False
    
    # Verify repository
    if not os.path.exists(os.path.join(repo_path, '.git')):
        logger.error(f"Invalid Git repository path: {repo_path}")
        return False
    
    # Ensure LFS is installed
    if not lfs_handler.is_lfs_installed():
        logger.info("Git LFS not installed. Installing...")
        if not lfs_handler.install_lfs():
            logger.error("Failed to install Git LFS. Please install manually.")
            return False
    
    # Optimize git config for large repositories
    logger.info("Optimizing Git configuration for large repository handling...")
    lfs_handler.optimize_for_large_repo()
    
    # Find large files
    logger.info(f"Scanning repository for files larger than {size_threshold_mb}MB...")
    large_files = lfs_handler.find_large_files(size_threshold_mb=size_threshold_mb)
    
    if not large_files:
        logger.info("No large files found that meet the threshold criteria.")
        return True

   # Log large file findings
   logger.info(f"Found {len(large_files)} large files:")
   for i, file in enumerate(sorted(large_files, key=lambda x: x['size_mb'], reverse=True)):
       if i < 20:  # Only print the top 20
           logger.info(f"  {file['path']} ({file['size_mb']} MB)")
       elif i == 20:
           logger.info(f"  ... and {len(large_files) - 20} more files")
   
   # Create/update .gitattributes
   logger.info("Creating .gitattributes file for LFS tracking...")
   lfs_handler.create_gitattributes(large_files)
   
   # Collect unique extensions from large files
   extensions = set()
   for file in large_files:
       path = file['path']
       _, ext = os.path.splitext(path)
       if ext:
           extensions.add(ext.lstrip('.'))
   
   # Create migration batch lists by grouping extensions
   logger.info(f"Found {len(extensions)} unique file extensions to migrate")
   extensions_list = list(extensions)
   
   # Prepare patterns for migration
   patterns = [f"*.{ext}" for ext in extensions_list]
   
   # Add exact paths for large files without extensions
   for file in large_files:
       path = file['path']
       _, ext = os.path.splitext(path)
       if not ext:
           patterns.append(path)
   
   # Start LFS migration
   logger.info("Starting LFS migration process...")
   migration_results = {}
   
   for pattern in patterns:
       logger.info(f"Migrating files matching: {pattern}")
       success = lfs_handler.migrate_import(
           file_pattern=pattern, 
           include_all_branches=True,
           above_size=f"{size_threshold_mb}MB"
       )
       migration_results[pattern] = success
       
       if not success:
           logger.error(f"Migration failed for pattern: {pattern}")
   
   # Check results
   failed_patterns = [p for p, success in migration_results.items() if not success]
   if failed_patterns:
       logger.warning(f"Migration failed for {len(failed_patterns)} patterns:")
       for pattern in failed_patterns:
           logger.warning(f"  - {pattern}")
   
   # Verify LFS objects
   logger.info("Verifying LFS objects...")
   lfs_handler.verify_lfs_objects()
   
   # Get LFS status
   lfs_status = lfs_handler.status()
   if lfs_status:
       logger.info("LFS Status:")
       if lfs_status.get('tracked_files'):
           logger.info(f"  Tracked files: {len(lfs_status['tracked_files'])}")
       if lfs_status.get('not_tracked'):
           logger.warning(f"  Files not tracked by LFS: {len(lfs_status['not_tracked'])}")
   
   # Push to target repo if specified
   if target_repo_url:
       logger.info(f"Pushing repository to target: {target_repo_url}")
       push_success = lfs_handler.push(
           remote=target_repo_url,
           force=True,  # Force push is required after history rewrite
           batch_size=batch_size
       )
       
       if push_success:
           logger.info(f"Successfully pushed to target repository")
       else:
           logger.error(f"Failed to push to target repository")
           return False
   
   # Clean up
   logger.info("Cleaning up LFS cache...")
   lfs_handler.cleanup()
   
   elapsed_time = time.time() - start_time
   logger.info(f"LFS migration completed in {elapsed_time:.2f} seconds")
   
   return True

def parse_arguments():
   """Parse command line arguments"""
   parser = argparse.ArgumentParser(description='Git LFS Migration Tool')
   parser.add_argument('--repo-path', '-r', required=True, help='Path to Git repository')
   parser.add_argument('--size-threshold', '-s', type=int, default=5, help='Size threshold in MB (default: 5)')
   parser.add_argument('--target-repo', '-t', help='Target repository URL to push to')
   parser.add_argument('--batch-size', '-b', type=int, default=0, help='Batch size for pushing branches (0 = all at once)')
   parser.add_argument('--log-file', '-l', default='git_lfs_migration.log', help='Log file path')
   return parser.parse_args()

def main():
   """Main entry point"""
   args = parse_arguments()
   
   # Set up logging to file
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       filename=args.log_file
   )
   console = logging.StreamHandler()
   console.setLevel(logging.INFO)
   formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
   console.setFormatter(formatter)
   logging.getLogger('').addHandler(console)
   
   logger = logging.getLogger('Main')
   logger.info("Starting Git LFS migration process")
   
   success = find_large_files_and_prepare_lfs(
       repo_path=args.repo_path,
       size_threshold_mb=args.size_threshold,
       target_repo_url=args.target_repo,
       batch_size=args.batch_size
   )
   
   if success:
       logger.info("✅ Migration completed successfully!")
       return 0
   else:
       logger.error("❌ Migration failed!")
       return 1

if __name__ == "__main__":
   sys.exit(main())