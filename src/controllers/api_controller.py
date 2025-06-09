"""API controller."""

from flask import jsonify

def status():
    """API status controller."""
    return jsonify({
        "status": "running",
        "service": "Moodist"
    })

def info():
    """API info controller."""
    return jsonify({
        "name": "Moodist API",
        "creator": "rNLKJA @ The University of Melbourne",
        "organization": "The University of Melbourne",
        "year": "2025",
        "email": "huang@rin.contact; rinh@unimelb.edu.au",
        "version": "1.7.2",
        "description": "A mood tracking application for psychiatry studies, helping you track your emotional ups and downs... because even your feelings deserve version control!"
    }) 