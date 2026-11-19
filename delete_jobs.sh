#!/bin/bash

# Script to delete all jobs in storage/jobs/ folder

JOBS_DIR="$(dirname "$0")/storage/jobs"

if [ ! -d "$JOBS_DIR" ]; then
    echo "Error: $JOBS_DIR directory not found"
    exit 1
fi

# Count jobs before deletion
job_count=$(find "$JOBS_DIR" -maxdepth 1 -type d -name "job_*" | wc -l)

if [ "$job_count" -eq 0 ]; then
    echo "No jobs found to delete"
    exit 0
fi

echo "Found $job_count job(s) to delete"
echo "Deleting jobs in: $JOBS_DIR"

# Delete all job directories
rm -rf "$JOBS_DIR"/job_*

if [ $? -eq 0 ]; then
    echo "✓ Successfully deleted $job_count job(s)"
else
    echo "✗ Error deleting jobs"
    exit 1
fi
