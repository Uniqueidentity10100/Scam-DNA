#!/usr/bin/env python3
"""
SCAM DNA - Launcher Script
Sets environment variables to disable TensorFlow before importing modules
"""

import os
import sys

# Disable TensorFlow in transformers library - MUST be set before importing transformers
os.environ['USE_TF'] = '0'
os.environ['USE_TORCH'] = '1'
os.environ['TRANSFORMERS_NO_TF'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import and run main
if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Now import and create the app
    from app import create_app
    
    # Initialize the Flask application
    app = create_app()
    
    print("\n" + "="*60)
    print("SCAM DNA - Cybersecurity Research Platform")
    print("="*60)
    print("\n🧬 Decoding the genetic code of scams...")
    print("\n📊 Application running at:")
    print("   http://127.0.0.1:5001")
    print("\n🔬 Features:")
    print("   • DNA Pattern Encoder")
    print("   • Similarity Analysis Engine")
    print("   • Family Clustering")
    print("   • Evolution Timeline")
    print("   • Predictive Insights")
    print("\n⚠️  Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5001)
