# Password Health Analyzer

A privacy-focused, local-only tool designed to analyze password strength, detect reuse, and generate secure passwords. This application features a modern Tkinter GUI and a command-line interface for quick assessments.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

## 🚀 Features

- **Strength Analysis**:  Evaluates passwords on a 0–10 scale based on entropy, common dictionary words, and sequence patterns.
- **Reuse Detection**: Identifies exact duplicates and similar passwords (using similarity thresholds) to prevent security risks.
- **Secure Password Generator**: built-in generator using Python's `secrets` module for cryptographically strong passwords. Customizable constraints (length, uppercase, lowercase, digits, symbols).
- **Encrypted Storage**: Save and load your analyzed password lists securely. Uses `Fernet` (AES) encryption if `cryptography` is installed, with a secure fallback for standard library users.
- **Modern GUI**: A user-friendly interface built with Tkinter, featuring:
    - Dark Mode toggle
    - Tooltips and keyboard shortcuts
    - Responsive layout
- **CLI Support**: Quick command-line checks for strength and reuse testing.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/BenkacemIbrahim/password-health-analyzer.git
    cd password-health-analyzer
    ```

2.  **Install dependencies:**
    The application runs with standard Python libraries. For enhanced security (Fernet encryption), install the optional `cryptography` package:
    ```bash
    pip install -r requirements.txt
    ```

## 💻 Usage

### Graphical User Interface (GUI)
Run the main script to launch the application:
```bash
python main.py
```
- **Add Password**: specificy passwords to analyze.
- **Analyze Strength**: Select a password to see detailed metrics.
- **Check Reuses**: Scan the list for duplicate or similar passwords.
- **Generate**: Create new, strong passwords.
- **Save/Load**: Encrypt and save your session to a `.pha` file.

### Command Line Interface (CLI)

Check a single password's strength:
```bash
python main.py --password "YourP@ssw0rd"
```

Run a sample reuse detection test:
```bash
python main.py --test-reuse
```

## ⌨️ Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+A` | Add Password |
| `Ctrl+E` | Analyze Last Password |
| `Ctrl+R` | Check Reuses |
| `Ctrl+G` | Generate Password |
| `Ctrl+C` | Copy Generated Password |
| `Ctrl+S` | Save List |
| `Ctrl+O` | Load List |
| `Ctrl+L` | Clear List |
| `F2`     | Toggle Dark Mode |

## 🔒 Security Note

- **Local Only**: No data is ever sent to the cloud. All analysis happens locally on your machine.
- **No Logging**: Passwords are not logged.
- **Encryption**: If saving lists, they are encrypted with a user-provided master password.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
