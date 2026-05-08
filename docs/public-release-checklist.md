# Public Release Checklist

Use this checklist before making the repository public.

## In the repository

- [x] Add a license file.
- [x] Add a security policy.
- [x] Add contribution guidelines.
- [x] Add a code of conduct.
- [x] Add a CI secret scan.
- [x] Review `.gitignore`.

## In GitHub settings

- Protect the default branch.
- Require pull requests before merging.
- Require status checks to pass before merging.
- Require review before merge if the repo has multiple maintainers.
- Enable secret scanning if it is available for the repository plan.
- Enable push protection if it is available.

## Before toggling public

- Re-run the deep secret scan.
- Confirm there are no personal credentials in Git history.
- Check repository settings for any accidental access grants.