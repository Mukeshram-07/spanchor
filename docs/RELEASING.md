# SPANCHOR Release Process

## Current Release

**Latest Public Release**: v0.1.0  
**Release Date**: September 30, 2026  
**PyPI**: https://pypi.org/project/spanchor/0.1.0/

---

## Release Workflow

The SPANCHOR project uses automated release publishing with GitHub Actions and PyPI Trusted Publishing (OIDC).

### Release Flow

```
1. Update package version in pyproject.toml
   ↓
2. Run full test suite locally
   ↓
3. Run ruff linting locally
   ↓
4. Run mypy --strict locally
   ↓
5. Commit version change
   ↓
6. Create annotated Git tag (v0.x.y)
   ↓
7. Push tag to GitHub
   ↓
8. GitHub Actions: Validate job
   - Verify tag matches package version
   - Run pytest
   - Run ruff
   - Run mypy
   ↓
9. GitHub Actions: Build job (depends on Validate)
   - Build wheel (.whl)
   - Build source distribution (.tar.gz)
   - Verify with twine
   ↓
10. GitHub Actions: Publish job (depends on Build)
    - Download built artifacts
    - Publish to PyPI using Trusted Publishing / OIDC
    ↓
11. PyPI: Package available at https://pypi.org/project/spanchor/
```

---

## Release Workflow Details

### Trigger

The release workflow (`.github/workflows/release.yml`) is triggered when a Git tag matching the pattern `v*` is pushed:

```bash
git push origin v0.1.1  # Triggers release workflow
```

### Version Tag Format

Release tags use semantic versioning with a `v` prefix:

- `v0.1.0` — initial release (current)
- `v0.1.1` — patch release
- `v0.2.0` — minor release
- `v1.0.0` — major release

### Validation Job

The `validate` job runs first and ensures:

1. **Tag ↔ Version Match**: Git tag version must exactly match `pyproject.toml` version
   ```
   Tag:  v0.1.1
   Version: 0.1.1  ✓ match
   ```

2. **Full Test Suite**: All 735+ pytest tests must pass
3. **Linting**: ruff must find no blocking issues
4. **Type Safety**: mypy --strict must pass on src/spanchor

**If validation fails**: Release is **blocked**, no publication occurs.

### Build Job

The `build` job (depends on `validate` passing):

1. Checks out the tagged commit
2. Builds wheel distribution: `dist/*.whl`
3. Builds source distribution: `dist/*.tar.gz`
4. Validates with `twine check` (verifies metadata)
5. Uploads distributions as GitHub Actions artifact

**If build fails**: Publication is **blocked**.

### Publish Job

The `publish` job (depends on `build` passing):

1. Downloads the artifacts
2. Publishes to PyPI using GitHub Actions OIDC Trusted Publishing
3. Uses `pypa/gh-action-pypi-publish` official action

---

## PyPI Trusted Publishing (OIDC)

SPANCHOR uses PyPI Trusted Publishing with OIDC for secure, token-free publishing.

### How It Works

1. **GitHub Action** requests a time-limited OIDC token from GitHub
2. **PyPI** verifies the OIDC token came from the trusted GitHub Actions workflow
3. **PyPI** confirms the repository and workflow match the configured Trusted Publisher
4. **Publication** proceeds without any stored credentials

### Security Benefits

- ✅ No PyPI API token in repository secrets
- ✅ No permanent credentials
- ✅ Automatic, short-lived tokens only
- ✅ Cryptographically verified GitHub Actions identity
- ✅ Auditable: each publish tied to a specific GitHub Actions run

### Configuration Requirements

#### GitHub-Side (Repository)

**Status**: ✅ **COMPLETE**

The release workflow (`.github/workflows/release.yml`) has:
- `permissions: id-token: write` — allows GitHub to issue OIDC token
- `pypa/gh-action-pypi-publish@release/v1` — official action that uses OIDC

**No manual GitHub configuration needed.**

#### PyPI-Side (Project Account)

**Status**: ⏳ **REQUIRES MANUAL CONFIGURATION**

The PyPI project account must have a Trusted Publisher configured for:

- **Publisher**: GitHub
- **Repository Name**: `Mukeshram-07/spanchor`
- **Workflow Name**: `release.yml`
- **Workflow Ref Branch**: `master` (or `main` if applicable)
- **Workflow Trigger Event**: `push` (tag events trigger via push)

**How to Configure on PyPI**:

1. Go to: https://pypi.org/manage/projects/
2. Select the SPANCHOR project
3. Navigate to: **Publishing** → **Trusted Publishers**
4. Click: **Add a New Trusted Publisher**
5. Select: **GitHub**
6. Fill in:
   - **Repository Name**: `Mukeshram-07/spanchor`
   - **Workflow Name**: `release.yml`
   - **Workflow Ref (branch)**: `master`
7. Save

Once configured, the next tagged release will automatically publish to PyPI.

---

## Future Release Example

This is documentation only. **DO NOT execute these commands yet.**

```bash
# 1. Update version in pyproject.toml
# (edit pyproject.toml: version = "0.1.1")

# 2. Run full quality checks locally
python -m pytest
ruff check .
mypy --strict src/spanchor

# 3. Commit version change
git add pyproject.toml
git commit -m "Release v0.1.1"

# 4. Create annotated tag
git tag -a v0.1.1 -m "Release v0.1.1"

# 5. Push commit
git push origin master

# 6. Push tag (triggers release workflow)
git push origin v0.1.1

# 7. Watch GitHub Actions
# https://github.com/Mukeshram-07/spanchor/actions/workflows/release.yml

# 8. Verify on PyPI
# https://pypi.org/project/spanchor/0.1.1/
```

---

## Rollback / Handling Failed Releases

If a release fails:

1. **Fix the issue** (e.g., failing test, version mismatch)
2. **Do NOT delete the tag**
3. **Create a new tag** with the next version (e.g., v0.1.2)
4. **Push the new tag**
5. The workflow will run again with the new version

Example:
```bash
# v0.1.1 failed due to test failure
# Fix the test locally
git add src/spanchor/...
git commit -m "Fix test for v0.1.1"
git tag -a v0.1.2 -m "Release v0.1.2"
git push origin master
git push origin v0.1.2
```

---

## Verifying a Release

After a release is published:

```bash
# Install from PyPI
pip install spanchor==0.1.1

# Verify version
python -c "import spanchor; print(spanchor.__version__)"
# Output: 0.1.1

# Verify CLI
spanchor --help
```

---

## Version Numbering

SPANCHOR follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 0.1.0)
- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible features
- **PATCH**: Backward-compatible bug fixes

Current: **0.1.0** (initial release, alpha status)

---

## CI/CD Integration

Once a release is published to PyPI, it's automatically available for:

```bash
pip install spanchor
pip install spanchor==0.1.1
pip install spanchor>=0.1.0
```

No manual post-release steps needed.

---

## Troubleshooting

### Tag version doesn't match package version

**Error**: "Tag version (0.1.1) does not match package version (0.1.0)"

**Solution**: Make sure `pyproject.toml` version is updated before creating the tag.

```bash
# Check current version
grep '^version' pyproject.toml

# Update pyproject.toml, commit, then create tag
```

### Tests fail during release

**Error**: Release workflow fails at `Run pytest` step

**Solution**: The release was blocked intentionally. Fix the test, commit, and create a new tag.

### Build fails

**Error**: Build job produces errors

**Solution**: Run `python -m build` locally to diagnose, fix, then create a new release tag.

### PyPI Trusted Publisher not configured

**Error**: Publish job fails with OIDC error

**Solution**: Configure the Trusted Publisher on PyPI (see **PyPI-Side Configuration** above).

---

## References

- [PyPI Trusted Publishing Docs](https://docs.pypi.org/trusted-publishers/)
- [GitHub OIDC Tokens](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/using-openid-connect-with-your-deployments)
- [Semantic Versioning](https://semver.org/)
- [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)

---

## Support

For release-related issues:

1. Check the [GitHub Actions logs](https://github.com/Mukeshram-07/spanchor/actions/workflows/release.yml)
2. Verify PyPI Trusted Publisher is configured
3. Ensure `pyproject.toml` version matches the Git tag
4. Run quality checks locally before releasing

---

**Last Updated**: September 30, 2026  
**Release Workflow Status**: Ready for v0.1.1 and beyond
