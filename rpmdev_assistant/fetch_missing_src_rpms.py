# -*- coding: utf-8 -*-
import argparse
from utils import get_missing_deps, download_src_rpms, extract_src_rpms


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=(
            'Fetch and extract source packages for missing '
            'dependenices for a package.')
    )
    parser.add_argument('package_name', help='Package name')
    parser.add_argument('--source-enablerepos', help='Source repositories enabled.')
    parser.add_argument('--source-disablerepos', help='Source repositories disabled.')
    parser.add_argument('--target-enablerepos', help='Target repositories enabled.')
    parser.add_argument('--target-disablerepos', help='Target repositories disabled.')
    args = parser.parse_args()
    def parse_repo_args(value):
        return [
            item for item in (value or '').split(',') if item
        ]

    deps_graph = get_missing_deps(
        args.package_name,
        source_enablerepos=parse_repo_args(args.source_enablerepos),
        source_disablerepos=parse_repo_args(args.source_disablerepos),
        target_enablerepos=parse_repo_args(args.target_enablerepos),
        target_disablerepos=parse_repo_args(args.target_disablerepos)
    )
    download_src_rpms(deps_graph.keys())
    extract_src_rpms()
