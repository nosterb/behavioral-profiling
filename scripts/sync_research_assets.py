#!/usr/bin/env python3
"""
Sync research assets to S3/CloudFront CDN.

Scans MAIN_RESEARCH_BRIEF.md for file references, uploads them to S3,
and generates MAIN_RESEARCH_BRIEF_PUBLIC.md with CDN URLs.

Usage:
    python3 scripts/sync_research_assets.py
    python3 scripts/sync_research_assets.py --dry-run
    python3 scripts/sync_research_assets.py --invalidate
"""

import os
import re
import json
import argparse
import subprocess
from pathlib import Path
from typing import Set, Dict, List, Tuple
from datetime import datetime

# Load .env file if it exists
def load_dotenv():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_dotenv()

# Configuration - set via environment or defaults
CDN_BUCKET = os.environ.get('CDN_BUCKET', 'behavioral-profiling-public')
CDN_DOMAIN = os.environ.get('CDN_DOMAIN', '')  # e.g., 'd1234567890.cloudfront.net'
CDN_DISTRIBUTION_ID = os.environ.get('CDN_DISTRIBUTION_ID', '')

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RESEARCH_SYNTHESIS = PROJECT_ROOT / 'outputs' / 'behavioral_profiles' / 'research_synthesis'
MAIN_BRIEF = RESEARCH_SYNTHESIS / 'MAIN_RESEARCH_BRIEF.md'
PUBLIC_BRIEF = RESEARCH_SYNTHESIS / 'MAIN_RESEARCH_BRIEF_PUBLIC.md'
BEHAVIORAL_PROFILES = PROJECT_ROOT / 'outputs' / 'behavioral_profiles'

# Condition names for <condition> template expansion
CONDITIONS = ['baseline', 'authority', 'urgency', 'minimal_steering', 'telemetryV3', 'reminder']

# File patterns to look for
FILE_PATTERNS = [
    # Markdown image syntax: ![alt](path)
    r'!\[([^\]]*)\]\(([^)]+\.png)\)',
    # Backtick references to files
    r'`([^`]+\.(png|json|md))`',
    # See/Full analysis references
    r'(?:See|Full analysis)[:\s]+`?([^`\s]+\.(png|json|md))`?',
]

# MIME types for S3 upload
MIME_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.json': 'application/json',
    '.md': 'text/markdown',
    '.csv': 'text/csv',
}


def find_file_references(content: str) -> Set[str]:
    """Extract all file references from markdown content."""
    references = set()

    for pattern in FILE_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            # Get the file path (could be in different capture groups)
            groups = match.groups()
            for group in groups:
                if group and ('.' in group) and any(group.endswith(ext) for ext in ['.png', '.json', '.md', '.csv']):
                    references.add(group)

    # Expand <condition> templates
    expanded = set()
    for ref in references:
        if '<condition>' in ref:
            for condition in CONDITIONS:
                expanded.add(ref.replace('<condition>', condition))
        else:
            expanded.add(ref)

    # Expand glob patterns (e.g., provider_constraint_*.json)
    final = set()
    for ref in expanded:
        if '*' in ref:
            # Find matching files
            glob_matches = list(BEHAVIORAL_PROFILES.glob('**/' + Path(ref).name))
            if glob_matches:
                for match in glob_matches:
                    try:
                        final.add(str(match.relative_to(BEHAVIORAL_PROFILES)))
                    except ValueError:
                        final.add(match.name)
            else:
                final.add(ref)  # Keep original if no matches
        else:
            final.add(ref)

    return final


def resolve_file_path(reference: str) -> Path | None:
    """Resolve a file reference to an actual path."""
    # Try relative to research_synthesis
    path = RESEARCH_SYNTHESIS / reference
    if path.exists():
        return path

    # Try relative to behavioral_profiles
    path = BEHAVIORAL_PROFILES / reference
    if path.exists():
        return path

    # Try relative to project root
    path = PROJECT_ROOT / reference
    if path.exists():
        return path

    # Try with outputs prefix
    path = PROJECT_ROOT / 'outputs' / 'behavioral_profiles' / reference
    if path.exists():
        return path

    # Try condition directories
    for condition in CONDITIONS:
        path = BEHAVIORAL_PROFILES / condition / reference
        if path.exists():
            return path
        # Try without condition prefix if reference includes it
        if reference.startswith(f'{condition}/'):
            path = BEHAVIORAL_PROFILES / reference
            if path.exists():
                return path

    # Recursive search by filename in behavioral_profiles
    filename = Path(reference).name
    matches = list(BEHAVIORAL_PROFILES.glob(f'**/{filename}'))
    if matches:
        return matches[0]

    # Recursive search in research_synthesis
    matches = list(RESEARCH_SYNTHESIS.glob(f'**/{filename}'))
    if matches:
        return matches[0]

    return None


def get_s3_key(local_path: Path) -> str:
    """Generate S3 key from local path."""
    # Make path relative to behavioral_profiles
    try:
        relative = local_path.relative_to(BEHAVIORAL_PROFILES)
        return str(relative)
    except ValueError:
        # Fallback: use filename only
        return local_path.name


def sync_to_s3(dry_run: bool = False) -> bool:
    """Sync behavioral_profiles directory to S3 using aws s3 sync (skips unchanged files)."""
    s3_uri = f's3://{CDN_BUCKET}/'

    if dry_run:
        print(f"  [DRY RUN] Would sync: {BEHAVIORAL_PROFILES} -> {s3_uri}")
        cmd = [
            'aws', 's3', 'sync',
            str(BEHAVIORAL_PROFILES),
            s3_uri,
            '--dryrun',
            '--exclude', '*.pyc',
            '--exclude', '__pycache__/*',
            '--exclude', '.DS_Store',
        ]
    else:
        cmd = [
            'aws', 's3', 'sync',
            str(BEHAVIORAL_PROFILES),
            s3_uri,
            '--exclude', '*.pyc',
            '--exclude', '__pycache__/*',
            '--exclude', '.DS_Store',
        ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            # Count uploads from output
            lines = [l for l in result.stdout.strip().split('\n') if l]
            if lines:
                for line in lines[:20]:  # Show first 20
                    print(f"  {line}")
                if len(lines) > 20:
                    print(f"  ... and {len(lines) - 20} more")
                print(f"  Total: {len(lines)} files synced")
            else:
                print("  All files up to date (nothing to sync)")
        else:
            print("  All files up to date (nothing to sync)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR syncing: {e.stderr}")
        return False


def generate_cdn_url(s3_key: str) -> str:
    """Generate CDN URL for an S3 key."""
    if CDN_DOMAIN:
        return f'https://{CDN_DOMAIN}/{s3_key}'
    else:
        # Fallback to S3 URL
        return f'https://{CDN_BUCKET}.s3.amazonaws.com/{s3_key}'


def rewrite_brief_with_cdn_urls(content: str, url_map: Dict[str, str]) -> str:
    """Rewrite file references to use CDN URLs."""
    result = content

    # Build a filename -> cdn_url lookup for short references
    filename_to_url = {}
    for local_ref, cdn_url in url_map.items():
        filename = Path(local_ref).name
        # Prefer more specific paths, but allow filename-only lookup
        if filename not in filename_to_url:
            filename_to_url[filename] = cdn_url

    for local_ref, cdn_url in url_map.items():
        filename = Path(local_ref).name

        # Replace backtick references with links (full path)
        if local_ref.endswith('.md') or local_ref.endswith('.json') or local_ref.endswith('.csv'):
            result = re.sub(
                rf'`{re.escape(local_ref)}`',
                f'[{filename}]({cdn_url})',
                result
            )

        # Replace image references (full path)
        if local_ref.endswith('.png'):
            result = re.sub(
                rf'!\[([^\]]*)\]\({re.escape(local_ref)}\)',
                rf'![\1]({cdn_url})',
                result
            )

        # Replace See/Full analysis references (full path)
        result = re.sub(
            rf'((?:See|Full analysis)[:\s]+)`?{re.escape(local_ref)}`?',
            rf'\1[{filename}]({cdn_url})',
            result,
            flags=re.IGNORECASE
        )

    # Second pass: replace filename-only references that weren't matched
    for filename, cdn_url in filename_to_url.items():
        # Replace backtick references by filename only
        if filename.endswith('.md') or filename.endswith('.json') or filename.endswith('.csv'):
            result = re.sub(
                rf'`{re.escape(filename)}`',
                f'[{filename}]({cdn_url})',
                result
            )

        # Replace PNG references by filename only
        if filename.endswith('.png'):
            # Backtick PNG references
            result = re.sub(
                rf'`{re.escape(filename)}`',
                f'[{filename}]({cdn_url})',
                result
            )
            # Image syntax
            result = re.sub(
                rf'!\[([^\]]*)\]\({re.escape(filename)}\)',
                rf'![\1]({cdn_url})',
                result
            )

    return result


def add_image_embeds(content: str, url_map: Dict[str, str]) -> str:
    """Add inline image embeds for PNG references that aren't already images."""
    result = content

    for local_ref, cdn_url in url_map.items():
        if not local_ref.endswith('.png'):
            continue

        filename = Path(local_ref).name

        # If there's a link to a PNG that's not an image tag, add the image
        # Pattern: [filename](url) not preceded by !
        link_pattern = rf'(?<!!)\[{re.escape(filename)}\]\({re.escape(cdn_url)}\)'

        # Replace with image followed by link
        replacement = f'![{filename}]({cdn_url})\n\n*[View full size]({cdn_url})*'
        result = re.sub(link_pattern, replacement, result)

    return result


def invalidate_cloudfront(paths: List[str], dry_run: bool = False) -> bool:
    """Invalidate CloudFront cache for updated paths."""
    if not CDN_DISTRIBUTION_ID:
        print("  No CDN_DISTRIBUTION_ID set, skipping invalidation")
        return True

    if dry_run:
        print(f"  [DRY RUN] Would invalidate {len(paths)} paths")
        return True

    # Invalidate all for simplicity (or could invalidate specific paths)
    try:
        cmd = [
            'aws', 'cloudfront', 'create-invalidation',
            '--distribution-id', CDN_DISTRIBUTION_ID,
            '--paths', '/*'
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  CloudFront invalidation created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR invalidating CloudFront: {e.stderr.decode()}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Sync research assets to CDN')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without doing it')
    parser.add_argument('--invalidate', action='store_true', help='Invalidate CloudFront cache after upload')
    parser.add_argument('--no-rewrite', action='store_true', help='Upload only, do not generate public brief')
    args = parser.parse_args()

    print("=" * 60)
    print("Research Assets CDN Sync")
    print("=" * 60)
    print(f"Bucket: {CDN_BUCKET}")
    print(f"CDN Domain: {CDN_DOMAIN or '(not set - using S3 URLs)'}")
    print(f"Source: {MAIN_BRIEF}")
    print()

    # Check if main brief exists
    if not MAIN_BRIEF.exists():
        print(f"ERROR: {MAIN_BRIEF} not found")
        return 1

    # Read the brief
    content = MAIN_BRIEF.read_text()

    # Find all file references
    print("Scanning for file references...")
    references = find_file_references(content)
    print(f"Found {len(references)} unique file references")
    print()

    # Sync entire directory to S3 (skips unchanged files)
    print("Syncing to S3 (unchanged files will be skipped)...")
    sync_success = sync_to_s3(args.dry_run)

    if not sync_success:
        print("ERROR: S3 sync failed")
        return 1

    # Build URL map for referenced files
    print()
    print("Resolving file references for URL rewriting...")
    url_map = {}  # local_ref -> cdn_url
    not_found = 0

    for ref in sorted(references):
        local_path = resolve_file_path(ref)
        if local_path is None:
            print(f"  NOT FOUND: {ref}")
            not_found += 1
            continue

        s3_key = get_s3_key(local_path)
        url_map[ref] = generate_cdn_url(s3_key)

    print(f"Resolved {len(url_map)} file references, {not_found} not found")

    # Generate public brief with CDN URLs
    if not args.no_rewrite and url_map:
        print()
        print("Generating public brief with CDN URLs...")

        public_content = rewrite_brief_with_cdn_urls(content, url_map)

        if args.dry_run:
            print(f"  [DRY RUN] Would write: {PUBLIC_BRIEF}")
        else:
            PUBLIC_BRIEF.write_text(public_content)
            print(f"  Written: {PUBLIC_BRIEF}")

    # Invalidate CloudFront if requested
    if args.invalidate:
        print()
        print("Invalidating CloudFront cache...")
        invalidate_cloudfront(list(url_map.values()), args.dry_run)

    print()
    print("=" * 60)
    print("Done!")
    if not args.dry_run and url_map:
        print(f"Public brief: {PUBLIC_BRIEF}")
        print(f"CDN base URL: https://{CDN_DOMAIN or f'{CDN_BUCKET}.s3.amazonaws.com'}/<path>")

    return 0


if __name__ == '__main__':
    exit(main())
