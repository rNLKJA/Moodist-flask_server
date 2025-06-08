"""Index controller."""

from flask import jsonify

def index():
    """Home page controller."""
    return jsonify({
        "message": "Welcome to Moodist - Track Your Mood, Improve Your Mental Health!",
        "creator": "rNLKJA",
        "description": "A mood tracking application for psychiatry studies - The University of Melbourne @2025"
    }) 