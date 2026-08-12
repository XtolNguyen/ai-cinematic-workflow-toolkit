# Security Policy

Security reports for **AI Cinematic Workflow Toolkit** are taken seriously.

Please follow this policy when reporting a potential vulnerability.

---

## Supported Versions

The project is currently in early development.

| Version                      | Supported |
| ---------------------------- | --------- |
| 0.1.x                        | ✅ Yes     |
| Earlier development versions | ❌ No      |

Security fixes will generally target the latest supported release.

---

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

Public Issues are appropriate for normal bugs and feature requests, but security-sensitive information should remain private until the issue has been investigated and, when necessary, fixed.

### Preferred Reporting Method

Use **GitHub Private Vulnerability Reporting** when it is available for this repository.

Navigate to the repository's **Security** area and choose the option to privately report a vulnerability.

Please include as much of the following information as possible:

* A clear description of the vulnerability
* Affected toolkit version or commit
* Affected component
* Steps required to reproduce the issue
* Minimal proof-of-concept code when appropriate
* Expected security impact
* Operating system
* Python version
* Suggested mitigation, if known

Do not include unrelated private information.

---

## Sensitive Information

Please never publish any of the following in public Issues, Discussions, pull requests, examples, logs, or screenshots:

* API keys
* Access tokens
* Passwords
* Private credentials
* Authentication cookies
* Private repository credentials
* Personal access tokens
* Environment files containing secrets
* Other sensitive production information

If sensitive credentials are accidentally exposed, revoke or rotate them immediately through the relevant service.

---

## What May Qualify as a Security Issue

Examples may include:

* Unsafe handling of credentials
* Unexpected disclosure of sensitive information
* Path traversal or unsafe file-writing behavior
* Dependency-related vulnerabilities
* Injection vulnerabilities
* Unsafe parsing of untrusted project data
* Security problems in future command-line or platform integrations

Ordinary validation errors, incorrect cinematic output, continuity mismatches, prompt-generation behavior, and documentation problems should normally be reported using the standard **Bug Report** Issue Form.

---

## Responsible Disclosure

Please allow reasonable time for investigation and remediation before publicly sharing technical details about a confirmed vulnerability.

Maintainers may:

1. Confirm receipt of the report
2. Request additional reproduction information
3. Evaluate severity and affected versions
4. Develop and test a fix
5. Prepare a security release when required
6. Coordinate public disclosure when appropriate

---

## Security Scope

The toolkit currently focuses on local Python-based cinematic workflow processing.

Third-party AI platforms, APIs, operating systems, package registries, and external services are outside the direct security scope of this repository unless a vulnerability is caused by code maintained within this project.

Platform-specific integrations added in the future may introduce additional security considerations and should be evaluated independently.

---

## Dependency Security

Contributors should avoid introducing unnecessary dependencies.

New dependencies should have a clear project purpose and should be reviewed before becoming part of the core toolkit.

Security-related dependency updates may be released outside the normal feature roadmap when necessary.

---

## Good-Faith Research

Good-faith security research and responsible disclosure are appreciated.

Please avoid:

* Accessing data that does not belong to you
* Disrupting services
* Destructive testing
* Publishing sensitive vulnerability details before remediation
* Using discovered vulnerabilities for unauthorized access

---

## Policy Updates

This security policy may evolve as the toolkit gains additional features, external integrations, command-line tooling, or network-connected functionality.

The latest version of this file represents the current project security policy.
