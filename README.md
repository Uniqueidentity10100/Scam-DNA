# SCAM DNA

**Tagline:** Decode the genetic code of scams and stop them before they evolve.

## Overview

SCAM DNA is a cybersecurity research platform that analyzes scam messages by identifying their underlying patterns — emotional triggers, structural markers, and linguistic tactics. By treating scam messages like organisms with "genetic codes," the system tracks how scam campaigns mutate over time, clusters them into families, and predicts future evolution patterns.

This tool is designed for researchers, educators, and security professionals who want to understand how scam tactics adapt and spread.

## Key Features

### 1. Scam DNA Encoder
- Analyzes text to extract emotional manipulation patterns (urgency, fear, reward, authority, trust)
- Identifies structural markers (links, payment requests, identity theft attempts, contact switching)
- Detects linguistic patterns (excessive capitalization, poor grammar, generic greetings)
- Generates unique DNA codes like `URG-FEAR-AUTH-LNK-PAY`

### 2. Similarity & Mutation Engine
- Uses sentence embeddings (Sentence-BERT) to compare messages semantically
- Automatically clusters related scams into families
- Calculates mutation scores showing how much a scam has evolved from its parent
- Classifies mutations as: Original, Minor Mutation, or Major Mutation

### 3. Evolution Timeline
- Visual timeline showing when scam messages were detected
- Tracks DNA code changes within families over time
- Displays mutation progression and pattern shifts

### 4. Family Analysis
- Groups related scams into named families
- Tracks member count and mutation velocity
- Shows dominant patterns within each family

### 5. Threat Prediction
- Analyzes mutation trends across families
- Generates defensive predictions about future scam evolution
- Provides educational recommendations for protection

## Architecture

```
scam_dna/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── data/                      # SQLite database storage
│   └── scam_dna.db           # (auto-generated)
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/               # Data models
│   │   ├── database.py       # Database schema and connections
│   │   └── message.py        # Message data model
│   ├── services/             # Business logic
│   │   ├── dna_encoder.py    # Pattern extraction engine
│   │   ├── similarity_engine.py  # Semantic comparison
│   │   ├── analysis_service.py   # Main analysis coordinator
│   │   └── prediction_service.py # Insights and predictions
│   ├── routes/               # HTTP endpoints
│   │   ├── main_routes.py    # Page routes
│   │   └── api_routes.py     # AJAX API endpoints
│   ├── templates/            # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── analyzer.html
│   │   ├── timeline.html
│   │   ├── families.html
│   │   ├── family_detail.html
│   │   └── insights.html
│   └── static/               # Frontend assets
│       ├── css/
│       │   └── style.css     # Professional dark theme
│       └── js/
│           ├── main.js       # Global utilities
│           └── analyzer.js   # Analysis page logic
```

## Technology Stack

- **Backend:** Python 3.8+, Flask
- **Database:** SQLite
- **NLP:** Sentence-Transformers (all-MiniLM-L6-v2)
- **Machine Learning:** scikit-learn for similarity calculations
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Visualization:** Built-in CSS charts (expandable to Plotly if needed)

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 2GB free disk space (for model downloads)

### Installation

1. **Clone or download the project**
   ```bash
   cd scam_dna
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Note: First run will download the sentence-transformer model (~80MB). This happens automatically.

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the platform**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage Guide

### Analyzing a Message

1. Navigate to the **Analyzer** page
2. Paste a suspected scam message (email, SMS, social media message)
3. Click **Analyze Message**
4. Review the extracted DNA code, category, and detected patterns
5. Check the family assignment and mutation status

### Viewing Timeline

The Timeline page shows all analyzed messages in chronological order, displaying:
- DNA codes and how they change
- Mutation classifications
- Emotional and structural patterns

### Exploring Families

The Families page groups related scams together:
- See how many messages belong to each family
- View average mutation scores
- Track first and last seen dates

### Getting Insights

The Insights page provides:
- Category distribution across all messages
- Most active scam families
- Mutation activity over time
- Defensive recommendations

## Example Scam Messages to Test

### Phishing Email
```
URGENT: Your account has been suspended due to unusual activity.
Click here to verify your identity within 24 hours or lose access permanently.
- PayPal Security Team
```

### Financial Fraud
```
Congratulations! You've won $50,000 in the Amazon Customer Lottery!
To claim your prize, send $500 processing fee via Western Union.
Reply with your bank details to claim now!
```

### Tech Support Scam
```
WARNING: Your computer is infected with 5 viruses!
Call Microsoft Support immediately at 1-800-XXX-XXXX
Do not turn off your computer. Technician standing by.
```

## Database Schema

### Messages Table
- Stores analyzed message content
- DNA code and category
- Emotional, structural, and linguistic signals
- Embedding vectors for similarity comparison
- Family assignment and mutation data

### Families Table
- Groups of related scam messages
- Primary DNA code signature
- Member count and activity tracking

### Mutations Table
- Parent-child relationships between messages
- Mutation scores and changed elements
- Timeline of evolution events

## Ethical Use Statement

**IMPORTANT:** This system is designed exclusively for educational and research purposes.

### Intended Use
- Understanding scam tactics for defensive purposes
- Training security awareness programs
- Academic research on social engineering
- Building better detection systems

### Prohibited Use
- Creating or distributing actual scams
- Generating malicious content
- Exploiting vulnerabilities in real systems
- Any illegal or harmful activities

The predictions generated by this system are meant to help people recognize and defend against scams, not to improve scam effectiveness.

## Future Improvements

### Near-term
- [ ] Export analysis reports as PDF
- [ ] Add more scam categories (romance, job, crypto)
- [ ] Implement real-time alerts for new family emergence
- [ ] Add visualization with Plotly for mutation graphs

### Long-term
- [ ] Multi-language support for international scams
- [ ] Integration with email clients as a plugin
- [ ] Collaborative database across research institutions
- [ ] Machine learning for automatic category classification
- [ ] API for external security tools

## Technical Notes

### Performance
- First analysis takes ~2-3 seconds (model loading)
- Subsequent analyses: <1 second
- Database queries optimized with indexes
- Suitable for datasets up to 100,000 messages

### Limitations
- Semantic analysis requires internet connection on first run (model download)
- Works best with English text (current model)
- Mutation detection accuracy improves with more data

## Contributing

This is a hackathon research project. Contributions welcome:
- Report bugs or suggest features via issues
- Submit pull requests for improvements
- Share interesting scam patterns for analysis

## Team

Built by a student cybersecurity research team for educational purposes.

## License

This project is provided as-is for educational use. See LICENSE file for details.

## Disclaimer

This tool analyzes text patterns and does not guarantee detection of all scams. Always verify unexpected messages through official channels. The developers are not responsible for any misuse of this software.

---

**Remember:** If something feels wrong, it probably is. When in doubt, verify through official channels.
