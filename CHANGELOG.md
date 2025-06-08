# Changelog

All notable changes to this project will be documented in this file.

## [0.3.1] - 2024-10-23

### Changed
- Updated SSL certificates to include "rNLKJA" in email addresses
- Updated verification script to validate the new certificates
- Fixed port configuration issue in the development server

## [0.3.0] - 2024-10-23

### Changed
- Renamed application to "Moodist" - A mood tracking application for psychiatry studies
- Added application creator and description
- Implemented robust SSL/TLS configuration with proper certificate generation
- Added SSL middleware for HTTP to HTTPS redirection
- Implemented security headers (HSTS, CSP, X-Content-Type-Options, X-Frame-Options)
- Added scripts for certificate generation and verification

## [0.2.1] - 2024-10-23

### Changed
- Changed default port from 5000 to 5001 to avoid conflict with macOS AirPlay Receiver

## [0.2.0] - 2024-10-23

### Changed
- Restructured project to follow Express.js-like organization
- Moved code to `src` directory with clear separation of concerns
- Implemented controller-based architecture
- Added middleware support
- Created utility functions for logging
- Improved error handling
- Added CHANGELOG.md to track project changes

## [0.1.0] - 2024-10-23

### Added
- Initial Flask server setup with virtual environment
- HTTPS support for development using self-signed certificates
- Basic API endpoints
- Configuration system for different environments
- Environment variable loading from .env file
- Documentation in README.md
- Project structure with blueprints 