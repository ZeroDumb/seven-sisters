# Alice's Adventure Guide 🎩

## Overview
Alice is the reconnaissance specialist of the Seven Sisters, equipped with tools for discovering and analyzing digital footprints. Her tools are designed for ethical security research and authorized penetration testing.

## Tools & Capabilities

### 1. Wayback Machine Explorer (waybackurls)
**Purpose**: Historical URL Discovery
- Queries the Internet Archive's Wayback Machine
- Discovers historical endpoints and URLs
- Maps the evolution of web applications
- Identifies deprecated but potentially still accessible endpoints

**Ethical Usage**:
- Only use on authorized targets
- Respect robots.txt and rate limits
- Do not use for scraping or archiving without permission
- Use findings to improve security, not exploit

### 2. URL Discovery (gau)
**Purpose**: Comprehensive URL Mapping
- Aggregates URLs from multiple sources:
  - AlienVault's Open Threat Exchange
  - Wayback Machine
  - CommonCrawl
- Creates a comprehensive map of known endpoints
- Identifies potentially sensitive paths

**Ethical Usage**:
- Use only for authorized security research
- Respect rate limits and terms of service
- Report findings responsibly
- Do not use for unauthorized data collection

### 3. Directory Scanner (dirsearch)
**Purpose**: Web Path Discovery
- Scans for hidden directories and files
- Focuses on common web technologies (PHP, HTML, JS)
- Identifies potentially sensitive endpoints
- Maps application structure

**Ethical Usage**:
- Only scan authorized targets
- Use appropriate scan speeds to avoid disruption
- Report findings through proper channels
- Do not attempt to access sensitive data

### 4. GitHub Intelligence (github-dorker)
**Purpose**: Code Repository Analysis
- Searches GitHub for potentially sensitive information
- Requires GitHub API token
- Identifies exposed credentials, API keys, and sensitive data
- Maps codebase structure and dependencies

**Ethical Usage**:
- Only search public repositories
- Respect GitHub's terms of service
- Report security issues responsibly
- Do not use for unauthorized data collection

## Best Practices

1. **Authorization**
   - Always ensure proper authorization before scanning
   - Document all permissions and scope
   - Respect boundaries and limitations

2. **Rate Limiting**
   - Implement appropriate delays between requests
   - Respect API rate limits
   - Use tools responsibly to avoid service disruption

3. **Data Handling**
   - Securely store and handle discovered information
   - Follow data protection regulations
   - Properly dispose of sensitive data

4. **Reporting**
   - Document all findings thoroughly
   - Report issues through proper channels
   - Follow responsible disclosure practices

## Tool Configuration

### Required Environment Variables
- `GITHUB_TOKEN`: GitHub API token for github-dorker
- Additional tokens may be required for other tools

### Output Files
- `urls_wayback.txt`: Combined results from waybackurls and gau
- `dir_output.txt`: Directory scanning results
- Additional output files may be generated by other tools

## Ethical Guidelines

1. **Do No Harm**
   - Avoid disrupting services
   - Respect privacy and confidentiality
   - Use tools for security improvement only

2. **Transparency**
   - Document all activities
   - Maintain clear communication
   - Follow established protocols

3. **Responsibility**
   - Report findings promptly
   - Follow up on security issues
   - Maintain professional standards

## Support and Resources

For additional guidance or support:
- Consult Seven for authorization
- Review tool documentation
- Follow security best practices
- Maintain proper communication channels

Remember: With great power comes great responsibility. Use these tools wisely and ethically. 🎩✨ 