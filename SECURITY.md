# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of AI-Financial-Agent seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** open a public issue
2. Email security concerns to: **21407alfredmunga@gmail.com** (or repository owner)
3. Include detailed information:
   - Type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: 
  - Critical vulnerabilities: 24-72 hours
  - High severity: 7-14 days
  - Medium severity: 30 days
  - Low severity: 90 days

### What to Expect

- Acknowledgment of your report
- Regular updates on the fix progress
- Credit in the security advisory (if desired)
- Coordination on public disclosure timing

## Security Measures

### Authentication & Authorization

#### Current Implementation
- ✅ JWT-based authentication with access and refresh tokens
- ✅ Bcrypt password hashing (12 rounds)
- ✅ Role-based access control (RBAC)
- ✅ Failed login attempt tracking
- ✅ Account lockout after 5 failed attempts
- ✅ Session management with token expiration
- ✅ Audit logging for authentication events

#### Best Practices
- Change default credentials immediately after installation
- Use strong passwords (minimum 8 characters, uppercase, lowercase, digits, special characters)
- Rotate JWT secrets regularly
- Review user permissions quarterly
- Enable multi-factor authentication (roadmap item)

### Data Protection

#### Sensitive Data Handling
- 🔒 **Never commit** `.env` files or credentials to git
- 🔒 All sensitive environment variables in `.env` file
- 🔒 MongoDB connection strings encrypted in transit (TLS/SSL)
- 🔒 API keys for external services (Gemini, MailerSend) stored securely
- 🔒 Customer financial data encrypted at rest (MongoDB encryption)

#### Current Protections
```bash
# Already in .gitignore
.env
.env.local
.env.*.local
*.key
*.pem
credentials.json
secrets/
```

### API Security

#### Implemented Protections
- ✅ CORS configuration for frontend domains
- ✅ Rate limiting on sensitive endpoints (roadmap)
- ✅ Input validation with Pydantic models
- ✅ SQL injection prevention (NoSQL, but input sanitized)
- ✅ XSS prevention in frontend (React escaping)
- ✅ CSRF protection for state-changing operations

#### Headers
```python
# Security headers (recommended to add)
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

### Database Security

#### MongoDB Security Checklist
- ✅ Authentication enabled (MongoDB Atlas)
- ✅ Network access restricted (IP whitelist)
- ✅ Connection over TLS/SSL
- ✅ Audit logging enabled
- ⚠️ Database-level encryption (Atlas default)
- ⚠️ Field-level encryption for PII (recommended)
- ⚠️ Regular backups (Atlas automated)

#### Collection-Level Security
- Users: Passwords hashed with bcrypt
- Audit logs: Immutable, append-only
- Financial data: Access controlled by user roles

### Third-Party Dependencies

#### Regular Updates
```bash
# Check for vulnerabilities
pip audit  # Python dependencies
npm audit  # Node.js dependencies

# Update dependencies
pip install --upgrade -r requirements.txt
npm update
```

#### Known Vulnerabilities
- Monitor GitHub Security Advisories
- Subscribe to security mailing lists
- Use Dependabot or similar tools

### Infrastructure Security

#### Production Deployment
```yaml
Recommended Security Measures:
- Deploy behind reverse proxy (nginx/Apache)
- Use firewall (UFW, iptables)
- Enable HTTPS/TLS (Let's Encrypt)
- Regular OS security updates
- Intrusion detection system (fail2ban)
- Log monitoring and alerting
- Container security scanning (if using Docker)
```

#### Environment Variables
```bash
# CRITICAL: Never expose these
JWT_SECRET_KEY=<random-256-bit-key>
MONGO_URI=<mongodb-connection-string>
GEMINI_API_KEY=<google-gemini-key>
MAILERSEND_API_KEY=<mailersend-key>

# Generate secure secrets:
python -c "import secrets; print(secrets.token_hex(32))"
```

### File Upload Security

#### Current Implementation
- Receipt/Invoice uploads stored in `/storage` directory
- File type validation (PDF, images)
- File size limits enforced
- Virus scanning (recommended to add)

#### Recommendations
```python
# Add to upload handler
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Validate file type by content, not extension
import magic
mime = magic.from_buffer(file_content, mime=True)
```

### Payment Gateway Security

#### M-Pesa Integration
- ✅ API credentials stored in environment variables
- ✅ HTTPS for all payment communications
- ✅ Transaction verification before processing
- ✅ Webhook signature validation
- ⚠️ PCI DSS compliance (if storing card data - NOT recommended)

### Logging & Monitoring

#### Security Events Logged
- Authentication attempts (success/failure)
- Authorization failures
- Password changes
- User creation/deletion
- Sensitive data access
- API rate limit violations

#### Log Protection
```python
# Logs stored in /logs directory
- Rotate logs daily
- Retain for 90 days minimum
- Restrict access (chmod 600)
- Encrypt sensitive log data
- Monitor for suspicious patterns
```

### Vulnerability Disclosure

#### Security Vulnerabilities Patched
- **2025-10**: Fixed hardcoded credentials in test files
- **2025-10**: Implemented proper .gitignore for sensitive files
- **2025-10**: Added audit logging for authentication events

## Security Checklist for Deployment

### Pre-Production
- [ ] Change all default credentials
- [ ] Rotate all API keys and secrets
- [ ] Review and restrict user permissions
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Review .env file (never commit)
- [ ] Enable database backups
- [ ] Configure CORS properly
- [ ] Set secure cookie flags

### Production
- [ ] Use environment-specific configurations
- [ ] Enable rate limiting
- [ ] Set up WAF (Web Application Firewall)
- [ ] Configure DDoS protection
- [ ] Enable security headers
- [ ] Set up intrusion detection
- [ ] Configure log aggregation
- [ ] Implement alerting for anomalies
- [ ] Regular security audits
- [ ] Penetration testing annually

## Compliance

### Data Protection
- **GDPR**: User data rights, data portability, right to deletion
- **Kenya Data Protection Act**: Local data protection requirements
- **PCI DSS**: If handling credit card data (use payment processors instead)

### Financial Regulations
- Maintain audit trails for 7 years
- Ensure transaction integrity
- Implement proper access controls
- Regular compliance audits

## Security Contacts

### Reporting
- **Email**: security@finguard.com
- **GPG Key**: (Add public key for encrypted communication)
- **Bug Bounty**: (If applicable)

### Emergency Response
- **On-Call**: (24/7 contact for critical vulnerabilities)
- **Incident Response Team**: (List team members and roles)

## Security Resources

### Internal
- [Development Security Guidelines](./docs/security-guidelines.md)
- [API Security Best Practices](./docs/api-security.md)
- [Incident Response Plan](./docs/incident-response.md)

### External
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls/)

## Acknowledgments

We appreciate the security research community and acknowledge responsible disclosure. Contributors who report valid security issues will be credited in our security advisories.

### Hall of Fame
(Security researchers who have helped improve our security will be listed here with their permission)

---

**Last Updated**: October 30, 2025  
**Next Review**: January 30, 2026  
**Version**: 1.0.0
