# Contributing to OmniConvert

Thank you for your interest in contributing to **OmniConvert**! We welcome bug fixes, performance improvements, new format converters, and feature enhancements.

---

## 🚀 How to Contribute

### 1. Fork & Clone
Fork the repository on GitHub and clone your fork locally:
```bash
git clone https://github.com/your-username/OmniConvert.git
cd OmniConvert
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/my-cool-feature
```

### 3. Install Dependencies & Set Up
```bash
pip install -r requirements.txt
```

### 4. Implement Your Changes
- Ensure code complies with PEP 8 standards.
- Keep converter modules decoupled inside `converters/`.
- Preserve pre-existing docstrings and comments.

### 5. Run the Test Suite
Ensure all test cases pass before submitting a pull request:
```bash
python test_converters.py
python verify_ownership.py
```

### 6. Commit & Push
```bash
git commit -m "feat: add support for XYZ format"
git push origin feature/my-cool-feature
```

### 7. Open a Pull Request
Submit a pull request to the `main` branch with a clear description of your changes.

---

## 📜 Code of Conduct

All contributors are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
