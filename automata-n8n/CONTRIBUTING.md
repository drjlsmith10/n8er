# Contributing to Project Automata

Thank you for your interest in contributing to Project Automata! 🎉

We welcome contributions from everyone. This document provides guidelines for contributing to the project.

---

## 🌟 Ways to Contribute

### 1. **Report Bugs** 🐛
Found a bug? Please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error messages or logs

### 2. **Suggest Features** 💡
Have an idea? Open a feature request with:
- Problem you're trying to solve
- Proposed solution
- Why it would benefit users
- Any implementation ideas

### 3. **Improve Documentation** 📚
Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples
- Improve getting started guides
- Translate documentation

### 4. **Contribute Code** 💻
Submit pull requests for:
- Bug fixes
- New features
- Performance improvements
- Code quality improvements

### 5. **Share Workflow Patterns** 🔄
Add community-learned workflow patterns:
- Real-world n8n workflows
- Error solutions you've discovered
- Node usage tips
- Best practices

### 6. **Help Others** 🤝
Support the community by:
- Answering questions in issues
- Helping debug problems
- Sharing your use cases
- Writing tutorials or blog posts

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- git
- Basic knowledge of n8n (helpful but not required)

### Setup Development Environment

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/n8er.git
cd n8er/automata-n8n

# 3. Add upstream remote
git remote add upstream https://github.com/drjlsmith10/n8er.git

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# 6. Run tests to verify setup
pytest tests/ -v
```

### Keep Your Fork Updated

```bash
# Fetch latest changes from upstream
git fetch upstream

# Merge upstream changes into your main branch
git checkout main
git merge upstream/main

# Push updates to your fork
git push origin main
```

---

## 📝 Development Workflow

### 1. Create a Branch

```bash
# Create a new branch for your work
git checkout -b feature/my-new-feature

# Or for bug fixes
git checkout -b fix/issue-123
```

**Branch naming conventions:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test additions/improvements

### 2. Make Your Changes

**Code Style:**
- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and small
- Add inline comments for complex logic

**Example:**
```python
def generate_workflow(prompt: str, validate: bool = True) -> Dict:
    """
    Generate n8n workflow from natural language prompt.

    Args:
        prompt: Natural language description of workflow
        validate: Whether to validate generated workflow

    Returns:
        Dictionary containing workflow JSON

    Raises:
        ValueError: If prompt is empty or invalid
    """
    # Implementation here
    pass
```

### 3. Write Tests

**All new code must include tests:**

```python
# tests/test_my_feature.py
import pytest
from skills.my_feature import my_function

def test_my_function_basic():
    """Test basic functionality"""
    result = my_function("test input")
    assert result == "expected output"

def test_my_function_edge_case():
    """Test edge case handling"""
    with pytest.raises(ValueError):
        my_function("")
```

**Run tests:**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_my_feature.py -v

# Run with coverage
pytest tests/ --cov=skills --cov=agents --cov-report=html
```

### 4. Commit Your Changes

**Write clear commit messages:**

```bash
# Format: <type>: <description>
git commit -m "feat: Add workflow optimization engine"
git commit -m "fix: Resolve circular dependency detection bug"
git commit -m "docs: Update installation instructions"
git commit -m "test: Add tests for NL parser"
```

**Commit types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/improvements
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Good commit messages:**
✅ `feat: Add simulation engine for workflow testing`
✅ `fix: Handle empty node lists in parser (closes #123)`
✅ `docs: Add deployment guide for Docker`

**Bad commit messages:**
❌ `update`
❌ `fix bug`
❌ `changes`

### 5. Run Quality Checks

```bash
# Format code
black .

# Check code style
flake8 .

# Type checking
mypy skills/ agents/

# Run all tests
pytest tests/ -v

# Check test coverage
pytest tests/ --cov=. --cov-report=term-missing
```

### 6. Push to Your Fork

```bash
# Push your branch to your fork
git push origin feature/my-new-feature
```

### 7. Create Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Fill in the PR template
4. Link related issues (e.g., "Closes #123")
5. Wait for review

---

## 🎯 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Code follows style guidelines (`black .` and `flake8 .`)
- [ ] Documentation updated (if applicable)
- [ ] Changelog updated (if applicable)
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Should Include

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes Made
- Change 1
- Change 2

## Testing
How did you test this?

## Screenshots (if applicable)
Before/after screenshots

## Related Issues
Closes #123
Related to #456
```

### Detailed Code Review Process

Our code review process ensures quality, maintainability, and consistency:

#### 1. Automated Checks (Pre-Review)
Before any human review, automated checks must pass:
- **Tests**: `pytest tests/ -v` must pass all tests
- **Code Style**: `black .` and `flake8 .` must have 0 issues
- **Type Hints**: `mypy skills/ agents/` must pass
- **Coverage**: New code should not decrease coverage below 85%

```bash
# Run all checks locally before pushing
pytest tests/ -v
black . && isort .
flake8 .
mypy skills/ agents/
```

#### 2. Initial Triage
Maintainers review PR for:
- Clear PR description and title
- Linked related issues
- Appropriate branch name
- Commit messages follow conventions

**Expected Response:** 24-48 hours

#### 3. Code Review
Reviewer checks for:
- **Correctness**: Does the code solve the stated problem?
- **Design**: Is the solution well-architected?
- **Performance**: Are there performance implications?
- **Security**: Are there potential security issues?
- **Testing**: Is coverage adequate?
- **Documentation**: Is it documented?
- **Style**: Does it follow project conventions?

**Review Comments:**
- **MUST**: Critical issues that block merge
- **SHOULD**: Strong recommendations
- **NICE**: Suggestions for future improvement

#### 4. Iteration
Author addresses feedback:
- Push commits to same branch
- Reply to each comment
- Request re-review when complete

**No force-push** after review has started (makes conversation hard to follow)

#### 5. Approval and Merge
Once approved:
- At least 1 approval required for bug fixes
- At least 2 approvals required for features
- All conversations must be resolved
- All checks must pass
- Branch must be up-to-date with main

Maintainers will merge once criteria met.

**Typical Timeline:**
- Simple fixes: 1-2 days
- Medium features: 2-5 days
- Complex features: 5-10 days

---

## 🧪 Testing Guidelines

### Mandatory Test Requirements

**All contributions MUST pass these requirements:**

#### 1. Test Coverage
- **New features**: Must include tests with >85% line coverage
- **Bug fixes**: Must include regression test preventing re-occurrence
- **Overall project**: Must not decrease coverage below 85%
- **Critical paths**: Must have 95%+ coverage

#### 2. Test Types Required
- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **Regression tests**: Prevent fixes from breaking again
- **Edge case tests**: Handle boundary conditions

#### 3. Test Quality Standards
- Each test should be <20 lines of code
- Test should have single clear assertion (or related assertions)
- No dependencies between tests (can run in any order)
- Deterministic (same input = same output)
- Fast (most tests <100ms)
- Clear, descriptive names: `test_<function>_<scenario>_<expected_result>`

**Good test names:**
- ✅ `test_parse_workflow_valid_json_returns_parsed_workflow`
- ✅ `test_generate_workflow_with_zero_nodes_raises_error`
- ✅ `test_knowledge_base_lookup_missing_pattern_returns_none`

**Bad test names:**
- ❌ `test_parse`
- ❌ `test_error`
- ❌ `test_1`

### Test Structure

```python
def test_feature_name():
    """Test description"""
    # Arrange - Set up test data
    input_data = {...}

    # Act - Execute the code
    result = function_to_test(input_data)

    # Assert - Verify results
    assert result == expected_value
```

### Running Tests

```bash
# All tests (must pass before PR submission)
pytest tests/ -v

# Specific file
pytest tests/test_schema_validation.py

# Specific test
pytest tests/test_schema_validation.py::test_valid_workflow

# With coverage report
pytest tests/ --cov=skills --cov=agents --cov-report=html
# Coverage report will be in htmlcov/index.html

# Fast tests only
pytest -m "not slow"

# Verbose output
pytest -v

# Stop on first failure (useful for debugging)
pytest -x

# Run with warnings
pytest --tb=short

# See which tests are slowest
pytest --durations=10
```

### Test Requirements Checklist

Before submitting a PR, verify:
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage is adequate: `pytest --cov=skills --cov-report=term-missing`
- [ ] No coverage regression (coverage % doesn't decrease)
- [ ] All new functions have tests
- [ ] All edge cases are covered
- [ ] Test names are descriptive
- [ ] Tests are isolated (no dependencies)
- [ ] Tests are deterministic (reproducible results)

---

## 📚 Documentation Guidelines

### Docstring Format

Use Google-style docstrings:

```python
def parse_workflow(prompt: str, strict: bool = True) -> ParsedIntent:
    """
    Parse natural language prompt into workflow intent.

    Args:
        prompt: Natural language description of desired workflow
        strict: Whether to use strict parsing mode

    Returns:
        ParsedIntent object containing extracted information

    Raises:
        ValueError: If prompt is empty or invalid

    Example:
        >>> intent = parse_workflow("When webhook arrives, save to DB")
        >>> print(intent.trigger_type)
        'webhook'
    """
```

### Documentation Files

- **README.md** - Overview, quick start, main features
- **QUICKSTART.md** - 5-minute getting started
- **docs/DEPLOYMENT.md** - Deployment instructions
- **docs/architecture.md** - System architecture
- **Code comments** - Inline explanations for complex logic

---

## 🎨 Code Style Guidelines

### Python Style

Follow PEP 8 with these specifics:

```python
# Line length: 100 characters max
# Indentation: 4 spaces (no tabs)
# Quotes: Double quotes for strings
# Naming:
#   - Classes: PascalCase
#   - Functions: snake_case
#   - Constants: UPPER_SNAKE_CASE
#   - Private: _leading_underscore

# Good
class WorkflowParser:
    """Parse workflow descriptions."""

    def parse_prompt(self, prompt: str) -> ParsedIntent:
        """Parse natural language prompt."""
        return ParsedIntent(...)

# Use type hints
def generate_workflow(
    prompt: str,
    validate: bool = True,
    simulate: bool = False
) -> Dict[str, Any]:
    """Generate workflow with options."""
    pass

# Use f-strings
message = f"Generated {count} workflows"

# Use list comprehensions for simple transformations
active_nodes = [n for n in nodes if n.enabled]

# Use descriptive variable names
user_prompt = "..."  # Good
up = "..."          # Bad
```

### Import Order

```python
# 1. Standard library
import os
import sys
from typing import Dict, List

# 2. Third-party
import pytest
from dotenv import load_dotenv

# 3. Local
from skills.knowledge_base import KnowledgeBase
from agents import BaseAgent
```

---

## 🐛 Reporting Bugs

### Before Reporting

1. **Search existing issues** - Your bug may already be reported
2. **Try latest version** - Bug might be fixed in main branch
3. **Minimal reproduction** - Simplify to smallest reproducing case

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Install version X
2. Run command Y
3. See error Z

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11.0]
- Project Automata version: [e.g., 2.0.0]

**Error Messages**
```
Paste full error message here
```

**Additional Context**
Any other relevant information
```

---

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Problem**
What problem does this solve?

**Proposed Solution**
Describe your proposed solution

**Alternatives Considered**
Other solutions you've thought about

**Use Cases**
How would this be used?

**Additional Context**
Mock-ups, examples, etc.
```

---

## 🔒 Security Issues

**Do NOT report security vulnerabilities in public issues.**

Instead:
1. Email security concerns to: [your-security-email]
2. Include "SECURITY" in subject line
3. Provide detailed description
4. We'll respond within 48 hours

See [SECURITY.md](SECURITY.md) for details.

---

## 🏆 Recognition

Contributors are recognized in:
- **GitHub Contributors** page
- **Release notes** for significant contributions
- **README.md** (top contributors)

---

## 📜 Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

**Summary:**
- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

---

## 💬 Getting Help

**Need help contributing?**

- 💬 **GitHub Discussions** - Ask questions
- 📧 **Email** - [maintainer email]
- 🐛 **Issues** - Report bugs
- 📖 **Documentation** - Read the docs

---

## 📅 Release Process

### Semantic Versioning

Releases follow [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0) - Breaking changes (rare, careful consideration)
- **Minor** (0.X.0) - New features, backwards compatible
- **Patch** (0.0.X) - Bug fixes and security patches

**Release schedule:**
- Patch releases: As needed for bugs/security
- Minor releases: Monthly (typically first week)
- Major releases: When necessary (1-2 per year)

### How to Bump Versions

Maintainers handle version bumping, but you should know the process:

#### 1. Update Version Numbers
Update version in these files:
```bash
# Main version file
# Edit: setup.py
# Change: version="X.Y.Z"

# Python package versions
# Edit: skills/__init__.py, agents/__init__.py, config.py
# Change: __version__ = "X.Y.Z"

# Docker
# Edit: Dockerfile
# Add label: LABEL version="X.Y.Z"

# Documentation
# Edit: README.md, QUICKSTART.md
# Update any references to version numbers
```

#### 2. Update Changelog
Create entry in `docs/changelog.md`:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features here

### Changed
- Changes here

### Fixed
- Bug fixes here

### Security
- Security patches here
```

#### 3. Create Git Tag
```bash
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin vX.Y.Z
```

#### 4. Create GitHub Release
- Go to GitHub Releases
- Create new release from tag
- Add changelog entry as description
- Attach any binary artifacts

#### 5. Update Documentation
- Update deployment guides if needed
- Add release notes
- Update compatibility matrix

### Testing Before Release
Before releasing, verify:
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No critical issues in linting
- [ ] Documentation is updated
- [ ] Changelog is complete
- [ ] Version numbers are consistent
- [ ] Build succeeds: `python setup.py build`
- [ ] Docker image builds successfully
- [ ] No regressions vs previous version

### Documentation Requirements

#### For Code Changes
**All code PRs must include documentation:**

1. **Docstrings** (Google format)
   - All public functions/classes must have docstrings
   - Include Args, Returns, Raises sections
   - Add examples for complex functions

2. **Code Comments**
   - Complex logic needs inline comments
   - Non-obvious decisions should be explained
   - WHY, not WHAT (what is obvious from code)

3. **README Updates**
   - If new user-facing feature, update README.md
   - Add to features list if applicable
   - Update quick start if needed

4. **Architecture Updates**
   - If changing system design, update docs/architecture.md
   - Include diagrams if helpful
   - Document new modules/classes

5. **API Documentation**
   - If adding new skills/agents, document API
   - Include usage examples
   - Document parameters and return values

#### For Feature Contributions
**Feature PRs need comprehensive documentation:**

1. **QUICKSTART.md Update**
   - Add example of using new feature
   - Keep it brief (5 minutes max)

2. **docs/DEPLOYMENT.md Update**
   - If feature affects deployment, document it
   - Add configuration options
   - Include troubleshooting

3. **Example Workflows**
   - Add workflow example for new capability
   - Place in `workflows/examples/`
   - Include explanatory comments

#### For Bug Fix Contributions
**Bug fixes need:**
1. Test case demonstrating the bug
2. Comment explaining fix
3. Changelog entry

### Documentation Format Standards

**Use Markdown for all documentation:**
```markdown
# Heading 1 (one per file)

## Heading 2 (main sections)

### Heading 3 (subsections)

**Bold** for emphasis
`code` for inline code
```code block```  for multi-line code
- Lists for non-ordered items
1. Numbered lists for steps
[Link text](URL) for links
```

**Code Examples:**
- Include import statements
- Should be runnable/complete
- Use realistic examples
- Include expected output

**Diagrams:**
- Use ASCII diagrams for simple flows
- Consider using Mermaid for complex diagrams
- Always have alt text describing diagram

---

## 🎓 Learning Resources

**New to open source?**
- [First Contributions](https://github.com/firstcontributions/first-contributions)
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)

**New to n8n?**
- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)

**New to Python?**
- [Python Official Tutorial](https://docs.python.org/3/tutorial/)
- [Real Python](https://realpython.com/)

---

## 🙏 Thank You!

Every contribution helps make Project Automata better. Whether you're:
- Fixing a typo
- Reporting a bug
- Adding a feature
- Helping others

**You're making a difference. Thank you!** ❤️

---

**Questions?** Open a discussion on GitHub or reach out to maintainers.

**Happy contributing!** 🚀
