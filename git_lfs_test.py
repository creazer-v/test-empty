from git_lfs import GitLFS

# Initialize with repo path (or use current directory)
lfs = GitLFS("/path/to/repository")

# Check if Git LFS is installed
if not lfs.is_lfs_installed():
    print("Installing Git LFS...")
    lfs.install_lfs()

# Track large file patterns
lfs.track_file("*.psd")
lfs.track_file("*.zip")
lfs.track_file("*.mp4")

# Check for large files in the repository
large_files = lfs.check_large_files(size_threshold_mb=50)
for file in large_files:
    print(f"Large file found: {file['path']} ({file['size_mb']} MB)")
    
# Add and commit the .gitattributes file (which tracks LFS patterns)
lfs.add_file(".gitattributes")
lfs.commit("Add LFS tracking for large files")

# Add large files to git
for file in large_files:
    lfs.add_file(file['path'])

# Commit the large files
lfs.commit("Add large files using Git LFS")

# Push to GitHub
lfs.push("origin", "main")

# Show LFS status
status = lfs.status()
print(f"Tracked files: {status['tracked_files']}")
